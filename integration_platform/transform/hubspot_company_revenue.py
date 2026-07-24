from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines import HubspotCompanyRevenue
import logging
import polars as pl
import json
class Transform:
    def __init__(self, pipeline: HubspotCompanyRevenue):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.Transform')
        self.prefix = ''
        self.distinct_company_contacts = {}
        self.sql_data_transformed = []
        self.unmatched_companies = []

        pass
    
    def transform(self, data_extract: dict):
        self.hubspot_extract = data_extract['hubspot_extract']
        self.revenue_extract = data_extract['revenue_extract']
        self.hs_total = len(self.hubspot_extract)
        data_transformed = self._main_iterator()
        return data_transformed


    def _main_iterator(self):
        for i, company in enumerate(self.hubspot_extract):
            self.prefix = f'{i+1}/{self.hs_total}, {company['name']}: '
            company['phone_match'] = False
            company['email_match'] = False
            phones = ([company['phone']] if company['phone'] != None else []) + [contact['pc_phone'] for contact in company['contacts'] if contact['pc_phone'] != None]
            emails = ([company['email']] if company['email'] != None else []) + [contact['pc_email'] for contact in company['contacts'] if contact['pc_email'] != None]
            phones = self._format_phones(phones)
            emails = self._format_emails(emails)
            self.logger.info(f'{self.prefix}{len(phones)} phones found, {len(emails)} emails found')
            company['phones'] = phones
            company['emails'] = emails
            
            contacts = [int(c['pc_id']) for c in company['contacts']]
            db_row = {
                'hsID': int(company['id']),
                'hsName': company['name'],
                'hsCompanyPhone': company['phone'],
                'hsCompanyEmail': company['email'],
                'hsContacts': json.dumps(contacts) if contacts != [] else None,
                'hsPhones': json.dumps(company['phones']) if company['phones'] != [] else None,
                'hsEmails': json.dumps(company['emails']) if company['emails'] != [] else None,
                'LastExtracted': company['LastExtracted']
            }
            company = self._find_matches(company)
            if len(company['distinct_matches']) == 0:
                self.logger.warning(f'{self.prefix}No matches found! Continuing...')
                company['LastUpdated'] = None
                self.unmatched_companies.append(db_row)
                continue
            else:
                company['CustomerIDs'] = [c['CustomerID'] for c in company['distinct_matches']]
                company = self._aggregate_matches(company)
                self.logger.info(f'Formatting and sending update payload via hubspot api...')
                company = self._update_payload(company)
                bp = 'here'
            company['CustomerIDs'] = [c['CustomerID'] for c in company['distinct_matches']]
            db_row = {
                **db_row,
                'acuCustomerIDs': json.dumps(company['CustomerIDs']),
                'acuCustomers': json.dumps(company['distinct_matches']),
                'phone_match': company['phone_match'],
                'email_match': company['email_match'],
                'LastUpdated': company['LastUpdated'] if company.get('LastUpdated') else None
            }
            self.sql_data_transformed.append(db_row)
            bp = 'here'
        data_transformed = {
            'acu_companies': self.sql_data_transformed,
            'unmatched_companies': self.unmatched_companies
        }
        return data_transformed



    def _find_matches(self, company: dict):
        '''`_find_matches`(self, company: *dict*, ):
        ---
        <hr>
        
        For each value found in the `company` dict's respective `phone` and `email` lists, check for that value in self.:attr:`~revenue_extract`
        
        ### Downstream Calls 
         #### :class:`~pipelines.hubspot_company_revenue.HubspotCompanyRevenue`.:class:`~Transform`.:meth:`~_format_dedupe_matches`
            - If we have 1 or more matches in self.:attr:`~revenue_extract`:
                - Iterate list and ensure no duplication
                - Change flag on `company['phone_match']` and `company['phone_match']` if needed
        
        ### Upstream Calls 
         #### :class:`~pipelines.hubspot_company_revenue.HubspotCompanyRevenue`.:class:`~Transform`.:meth:`~_main_iterator`
            - All rows or companies from hubspot_extract will flow through
            
        <hr>
        
        Parameters
        ---
        :param (*dict*) `company`: dict of company data containing `phones` and `emails`
        
        <hr>
        
        Returns
        ---
        :return `company` (_dict_): Updated company data, with `distinct_matches` appended
        '''
        company['distinct_matches'] = []
        for phone in company['phones']:
            bp = 'here'
            matches = [customer for customer in self.revenue_extract if phone in [customer['phone'], customer['phone2']]]
            if len(matches) == 0:
                continue
            company['phone_match'] = True
            company['distinct_matches'].extend(self._format_dedupe_matches(company=company, matches=matches))
            
        bp = 'here'
        for email in company['emails']:
            bp = 'here'
            matches = [customer for customer in self.revenue_extract if email == customer['email']]
            if len(matches) == 0:
                continue
            company['email_match'] = True
            company['distinct_matches'].extend(self._format_dedupe_matches(company=company, matches=matches))
        bp = 'here'
        return company


    def _format_dedupe_matches(self, company: dict, matches: list):
        '''`_format_dedupe_matches`(self, company: *dict*, matches: *list*):
        ---
        <hr>
        
        For each matching self.:attr:`~revenue_extract` record, iterate list to ensure no duplicate Acu Customers are added and return list of distinct matches (acu customers)
                
        ### Upstream Calls 
         #### :class:`~pipelines.hubspot_company_revenue.HubspotCompanyRevenue`.:class:`~Transform`.:meth:`~_find_matches`
            - If a match is found on phone or email, :meth:`~_format_dedupe_matches` is called
            
        <hr>
        
        Parameters
        ---
        :param (*dict*) `company`: dict of company data, must contain `'id'`
        :param (*list*) `matches`: list of matching dicts (rows) from self.:attr:`~revenue_extract`
        
        <hr>
        
        Returns
        ---
        :return `distinct_matches` (_list_): list of distinct, formatted matches from self.:attr:`~revenue_extract`
        '''
        bp = 'here'
        distinct_matches = []
        for i, match in enumerate(matches):
            if self.distinct_company_contacts.get((company['id'], match['CustomerID'])) == None:
                match['TotalRevenue'] = float(match['TotalRevenue'])
                self.distinct_company_contacts[(company['id'], match['CustomerID'])] = {'id': company['id'], **match}
                distinct_matches.append(match)
            else:
                self.logger.warning(f'{self.prefix}. Already matched!')
        
        bp = 'here'
        return distinct_matches
    



    def _aggregate_matches(self, company: dict):
        '''`_aggregate_matches`(self, company: *dict*):
        ---
        <hr>
        
        Given a dict of company data that contains the `distinct_matches` *list*, aggregates **revenue**, **orders**, and **units** from all matching Acumatica customers
        
        ### Upstream Calls 
         #### :class:`~pipelines.hubspot_company_revenue.HubspotCompanyRevenue`.:class:`~Transform`.:meth:`~_main_iterator`
            - Description
            
        <hr>
        
        Parameters
        ---
        :param (*dict*) `company`: dict of company data containing `distinct_matches` list, which holds dicts having **revenue**, **orders**, and **units** within each
        
        <hr>
        
        Returns
        ---
        :return `company` (_dict_): dict of company data with aggregated `revenue`, `orders`, `units`, `rev_per_order`, and `units_per_order` added
        '''
        revenue = 0
        orders = 0
        units = 0
        total_matches = len(company['distinct_matches'])
        for i, match in enumerate(company['distinct_matches']):
            self.logger.info(f'{self.prefix}. Aggregating {i+1}/{total_matches} matches')
            revenue += match['TotalRevenue']
            orders += match['Orders']
            units += match['Units']
        self.logger.info(f'{self.prefix}. ${revenue} in revenue. {units} units across {orders} orders')
        rev_per_order = round(float(revenue/orders), 2) if orders != 0 else 0
        units_per_order = round(float(units/orders), 2) if orders != 0 else 0
        company = {
            **company, 
            'revenue': float(revenue),
            'orders': orders,
            'units': units,
            'rev_per_order': rev_per_order,
            'units_per_order': units_per_order
        }
        bp = 'here'
        return company


    def _update_payload(self, company: dict):
        '''`_update_payload`(self, company: *dict*):
        ---
        <hr>
        
        Formats `properties` payload before sending to Hubspot for a Company update
        
        ### Downstream Calls 
         #### :class:`~connectors.hubspot_api.HubSpotAPI`.:meth:`~connectors.hubspot_api.HubSpotAPI.update_company`
            - Method in HubSpot connector that sends **PATCH** command to specified comapny (using id), updating properties with the payload formatted here
        
        ### Upstream Calls 
         #### :class:`~pipelines.hubspot_company_revenue.HubspotCompanyRevenue`.:class:`~Transform`.:meth:`~_main_iterator`
            
        <hr>
        
        Parameters
        ---
        :param (*dict*) `company`: dict of company data. Must contain **revenue**, **orders**, **units**, **rev_per_order**, **units_per_order** , and **CustomerIDs**
        
        <hr>
        
        Returns
        ---
        Nothing atm
        '''
        property_payload = {
            'properties':{
                'company_revenue': company['revenue'],
                'total_orders': company['orders'],
                'total_units': company['units'],
                'revenue_per_order': company['rev_per_order'],
                'units_per_order': company['units_per_order'],
                'acucustomers': ', '.join([c for c in company['CustomerIDs']])
            }
        }
        self.pipeline.hubspot.update_company(company=company, property_payload=property_payload)
        bp = 'here'
        return company


    def _format_phones(self, phones: list[str]):
        '''`_format_phones`(self, phones: *list[str]*):
        ---
        <hr>
        
        Normalizes and deduplicates list of phone number values pulled via Hubspot API
        - Removes ` `, `+1`, `(`, `)`, `-`, `.`, and `·`
            - ` ` = whitespace
        
        ### Upstream Calls 
         #### :class:`~pipelines.hubspot_company_revenue.HubspotCompanyRevenue`.:class:`~Transform`.:meth:`~_main_iterator`
            - All rows or companies from hubspot_extract will flow through 
        <hr>
        
        Parameters
        ---
        :param (**list[str]**) `phones`: list of phone numbers in string format
        
        <hr>
        
        Returns
        ---
        :return `phones` *(list[str])*: list of normalized phone numbers
        '''
        phone_dict = {
            phone.replace(' ', ''
                ).replace('+1' ,''
                ).replace('(' ,''
                ).replace(')' ,''
                ).replace('-' ,''
                ).replace('.' ,''
                ).replace('·' ,''
            ): phone
            for phone in phones
        }
        phones = [k for k, v in phone_dict.items()]
        bp = 'here'
        return phones

    def _format_emails(self, emails: list[str]):
        '''`_format_emails`(self, emails: *list[str]*):
        ---
        <hr>
        
        Normalizes and deduplicates list of email values pulled via Hubspot API
        - Removes whitespace and strips values
        
        ### Upstream Calls 
         #### :class:`~pipelines.hubspot_company_revenue.HubspotCompanyRevenue`.:class:`~Transform`.:meth:`~_main_iterator`
            - All rows or companies from hubspot_extract will flow through
            
        <hr>
        
        Parameters
        ---
        :param (**list[str]**) `emails`: list of emails in string format
        
        <hr>
        
        Returns
        ---
        :return `emails` *(list[str])*: list of normalized emails
        '''
        email_dict = {
            email.replace(' ', '').strip(): email
            for email in emails
        }
        emails = [k for k, v in email_dict.items()]
        return emails





    def _format_db_row_(self, company: dict):
        '''`_format_db_row_`(self, company: *dict*):
        ---
        <hr>
        
        Formats base dictionary for each row to be upserted to **hs.AcuCompanies** or **hs.Unmatched_Companies** in *db_CentralStore*
        
        ### Upstream Calls 
         #### :class:`~pipelines.hubspot_company_revenue.HubspotCompanyRevenue`.:class:`~Transform`.:meth:`~_main_iterator`
            - Formats base row structure for **hs.AcuCompanies** and **hs.Unmatched_Companies**
            - **hs.Unmatched_Companies** will show unchanged from the dictionary below, while **hs.AcuCompanies** will get more data appended later on
            - All rows or companies from hubspot_extract will flow through
            
        <hr>
        
        Parameters
        ---
        :param (*dict*) `company`: company data from hubspot. Must contain **id**, **name**, **phone**, **email**, **contacts**, **phones**, and **phone**
        
        <hr>
        
        Returns
        ---
        :return `db_row` (dict): row of data that can be upserted to either table in the load stage. If the company doesn't have a match to an Acu customer, this is our final row structure 
        '''
        return {
            'hsID': company['id'],
            'hsName': company['name'],
            'hsCompanyPhone': company['phone'],
            'hsCompanyEmail': company['email'],
            'hsContacts': [c['pc_id'] for c in company['contacts']],
            'hsPhones': company['phones'],
            'hsEmails': company['phone']            
        }