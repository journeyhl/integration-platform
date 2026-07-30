from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines import HubspotLeadsToDbc
import logging
import polars as pl
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

class Transform:
    def __init__(self, pipeline: HubspotLeadsToDbc):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.Transform')
        self.contact_prefix = ''
        pass

    def landing(self, data_extract: dict[str, dict]):
        db_rows = []
        nbr_of_lists_extracted = len(data_extract)
        for i, (list, list_data) in enumerate(data_extract.items()):
            self.list_prefix = f'{i+1}/{nbr_of_lists_extracted}'
            current_list_rows = len(list_data['detailed_rows'])
            self.db_row_constant = {
                'ListID': int(list_data['listId']),
                'ListName': list_data['name'],
                'ExtractDatetime': list_data['timestamp_extract']
            }
            for j, contact_details in enumerate(list_data['detailed_rows']):
                self.contact_prefix = f'{j+1}/{current_list_rows} ({self.list_prefix}): '
                db_row = self.format_db_row(contact_details)
                db_rows.append(db_row)
                bp = 'here'
        return db_rows
    

    def format_db_row(self, contact_details: dict):
        names = self._get_names_(contact_details=contact_details)
        properties: dict = contact_details['properties']
        db_row = {
            **self.db_row_constant,
            'ContactID': int(contact_details['id']),
            'FirstName': names['first'],
            'LastName': names['last'],
            'Name': names['name'],
            'Phone': properties.get('phone'),
            'PhoneFmt': self._parse_phone_(properties.get('phone')),
            'Email': self.pipeline.default_transformer.clean_string(properties.get('email')),
            'CreatedDatetime': self._parse_date_str_(contact_details.get('createdAt')),
            'UpdatedDatetime': self._parse_date_str_(contact_details.get('updatedAt')),
            'URL': contact_details.get('url'),
            'Product': properties.get('product'),
            'BPS': properties.get('bps'),
            'BudgetRange': properties.get('budget_range'),
            'CreatedOnWeekend': 1 if properties.get('created_on_weekend') == 'true' else 0 if properties.get('created_on_weekend') == 'false' else None,
            'AnalyticsSource': properties.get('hs_analytics_source'),
            'LatestSource': properties.get('hs_latest_source'),
            'LeadStatus': properties.get('hs_lead_status'),
            'IsMarketable': 1 if properties.get('hs_marketable_status') == 'true' else 0 if properties.get('hs_marketable_status') == 'false' else None,
            'KustomerID': self.pipeline.default_transformer.clean_string(properties.get('kustomer_id')),
            # 'LastFive9CallDatetime': self._parse_date_str_(properties.get('last_five9_call_at')),
            # 'LastFive9CallDisposition': properties.get('last_five9_call_disposition'),
            'LeadGrade': properties.get('lead_grade'),
            'LeadSource': properties.get('lead_source'),
            'Sold': properties.get('sold'),
            'CallIntent': properties.get('intents_during_call'),
            'NotesLastContacted': self._parse_date_str_(properties.get('notes_last_contacted')),
            'NotesLastUpdated': self._parse_date_str_(properties.get('notes_last_updated')),
            'TimesContacted': self._parse_str_to_int_(properties.get('num_contacted_notes')) ,
            'WarmLeadDatetime': self._parse_date_str_(properties.get('date_became_the_warm_lead')),
            'AddedToListDatetime': self._parse_date_str_(date_str=contact_details.get('membershipTimestamp')),
            'TollFree': contact_details['properties']['toll_free__'],
            'TollFreeFmt': self._parse_phone_(contact_details['properties']['toll_free__']),
            'Revenue': properties.get('revenue'),
            'TotalOrders': properties.get('totalorders'),
            'TotalUnits': properties.get('totalunits'),
            'RevenuePerOrder': properties.get('revenueperorder'),
            'UnitsPerOrder': properties.get('unitsperorder'),
        }
        
        if not isinstance(db_row['IsMarketable'], int) and db_row['IsMarketable'] != None: 
            bp = 'here'
        if not isinstance(db_row['CreatedOnWeekend'], int) and db_row['CreatedOnWeekend'] != None: 
            bp = 'here'

        return db_row

    def _get_names_(self, contact_details: dict) -> dict:
        first = contact_details['properties']['firstname'].strip() if contact_details['properties'].get('firstname') != None else ''
        last = contact_details['properties']['lastname'].strip() if contact_details['properties'].get('lastname') != None else ''
        name = f'{first} {last}'.strip()
        return {
            'first': first if first != '' else None,
            'last': last if last != '' else None,
            'name': name if name != '' else None,
        }

    def _parse_date_str_(self, date_str: str | None, format: str = '%Y-%m-%dT%H:%M:%S.%fZ'):
        if date_str == None or date_str == '':
            self.logger.info(f'Date string is blank')
            return None
        try:
            date = datetime.strptime(date_str, format)
        except ValueError as e:
            self.logger.warning(f"Couldn't parse date, trying backup format...")
            date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
            self.logger.info(f'Parsed date successfully!')
        return date

    def _parse_str_to_int_(self, int_str: str | None):
        if int_str == None or int_str.strip() == '':
            return None
        try:
            intint = int(int_str)
        except Exception as e:
            self.logger.error(f'Error while converting string to integer! {e}')
            intint = int_str
        return intint

    def _parse_phone_(self, phone_str: str | None):
        if phone_str == None or phone_str.strip() == '':
            return None
        phone_fmt = phone_str.replace('-', '').replace('(', '').replace(')', '').replace('+1', '').replace(' ', '').strip()
        if len(phone_fmt) != 10:
            self.logger.warning(f'Unconventional Phone number length!')
            if phone_fmt[0] == '+':
                phone_fmt = phone_fmt[-10:]
            else:
                return None
        return phone_fmt

#leadstatus
  #3285 -> HubSpotLeadsV2 (Clone - HubSpot Open Leads to Outbound(1715) -> CentralStore.HubSpotLeads)
    #firstname,lastname,lead_source,email,phone,emailaddress,keycode,product,adddate,createdate,notes_last_updated,hubspot_owner_id
  #Flip Lead Source(2484) -> CentralStore.LeadStatus
    #firstname,lastname,email,phone,emailaddress,keycode,product,adddate,createdate,notes_last_updated,hubspot_owner_id,call_summary,hs_lead_status,hs_marketable_status,lead_source,lead_source_date
  #Flip-Callback Leads(2382) -> CentralStore.FlipCallbackLeads
    #firstname,lastname,email,phone,emailaddress,keycode,product,adddate,createdate,notes_last_updated,hubspot_owner_id,call_summary
    
  #HubSpot After Hours Leads(2315) -> CentralStore.AfterHoursLeads
    #firstname,lastname,email,phone,emailaddress,keycode,product,adddate,createdate,notes_last_updated,hubspot_owner_id

  #HubSpot Open Leads to Outbound(1715) -> CentralStore.HubSpotLeads
    #firstname,lastname,email,phone,emailaddress,keycode,product,adddate,createdate,notes_last_updated,hubspot_owner_id

  #HubSpot Ready for Outbound(837) -> CentralStore.HubSpotLeads
    #firstname,lastname,email,phone,emailaddress,keycode,product,adddate,createdate,notes_last_updated,hubspot_owner_id

  #Lead Status For DB Integration(2476) -> CentralStore.LeadStatus
    #firstname,lastname,email,phone,emailaddress,keycode,product,adddate,createdate,notes_last_updated,hubspot_owner_id,call_summary,hs_lead_status,hs_marketable_status,lead_source,lead_source_date

