from __future__ import annotations
from typing import TYPE_CHECKING,  Any, Iterator
if TYPE_CHECKING:
    from integration_platform.pipelines import HubspotSnapshot, HubSpotProperties, HubspotContacts, HubspotCompanyRevenue, HubspotPropertyUpdate, HubspotLeadsToDbc
from integration_platform.config.settings import HUBSPOT
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
import requests
import logging
import time


class HubSpotAPI:
    def __init__(self, pipeline: HubspotSnapshot | HubSpotProperties | HubspotContacts | HubspotCompanyRevenue | HubspotPropertyUpdate | HubspotLeadsToDbc | str):
        self.pipeline = pipeline
        if type(pipeline) == str:
            self.logger = logging.getLogger(f'{pipeline}.HubSpotAPI')
        else:
            self.logger = logging.getLogger(f'{pipeline.pipeline_name}.HubSpotAPI') #type: ignore
        self.base_url = 'https://api.hubapi.com'
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {HUBSPOT["access_token"]}',
            'Content-Type': 'application/json',
        })
        self.calls = 0
        self.lists = f'/crm/v3/lists'
        self.contact_property_str = 'firstname,lastname,lead_source,email,phone,emailaddress,keycode,product,adddate,createdate,notes_last_updated,hubspot_owner_id,call_summary,hs_lead_status,hs_marketable_status,lead_source_date,intents_during_call,toll_free__,bps,unitsperorder,totalorders,revenueperorder,totalunits,revenue,last_five9_call_disposition,last_five9_call_at,acumatica_product_list,who_is_the_chair_for,notes_last_contacted,notes_next_activity_date,num_contacted_notes,hs_analytics_source,hs_latest_source,date_and_time_added_to_outbound_list,lead_grade,date_added_to_outbound_list,budget_range,created_on_weekend,kustomer_id,sold,date_became_the_warm_lead'
        self.prefix = ''


        if type(pipeline).__name__ == 'hubspot-snapshot':
            self._get_deal_pipelines_()
            self._get_owners_()
            self._set_snapshot_windows_()

    #region _request_
    def _request_(self, method: str, path: str, **kwargs) -> dict[str, Any]:
        '''`_request_`(self, method: *str*, path: *str*, )
        ---
        <hr>
        
        Method that actually hits the HubSpot api with the method and args passed
        
        ### Downstream Calls 
         #### :meth:`~folder.file.class.method`
            - Description
        
        ### Upstream Calls 
         #### :meth:`~_get_owners_`
            - Gets distinct owners
         #### :meth:`~_get_deal_pipelines_`
            - Get each different deal pipeline
         #### :meth:`~get_properties`
            - Get all distinct properties
         #### :meth:`~search`
            - Search for the entity specified in the parameters passed
            
        <hr>
        
        Parameters
        ---
        :param (*str*) `method`: API Method to perform
        :param (*str*) `path`: API endpoint
        
        <hr>
        
        Returns
        ---
        :return `response` (dict[str, Any]): Response from HubSpot API
        '''
        url = f'{self.base_url}{path}'
        backoff = [1, 2, 4, 8, 16]
        last_status: int | None = None
        for attempt in range(5):
            self.logger.info(f'{self.prefix}Sending {method} request to {path}')
            response = self.session.request(method, url, timeout=30, **kwargs)
            self.calls += 1
            last_status = response.status_code
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 10))
                self.logger.warning(
                    f'{self.prefix}[RATE]  429 on {method} {path}; sleeping {retry_after}s '
                    f'(attempt {attempt + 1}/5).'
                )
                time.sleep(retry_after)
                continue
            if 500 <= response.status_code < 600:
                delay = backoff[attempt]
                self.logger.warning(
                    f'{self.prefix}[5XX]   {response.status_code} on {method} {path}; '
                    f'sleeping {delay}s (attempt {attempt + 1}/5).'
                )
                time.sleep(delay)
                continue
            response.raise_for_status()
            jresponse = response.json()
            self.logger.info(f'{self.prefix}Successfully parsed response from {path}')
            return jresponse
        self.logger.error(f'{self.prefix}Error! {method} request to {path} failed after five retries...{last_status}')
        return {}
    #endregion


    #region Methods in development
    def get_list_with_membership_contact_details(self, list_id: int, limit: int=250):
        ''':class:`~HubSpotAPI`.:meth:`~get_list_with_membership_contact_details` (self, list_id: *int*, limit: *int = 250* ):
        ---
        <hr>
        
        Given a ListID, get list data, membership and contact details for each member
        
        ### Downstream Calls 
         #### :class:`~HubSpotAPI`.:meth:`~get_list_with_membership`
            - Gets List data and membership(rows)
         #### :class:`~HubSpotAPI`.:meth:`~get_contact_by_id`
            - For each row in our list, we pass its ContactID and retrieve contact details from Hubspot
        
        ### Upstream Calls 
         #### :class:`~folder.file.class`.:meth:`~folder.file.class.method`
            
        <hr>
        
        Parameters
        ---
        :param (*int*) `list_id`: HubSpotID of list
        
        <hr>
        
        Returns
        ---
        :return `list_data` (*dict*): List data with membership and contact details
        '''
        list_data = self.get_list_with_membership(list_id, limit=limit)
        list_members = list_data['rows']
        rowlen = len(list_members)
        detailed_rows = []
        extracted_timestamp = datetime.now(ZoneInfo('America/New_York'))
        for i, (contact, data) in enumerate(list_members.items()):
            self.prefix = f'{list_data['name']}, {i+1}/{rowlen}: '
            self.logger.info(f'{self.prefix}Retrieving contact details for {contact}')
            contact_details = self.get_contact_by_id(contact_id=contact, properties=self.contact_property_str)
            data = {**contact_details, 'membershipTimestamp': data['membershipTimestamp']}
            detailed_rows.append(data)
        list_data['detailed_rows'] = detailed_rows
        list_data['timestamp_extract'] = extracted_timestamp
        self.logger.info(f'{list_data['name']} parsed successfully, {len(list_data['detailed_rows'])} rows returned')
        return list_data
    

    def get_list_with_membership(self, list_id: int, limit: int = 250):
        ''':class:`~HubSpotAPI`.:meth:`~get_list_with_membership` (self, list_id: *int*, limit: *int = 250*):
        ---
        <hr>
        
        Given a list id, get that list's details and membership(rows)
        
        ### Downstream Calls 
         #### :class:`~HubSpotAPI`.:meth:`~_request_`
            - Sends API call
        
        ### Upstream Calls 
         #### :class:`~HubSpotAPI`.:meth:`~get_list_with_membership_contact_details`
            
        <hr>
        
        Parameters
        ---
        :param (*int*) `list_id`: HubSpotID of list
        
        <hr>
        
        Returns
        ---
        :return `list_data` (*dict*): Dict of data regarding Hubspot List, including membership of list
        '''
        self.logger.info(f"{self.prefix}Retrieving list {list_id}'s information and members")
        list_information = self._request_('get', f'{self.lists}/{list_id}')
        self.logger.info(f'{self.prefix}List {list_id} resolved to {list_information['list']['name']}')
        path_to_row_data = f'{self.lists}/{list_id}/memberships?limit={limit}'
        after: str | None = None
        rows = {}
        while True:
            params: dict[str, Any] = {'limit': limit}
            if after:
                params['after'] = after
            data = self._request_('GET', path_to_row_data, params=params)
            for row in data.get('results', []):
                bp = 'here'
                if rows.get(row['recordId']) == None:
                    rows[row['recordId']] = row
            after = data.get('paging', {}).get('next', {}).get('after')
            if not after:
                break
        list_data = {
            **list_information['list'],
            'rows': rows 
        }
        self.logger.info(f'{list_data['name']} has {list_data['size']} rows')
        return list_data

    def get_contact_by_id(self, contact_id: int, properties: str = 'firstname,lastname,email,phone,name'):
        ''':class:`~HubSpotAPI`.:meth:`~get_contact_by_id` (self, contact_id: *int*, properties: *str = 'firstname,lastname,email,phone,name'*):
        ---
        <hr>
        
        Given a Hubspot ContactID, retrieve contact details, including the properties passed
        
        ### Downstream Calls 
         #### :class:`~HubSpotAPI`.:meth:`~_request_`
            - Sends API call
        
        ### Upstream Calls 
         #### :class:`~HubSpotAPI`.:meth:`~get_list_with_membership_contact_details`
            
        <hr>
        
        Parameters
        ---
        :param (*int*) `contact_id`: Hubspot ContactID
        
        <hr>
        
        Returns
        ---
        :return `contact_details` (*dict*): Response from HubSpot containing details corresponding to the passed contact_id value
        '''
        if properties != 'firstname,lastname,email,phone,name':
            properties = 'firstname,lastname,email,phone,name,' + properties
        contact_details = self._request_(method='GET', path=f'/crm/v3/objects/contacts/{contact_id}', params={'properties': properties})
        return contact_details


























    
    #region get_properties
    def get_properties(self, object_type: str, property_name: str = '') -> list[dict]:
        '''`_get_properties`(self, object_type: *str*)
        ---
        <hr>
        
        Method that drives the extraction of HubSpot properties from the **object_type** passed as a parameter
        
        ### Downstream Calls 
         #### :meth:`~_request_`
            - Method that hits the HubSpot API at the endpoint we pass
        
        ### Upstream Calls 
         #### :class:`~pipelines.hubspot_properties.HubSpotProperties`.:meth:`~pipelines.hubspot_properties.HubSpotProperties.extract`
            - Description
            
        <hr>
        
        Parameters
        ---
        :param (*str*) `object_type`: Hubspot Object Type to retrieve properties for (calls, contacts, emails, meetings, etc...)
        
        <hr>
        
        Returns
        ---
        :return `results` (list[dict]): list of properties belonging to the specified object_type
        '''
        data = self._request_('GET', f'/crm/v3/properties/{object_type}')
        results = data.get('results', [])
        if property_name != '':
            results = [r for r in results if r['name'] == property_name]
            return results
        for result in results:
            result['ObjectType'] = object_type
        # self.logger.info(f'')
        bp = 'here'
        return results
    #endregion


    
    #region search
    def search(self, object_type: str, filter_groups: list[dict], properties: list[str], query: str = '', limit: int = 100) -> Iterator[dict]:
        '''`search`(self, object_type: *str*, filter_groups: *list[dict]*, properties: *list[str]*, query *str = ''*, limit: *int = 100*)
        ---
        <hr>
        
        Method that orchestrates how the request payload to the HubSpot API is actually delivered
        
        ### Downstream Calls 
         #### :meth:`~_request_`
            - Method that goes out and hits the Hubspot API 
        
        ### Upstream Calls 
         #### :meth:`~search_deals`
            - Used to search deals
         #### :meth:`~search_activities`
            - Used to search calls, emails, meetings, tasks
         #### :meth:`~search_new_contacts`
            - Used to search for newly created contacts
            
        <hr>
        
        Parameters
        ---
        :param (*str*) `object_type`: Type of object that we are searching for (deals, calls, emails, meetings, etc)
        :param (*list[dict]*) `filter_groups`: How filtering of records should be performed
        :param (*list[str]*) `properties`: Additional properties that should be included in the response from API
        :param (*list[str]*) `query`: Value to search for in hubspot
        :param (*list[str]*) `limit`: Limit of records to return

        '''
        path = f'/crm/v3/objects/{object_type}/search'
        after: str | None = None
        total = 0
        results = []
        while True:
            body: dict[str, Any] = {
                'filterGroups': filter_groups,
                'properties': properties,
                'limit': limit,
            }
            if query != '':
                body['query'] = query
            if after:
                body['after'] = after
            data = self._request_('POST', path, json=body)
            full_total = data['total']
            if total == 0:
                self.logger.info(f'{full_total} records found')
            for record in data.get('results', []):
                yield record
                results.append(record)
                total += 1                
                if full_total and total % max(1, full_total // 10) == 0:
                    self.logger.info(f'{total} records extracted')
            after = data.get('paging', {}).get('next', {}).get('after')
            if not after:
                break
            if total >= 10_000:
                # HubSpot /search caps at 10k results — caller must narrow the filter.
                self.logger.error(
                    f'[CAP]   /search on {object_type} reached 10k cap; '
                    f'narrow the date range and re-query. Stopping pagination.'
                )
                break
            bp = 'here'
        bp = 'here'


    #endregion
    
    #region search_deals
    def search_deals(self) -> list[dict]:
        '''`search_deals`()
        ---
        <hr>
        
        put_summary_here
        
        ### Downstream Calls 
         #### :meth:`~search`
            - Orechestrates how the deal search payload will be delivered to Hubspot API

        ### Upstream Calls 
         #### :class:`~pipelines.hubspot_snapshot.HubSpotSnapshot`.:meth:`~pipelines.hubspot_snapshot.HubSpotSnapshot.extract`
            - deals -> data_extract['deals'] in HubSpotSnapshot pipeline execution
        
        <hr>
        
        Returns
        ---
        :return `deals` (list[dict]): list of deals returned from Hubspot API
        '''
        now = datetime.now(timezone.utc)
        two_years_ago_ms = str(int((now - timedelta(days=730)).timestamp() * 1000))

        filter_groups = [
            {
                "filters": [
                    {"propertyName": "pipeline",   "operator": "EQ",     "value": self.b2b_pipeline['id']},
                    {"propertyName": "createdate", "operator": "GTE",    "value": two_years_ago_ms},
                    {"propertyName": "dealstage",  "operator": "NOT_IN", "values": [self.b2b_closed_won['id'], self.b2b_closed_lost['id']]},
                ]
            },
            {
                "filters": [
                    {"propertyName": "pipeline",   "operator": "EQ",  "value": self.b2b_pipeline['id']},
                    {"propertyName": "createdate", "operator": "GTE", "value": self.fiscal_year_start_ms},
                    {"propertyName": "dealstage",  "operator": "IN",  "values": [self.b2b_closed_won['id'], self.b2b_closed_lost['id']]},
                ]
            },
        ]

        properties = [
            "dealname", "dealstage", "dealtype", "hubspot_owner_id", "createdate",
            "product", "amount", "closedate", "hs_last_activity_date", "notes_last_updated",
            "hs_deal_is_stalled", "closed_lost_reason", "primary_competitor",
            "lead_source", "order_number", 'hs_lead_status', 'inbound_call_disposition'
        ]

        seen: set[str] = set()
        deals: list[dict] = []
        deal_result = self.search('deals', filter_groups=filter_groups, properties=properties)
        for deal in deal_result:
            if deal['id'] not in seen:
                seen.add(deal['id'])
                deals.append(deal)
        return deals


    #endregion
    
    #region search_activities
    def search_activities(self, object_type: str) -> list[dict]:
        '''`search_activities`(self, object_type: *str*)
        ---
        <hr>
        
        Method to search activities in hubspot for the ***object_type*** passed to the method
        
        ### Downstream Calls 
         #### :meth:`~search`
            - Method that actually performs the API call
            
        <hr>
        
        Parameters
        ---
        :param (*str*) `object_type`: _description_
        
        <hr>
        
        Returns
        ---
        :return `variablename` (list[dict]): Response from :meth:`~search` from the Hubspot API
        '''
        self.logger.info(f'Extracting {object_type}...')
        fiscal_year_start_ms = str(int(self.fiscal_year_start.timestamp() * 1000))
        filter_groups = [
            {"filters": [{"propertyName": "hs_timestamp", "operator": "GTE", "value": self.fiscal_year_start_ms}]}
        ]
        return list(self.search(object_type, filter_groups=filter_groups, properties=["hs_timestamp", "hubspot_owner_id"]))
    #endregion
    
    #region search_new_contacts
    def search_new_contacts(self, properties: list = ["createdate", "hubspot_owner_id"]) -> list[dict]:
        '''`search_new_contacts`(self)
        ---
        <hr>
        
        Method to search Contacts in HubSpot specifically 
            
        <hr>
        
        Returns
        ---
        :return `variablename` (list[dict]): Response from :meth:`~search` containing the contacts found with the Hubspot API
        '''
        fiscal_year_start_ms = str(int(self.fiscal_year_start.timestamp() * 1000))
        filter_groups = [
            {"filters": [{"propertyName": "createdate", "operator": "GTE", "value": self.fiscal_year_start_ms}]}
        ]
        results = list(self.search('contacts', filter_groups=filter_groups, properties=properties))
        return results
    #endregion
    
    #region search_contacts
    def search_contacts(self, filter_groups: list = [], properties: list = ["createdate", "hubspot_owner_id"]) -> list[dict]:
        '''`search_new_contacts`(self)
        ---
        <hr>
        
        Method to search Contacts in HubSpot specifically 
            
        <hr>
        
        Returns
        ---
        :return `variablename` (list[dict]): Response from :meth:`~search` containing the contacts found with the Hubspot API
        '''
        if filter_groups == []:
            filter_groups = [
                {"filters": [{"propertyName": "createdate", "operator": "GTE", "value": self.contact_searching}]}
            ]
        results = list(self.search('contacts', filter_groups=filter_groups, properties=properties))
        return results    
    #endregion

    
    #region search_by_phone
    def search_by_phone(self, phone_value: str, object_type: str = 'contacts', filter_groups: list = [], properties: list = ["createdate", "hubspot_owner_id", "email", "phone"]) -> list[dict]:
        '''`search_new_contacts`(self)
        ---
        <hr>
        
        Method to search Contacts in HubSpot specifically 
            
        <hr>
        
        Returns
        ---
        :return `variablename` (list[dict]): Response from :meth:`~search` containing the contacts found with the Hubspot API
        '''
        # if filter_groups == []:
        #     filter_groups = [
        #         {"filters": [{"propertyName": "createdate", "operator": "GTE", "value": self.contact_searching}]}
        #     ]
        results = list(self.search(object_type=object_type, filter_groups=filter_groups, properties=properties, query=phone_value))
        return results
    #endregion


    
    #region retrieve_companies    
    def retrieve_companies(self, limit: int = 100):
        ''':class:`~HubSpotAPI`.:meth:`~retrieve_companies` (self, limit: *int = 100*):
        ---
        <hr>
        
        Gets companies, contacts and contact information from Hubspot
        
        ### Downstream Calls 
         #### :class:`~HubSpotAPI`.:meth:`~get_company_primary_contact`
            - For each company, get all primary contacts. For each primary contact, lookup their contact information and return company data with contacts appended
            
        
        ### Upstream Calls 
         #### :class:`~integration_platform.pipelines.hubspot_company_revenue.HubspotCompanyRevenue`.:meth:`~integration_platform.pipelines.hubspot_company_revenue.HubspotCompanyRevenue.extract`
            - Called during data extraction in HubspotCompanyRevenue pipeline execution

        <hr>
        
        Returns
        ---
        :return `companies` (list[*dict*]): List of companies with contacts and contact information
        '''
        companies = []
        after: str | None = None
        while True:
            body: dict[str, Any] = {
                'properties': ['name', 'phone', 'email'],
                'limit': limit,
                'sorts': [{'propertyName': 'createdate', 'direction': 'DESCENDING'}],
                # 'sorts': [{'propertyName': 'hs_lastmodifieddate', 'direction': 'DESCENDING'}],
                'filterGroups': [],
            }
            if after:
                body['after'] = after
            self.logger.info(f'Retrieving companies...{self.calls} total hubspot api calls')
            data = self._request_('POST', '/crm/v3/objects/companies/search', json=body)
            last_extracted = datetime.now(ZoneInfo('America/New_York'))
            for company in data.get('results', []):
                name = company['properties']['name'].strip()
                self.prefix = f'{len(companies) + 1}, {name}: '
                self.logger.info(self.prefix)                
                company_id = company['id']
                if company_id in['9313832804', '7780863589']:
                    continue
                company = {
                    'id': company['id'],
                    'name': company['properties'].get('name'),
                    'phone': company['properties'].get('phone'),
                    'email': company['properties'].get('email'),
                    'create_date': company['createdAt'],
                    'update_data': company['updatedAt'],
                    'LastExtracted': last_extracted
                }
                company = self.get_company_primary_contact(company)
                companies.append(company)
            after = data.get('paging', {}).get('next', {}).get('after')
            if not after: #or len(companies) >= 10:
                break
        self.logger.info(f'{self.calls} total hubspot api calls')
        return companies
    #endregion
    

    #region get_company_primary_contact
    def get_company_primary_contact(self, company: dict) -> dict:
        ''':class:`~HubSpotAPI`.:meth:`~get_company_primary_contact` (self, company: *dict*):
        ---
        <hr>
        
        Given a company, finds all primary contacts. Then for each contact, retrieves contact details (name, phone, email, etc.)
        
        ### Downstream Calls 
         #### :class:`~HubSpotAPI`.:meth:`~_request_`
            - Hits the Hubspot API to get all primary contacts, then for each one, hits the Hubspot API again to get the contact's contact info
        
        ### Upstream Calls 
         #### :class:`~HubSpotAPI`.:meth:`~retrieve_companies`
            - Main entry point. Calls this method for each company
            
        <hr>
        
        Parameters
        ---
        :param (*dict*) `company`: dict of company data. Must contain ***id***
        
        <hr>
        
        Returns
        ---
        :return `company` (dict): returns dict that was passed, but with contact information added. *`company['contacts']`*
        '''
        contacts = []
        self.logger.info(f'{self.prefix}retrieving primary contact...')
        data = self._request_('GET', f'/crm/v4/objects/companies/{company['id']}/associations/contacts')
        results = data.get('results', [])
        primary_contacts = [result['toObjectId'] for result in results for assoc_type in result.get('associationTypes', []) if assoc_type.get('label') == 'Contact with Primary Company']
        count_contacts = len(primary_contacts)
        self.logger.info(f'{self.prefix}{len(primary_contacts)} primary contacts found')
        for i, contact_id in enumerate(primary_contacts): 
            self.logger.info(f'{self.prefix}{i+1}/{count_contacts}: found primary contact, retrieving details...')
            contact = self._request_('GET', f'/crm/v3/objects/contacts/{contact_id}', params={
                'properties': 'firstname,lastname,email,phone,name'
            })
            time.sleep(.05)
            name = f"{contact['properties'].get('firstname', '') or ''} {contact['properties'].get('lastname', '') or ''}".strip()
            company_addition = {
                'pc_id': contact['id'],
                'pc_phone': contact['properties'].get('phone'),
                'pc_email':contact['properties'].get('email'),
                'pc_fname': contact['properties'].get('firstname'),
                'pc_lname': contact['properties'].get('lastname'),
                'pc_name': name if name != '' else None,
                'pc_create_date': contact['createdAt'],
                'pc_update_date': contact['updatedAt']
            }
            contacts.append(company_addition)
            self.logger.info(f'{self.prefix}parsed primary contact successfully!')
            
        company = {
            **company,
            'contacts': contacts
        }
        return company
    #endregion
    
    #region update_company
    def update_company(self, company: dict, property_payload: dict):
        ''':class:`~HubSpotAPI`.:meth:`~update_company` (self, company: *dict*, property_payload: *dict*):
        ---
        <hr>
        
        Given a dict of company data and properties to update, update the specified properties for the passed company
        
        ### Upstream Calls 
         #### :class:`~integration_platform.transform.hubspot_company_revenue.HubspotCompanyRevenue`.:class:`~integration_platform.transform.hubspot_company_revenue.Transform`.:meth:`~integration_platform.transform.hubspot_company_revenue.Transform._update_payload`
            
        <hr>
        
        Parameters
        ---
        :param (*dict*) `company`: dict of company data. Must contain ***`id`*** and ***`name`***
        :param (*dict*) `property_payload`: properties and values to send to HubSpot
        
        <hr>
        
        Returns
        ---
        :return `variablename` (_type_): _description_
        '''
        path = f'/crm/v3/objects/companies/{company['id']}'
        url = f'{self.base_url}{path}'
        browser_link = f'https://app.hubspot.com/contacts/5053729/record/0-2/{company['id']}'
        try:
            response = self.session.patch(url=url,json=property_payload)
        except Exception as e:
            self.logger.error(f"Error! Failed to update {company['name']}. {e}\n{browser_link}")
            return
        try:
            jresponse = response.json()
        except Exception as e:
            self.logger.error(f"Error! Couldn't parse response from hubspot api when updating {company['name']}. {e}\n{browser_link}")
            return
        self.logger.info(f'contact updated. {browser_link}') #type: ignore
        company['LastUpdated'] = datetime.now(ZoneInfo('America/New_York'))
        time.sleep(1)
        bp = 'here'
        return company
    #endregion

    #region update_property_options
    def update_property_options(self, property: dict):
        ''':class:`~HubSpotAPI`.:meth:`~update_property_options` (self, property: *dict*):
        ---
        <hr>
        
        Given a property (Acumatica Items), update its dropdown options
        
        ### Upstream Calls 
         #### :class:`~integration_platform.pipelines.hubspot_property_update.HubspotPropertyUpdate`.:meth:`~integration_platform.pipelines.hubspot_property_update.HubspotPropertyUpdate.load`
            - Description
            
        <hr>
        
        Parameters
        ---
        :param (*dict*) `property`: dict of property data with all existing options and new options appended. New options will be updated following successful update
        
        <hr>
        
        Returns
        ---
        :return `jresponse` (dict): json formatted response from Hubspot API
        '''
        path = f'/crm/v3/properties/Contact/{property['name']}'
        url = f'{self.base_url}{path}'
        try:
            response = self.session.patch(url=url,json=property)
        except Exception as e:
            self.logger.error(f"Error! Failed to update {property['name']}. {e}")
            return
        try:
            jresponse = response.json()
        except Exception as e:
            self.logger.error(f"Error! Couldn't parse response from hubspot api when updating {property['name']}. {e}")
            return
        self.logger.info(f'{property['name']} updated successfully!') #type: ignore
        time.sleep(1)
        bp = 'here'
        return jresponse
    #endregion

    #TODO Pull in data on all the contacts
    #Track where they come from, attribute sales 
    #Here are the data points and how to structure 

    #Requirements around hubspot 



    #region HubspotCompanyRevenue
 
    #region _get_owners_
    def _get_owners_(self) -> dict[str, str]:
        '''`_get_owners_`(self)
        ---
        <hr>
        
        Method to retrieve Contact OwnerIDs from Hubspot API
        
        ### Downstream Calls 
            #### :meth:`~._request_`
            - Method that actually hits the HubSpot API with args passed from here
        
        ### Upstream Calls 
            #### :meth:`~folder.file.class.method`
            - Description
        
        <hr>
        
        Sets
        ---
        - #### self.:attr:`~owners`
        
        <hr>
        
        Returns
        ---
        :return `owners` (dict[str, str]): list of owners returned from HubSpot
        '''
        path = '/crm/v3/owners'
        after: str | None = None
        owners: dict[str, str] = {}
        while True:
            params: dict[str, Any] = {'limit': 100}
            if after:
                params['after'] = after
            data = self._request_('GET', path, params=params)
            for owner in data.get('results', []):
                name = f"{owner.get('firstName', '') or ''} {owner.get('lastName', '') or ''}".strip()
                owners[owner['id']] = name
            after = data.get('paging', {}).get('next', {}).get('after')
            if not after:
                break
        self.owners = owners
        return owners
    #endregion


    #region _get_deal_pipelines_
    def _get_deal_pipelines_(self) -> list[dict]:
        data = self._request_('GET', '/crm/v3/pipelines/deals')
        bp = 'here'
        results = data['results']
        self.b2b_pipeline = next((result for result in results if result['label'].lower() == 'b2b'), {})
        self.b2b_closed_won = next((stage for stage in self.b2b_pipeline['stages'] if stage['label'].lower() == 'closed/won'), {})
        self.b2b_closed_lost = next((stage for stage in self.b2b_pipeline['stages'] if stage['label'].lower() == 'closed/ lost'), {})
        
        self.ecom_pipeline = next((result for result in results if result['label'].lower() == 'ecommerce pipeline'), {})
        self.inbound_pipeline = next((result for result in results if result['label'].lower() == 'inbound sales'), {})
        self.outbound_pipeline = next((result for result in results if result['label'].lower() == 'outbound sales'), {})
        return data.get('results', [])
    #endregion

   
    #region _set_snapshot_windows_ 
    def _set_snapshot_windows_(self):
        '''`_set_snapshot_windows_`()
        ---
        <hr>
        
        Sets snapshot start windows for :class:`~pipelines.hubspot_snapshot.HubSpotSnapshot`
        
        ### Upstream Calls 
         #### :class:`~pipelines.hubspot_snapshot.HubSpotSnapshot`.:meth:`~pipelines.hubspot_snapshot.HubSpotSnapshot.__init__`
            - Called when :class:`~pipelines.hubspot_snapshot.HubSpotSnapshot` is initialized and sets snapshot windows
            
        <hr>
        
        Parameters
        ---
        
        <hr>
        
        Sets
        ---
        - #### self.:attr:`~fiscal_year_start`
        - #### self.:attr:`~week_start`
        - #### self.:attr:`~month_start`
        '''
        self.fiscal_year_start = datetime(year=datetime.now(ZoneInfo('America/New_York')).year, month=1, day=1)
        self.fiscal_year_start_ms = str(int(self.fiscal_year_start.timestamp() * 1000))
        self.week_start = datetime.now(ZoneInfo('America/New_York')).date() - timedelta(datetime.now(ZoneInfo('America/New_York')).date().weekday())
        self.month_start = datetime.now(ZoneInfo('America/New_York')).date() - timedelta(days=datetime.now(ZoneInfo('America/New_York')).date().day - 1)
        
        self.contact_searching = str(int((self.fiscal_year_start.timestamp() + 100000) * 1000))
    #endregion

    #endregion
