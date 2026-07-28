from . import Pipeline
from integration_platform.transform.hubspot_list_to_dbc import Transform
from integration_platform.connectors import HubSpotAPI


class HubspotLeadsToDbc(Pipeline):    
    '''`HubspotLeadsToDbc`(Pipeline)
    ---
    <hr>

    Pipeline to load all Lead lists into one master table

    # Extraction
     - Extracts property data from Hubspot using :class:`~connectors.sql.HubSpotAPI`.:meth:`~connectors.sql.HubSpotAPI._get_properties`

    # Transformation
     - Transforms property extra into format needed for upsert to **hs.Properties**

    # Load
     - Upsert to **hs.Properties**

    # Results Logging
     - Upserts Acumatica API interactions to **_util.acu_api_log** 
    '''
    def __init__(self, function: str):
        super().__init__('hubspot-leads-to-dbc', function)
        self.transformer = Transform(self)
        self.hubapi = HubSpotAPI(self)


    def extract(self):
        open_leads_to_outbound = self.hubapi.get_list_with_membership_contact_details(list_id=1715)
        open_leads_backfill = self.hubapi.get_list_with_membership_contact_details(list_id=3285)
        flip_callbacks_outbound = self.hubapi.get_list_with_membership_contact_details(list_id=2382)
        after_hours_leads = self.hubapi.get_list_with_membership_contact_details(list_id=2315)
        ready_for_outbound = self.hubapi.get_list_with_membership_contact_details(list_id=837)
        lead_status = self.hubapi.get_list_with_membership_contact_details(list_id=2476)
        data_extract = {
            'open_leads_to_outbound': open_leads_to_outbound,
            'open_leads_backfill': open_leads_backfill,
            'flip_callbacks_outbound': flip_callbacks_outbound,
            'after_hours_leads': after_hours_leads,
            'ready_for_outbound': ready_for_outbound,
            'lead_status': lead_status,
        }
        return data_extract

    def transform(self, data_extract: dict[str, dict]):
        data_transformed = self.transformer.landing(data_extract=data_extract)
        return data_transformed
    
    def load(self, data_transformed):
        self.centralstore.checked_upsert_paginated('hs.Properties', data_transformed)
        return data_transformed
    
    def log_results(self, data_loaded):
        pass