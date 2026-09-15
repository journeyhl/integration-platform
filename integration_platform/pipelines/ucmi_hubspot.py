from integration_platform.pipelines import Pipeline
from integration_platform.connectors import HubSpotAPI, SFTP
from integration_platform.transform.ucmi_hubspot_phase1 import Transform
from integration_platform.transform.ucmi_hubspot_phase2 import TransformPhase2
from datetime import datetime
from zoneinfo import ZoneInfo


class UCMI_HubspotCustomers(Pipeline):
    def __init__(self, function: str, env: str='prod'):
        super().__init__(pipeline_name='ucmi-hubspot-customers', function=function, env=env)
        self.hubspot = HubSpotAPI(self)
        # self.sftp = SFTP(self)
        self.transformer = Transform(self)
        self.phase2_transformer = TransformPhase2(self)

    def extract(self):
        # data_extract = self.sftp.get_file_as_dataframe(type='xlsx', path='/apps/ucmi/hs26_9.11.xlsx')
        props = 'firstname,lastname,lead_source,email,phone,emailaddress,keycode,product,adddate,createdate,notes_last_updated,hubspot_owner_id,call_summary,hs_lead_status,hs_marketable_status,lead_source_date,intents_during_call,toll_free__,bps,unitsperorder,totalorders,revenueperorder,totalunits,revenue,last_five9_call_disposition,last_five9_call_at,acumatica_product_list,who_is_the_chair_for,notes_last_contacted,notes_next_activity_date,num_contacted_notes,hs_analytics_source,hs_latest_source,date_and_time_added_to_outbound_list,lead_grade,date_added_to_outbound_list,budget_range,created_on_weekend,kustomer_id,sold,date_became_the_warm_lead,s_call_summary,hs_createdate,hs_lastmodifieddate,acumatica_order_number_s_,acumatica_product_name,ai_agent,ai_weekly_review__contact_count,ai_weekly_review__generated_at,ai_weekly_review__html,ai_weekly_review__text,b2b_contact,billing_address,billing_city,billing_state,billing_zip,call_disposition,call_dispositions___five9,call_summary,call_transcript,company,contact_url_hs,country,createdate,date_became_the_dnc_lead_status,date_became_the_lead_exhausted_lead_status,date_became_the_new_lead_status,date_became_the_open_lead_lead_status,date_became_the_outbound_lead_status,date_became_the_reserved_lead_status,date_became_the_sold_lead_status,date_became_the_unqualified_lead_status,do_not_call,email_collection,email_option,first_conversion_date,first_conversion_event_name,firstname,hs_analytics_last_touch_converting_campaign,hs_analytics_num_page_views,hs_analytics_num_visits,hs_current_customer,hs_email_click,hs_email_delivered,hs_email_first_open_date,hs_email_last_send_date,hs_email_open,hs_email_optout,hs_email_optout_5436276,hs_email_optout_62421282,hs_email_optout_7434690,hs_email_optout_768616824,hs_email_replied,hs_email_sends_since_last_engagement,hs_emailconfirmationstatus,hs_lead_status,hs_linkedin_click_id,hs_marketable_status,hs_v2_date_entered_current_stage,hubspot_owner_id,inbound_call_disposition,intents_during_call,ip__ecomm_bridge__ecomm_synced,ip__ecomm_bridge__source_store_id,ip__shopify__accepts_marketing,ip__shopify__shopify_created_at,ip__shopify__verified_email,ip_country_code,ip_state,kustomer_id,kustomer_last_sync,kustomer_sync_error,kustomer_sync_needed,kustomer_sync_status,lastmodifieddate,lastname,lead_source,lead_source_date,notes_last_contacted,notes_last_updated,phone,recent_conversion_date,recent_conversion_event_name,shipping_address,shipping_city,shipping_state,shipping_zip,status,unsubscribe_to_mail,hs_createdate,hs_lastmodifieddate,hs_last_activity_date,hs_lead_source,hs_v2_date_entered_current_stage,hs_createdate,hs_lastmodifieddate,hs_task_last_contact_outreach'
        data_extract = self.hubspot.get_list_with_membership_contact_details(list_id=3534, props=props)
        return data_extract

    def transform(self, data_extract):
        data_transformed = self.transformer.landing(data_extract=data_extract)
       
        return data_transformed
    
    def load(self, data_transformed):
        data_loaded = {}
        now =  datetime.now(ZoneInfo('America/New_York'))
        data_transformed = self.default_loader.add_to_list(data_transformed, {'InsertedDT': now, 'LastChecked': now})
        # self.centralstore.paginated_merge(table_name='ucmiraw.HubspotCustomers', data=data_transformed)
        self.centralstore.checked_upsert_paginated(table_name='ucmiraw.HubspotCustomers', data=data_transformed)
        return data_loaded
    
    def log_results(self, data_loaded):
        pass