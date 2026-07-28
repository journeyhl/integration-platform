from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines import HubspotLeadsToDbc
import logging
import polars as pl
import json


class Transform:
    def __init__(self, pipeline: HubspotLeadsToDbc):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.Transform')
        self.contact_prefix = ''
        pass

    def landing(self, data_extract: dict[str, dict]):
        nbr_of_lists_extracted = len(data_extract)
        for i, (list, list_data) in enumerate(data_extract.items()):
            self.list_prefix = f'{i+1}/{nbr_of_lists_extracted}'
            current_list_rows = len(list_data['detailed_rows'])
            self.db_row_constant = {
                'ListName': list_data['name'],
                'ExtractDatetime': list_data['timestamp_extract']
            }
            for j, contact_details in enumerate(list_data['detailed_rows']):
                self.contact_prefix = f'{j+1}/{current_list_rows} ({self.list_prefix}): '
                db_row = self.format_db_row(contact_details)
                bp = 'here'

            bp = 'here'

        bp = 'here'


    def format_db_row(self, contact_details: dict):
        db_row = {
            **self.db_row_constant,
            'ID': contact_details['id'],
            'FirstName': contact_details['properties']['firstname'],
            'LastName': contact_details['properties']['lastname'],
            'Name': f'{contact_details['properties']['firstname'].strip()} {contact_details['properties']['lastname'].strip()}',
            'Phone': contact_details['properties']['phone'],
            'Ehone': contact_details['properties']['email'],
            'AddedToOutboundListDatetime': contact_details['properties']['date_and_time_added_to_outbound_list'],
            'WarmLeadDatetime': contact_details['properties']['date_became_the_warm_lead'],
            'MembershipDatetime': contact_details['membershipTimestamp'],
            'CreatedDatetime': contact_details['createdAt'],
            'UpdatedDatetime': contact_details['updatedAt'],
            'URL': contact_details['url'],
            'Product': contact_details['properties']['product'],
            'BPS': contact_details['properties']['bps'],
            'BudgetRange': contact_details['properties']['budget_range'],
            'CreatedOnWeekend': contact_details['properties']['created_on_weekend'],
            'AnalyticsSource': contact_details['properties']['hs_analytics_source'],
            'LatestSource': contact_details['properties']['hs_latest_source'],
            'LeadStatus': contact_details['properties']['hs_lead_status'],
            'IsMarketable': 1 if contact_details['properties']['hs_marketable_status'] == 'true' else 0,
            'KustomerID': contact_details['properties']['kustomer_id'],
            'LastFive9CallDatetime': contact_details['properties']['last_five9_call_at'],
            'LastFive9CallDisposition': contact_details['properties']['last_five9_call_disposition'],
            'LeadGrade': contact_details['properties']['lead_grade'],
            'LeadSource': contact_details['properties']['lead_source'],
            'ID': 0,
        }
        bp = 'here'


    def format_AfterHoursLeads(self, data_extract):
        bp = 'here'

        
    def format_FlipCallbackLeads(self, data_extract):
        bp = 'here'


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

