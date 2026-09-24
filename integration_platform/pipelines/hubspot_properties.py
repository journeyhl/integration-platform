from . import Pipeline
from integration_platform.transform.notify_fulfillment_ops import Transform
from integration_platform.connectors import HubSpotAPI
from datetime import datetime
from zoneinfo import ZoneInfo

class HubSpotProperties(Pipeline):    
    '''`HubSpotProperties`(Pipeline)
    ---
    <hr>

    Pipeline to load properties from main ObjectTypes in Hubspot to ***hs.Properties*** in db_CentralStore

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
        super().__init__('hubspot-properties', function)
        self.transformer = Transform(self)
        self.hubapi = HubSpotAPI(self)


    def extract(self):
        contacts = self.hubapi.get_properties('contacts')
        calls = self.hubapi.get_properties('calls')
        emails = self.hubapi.get_properties('emails')
        meetings = self.hubapi.get_properties('meetings')
        tasks = self.hubapi.get_properties('tasks')
        # deals = self.hubapi._get_properties('deals')
        leads = self.hubapi.get_properties('leads')
        territories = self.hubapi.get_properties(object_type='2-67850902',object_type_name='territories') #territories
        zip_codes = self.hubapi.get_properties(object_type='2-61043340',object_type_name='zip_codes') #zip_codes
        data_extract = contacts + calls + emails + meetings + tasks +  leads + territories + zip_codes
        self.ts_extract = datetime.now(ZoneInfo('America/New_York'))
        return data_extract

    def transform(self, data_extract):
        data_transformed = []
        for item in data_extract:
            data_transformed.append({
                'ObjectType': item['ObjectType'],
                'otName': item['otName'],
                'Name': item['name'],
                'Label': item['label'],
                'GroupName': item['groupName'],
                'Description': item['description'],
                'Type': item['type'],
                'FieldType': item['fieldType'],
                'CreatedUserId': item.get('createdUserId'),
                'UpdatedUserId': item.get('updatedUserId'),
                'DisplayOrder': item['displayOrder'],
                'Calculated': item['calculated'],
                'Archived': item.get('archived'),
                'Hidden': item['hidden'],
                'HubspotDefined': item.get('hubspotDefined'),
                'CreatedAt': item.get('createdAt'),
                'UpdatedAt': item.get('updatedAt'),
            })
        return data_transformed
    
    def load(self, data_transformed):
        now = datetime.now(ZoneInfo('America/New_York'))
        data_transformed = self.default_loader.add_to_list(ldata=data_transformed, additions={'InsertedDT': now, 'LastChecked': self.ts_extract})
        self.centralstore.merge_table_paginated(table_name='hs.Properties', data=data_transformed)
        return data_transformed
    
    def log_results(self, data_loaded):
        pass