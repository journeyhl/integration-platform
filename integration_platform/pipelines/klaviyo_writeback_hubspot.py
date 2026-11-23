from integration_platform.pipelines import Pipeline
from integration_platform.transform.klaviyo_writeback_hubspot import Transform
from integration_platform.transform.klaviyo_writeback_hubspot_phase2 import TransformPhase2
from integration_platform.transform.klaviyo_writeback_hubspot_phase3 import TransformPhase3
from integration_platform.connectors.hubspot_api import HubSpotAPI
from integration_platform.connectors.klaviyo import KlaviyoAPI
from integration_platform.helpers.klaviyo_writeback_hubspot import KlaviyoHubspotComparer
import json
from datetime import datetime
from zoneinfo import ZoneInfo
class KlaviyoWritebackHubspot(Pipeline):
    def __init__(self, function: str, env: str='prod'):
        super().__init__(pipeline_name='KlaviyoWritebackHubspot', function=function, env=env)
        self.hubspot = HubSpotAPI(self)
        self.klaviyo = KlaviyoAPI(self)
        self.transformer = Transform(self)
        self.transformer_phase2 = TransformPhase2(self)
        self.transformer_phase3 = TransformPhase3(self)
        self.comparer = KlaviyoHubspotComparer(self)

    def extract(self):
        contacts = self.centralstore.query_to_dataframe(query=self.centralstore.queries.KlaviyoWritebackHubspot)
        merged_contacts = self.centralstore.query_db(query="""
        select RecordID, MergedContactIDs
        from ucmiraw.HubspotCustomers
        where mergedcontactids is not null
        """)
        property_data = self.centralstore.query_db("select * from hs.Properties where otName = 'Contacts'").to_dicts()
        data_extract = {
            'contacts': contacts.to_dicts(),
            'merged_contacts': merged_contacts.to_dicts(),
        }
        self.read_only = [row['Name'] for row in property_data if row['ReadOnly'] == True]
        self.date_types = [row['Name'] for row in property_data if row['FieldType'] == 'date']
        return data_extract

    def transform(self, data_extract):
        contacts = self.transformer.landing(data_extract=data_extract)
        contacts_to_update, no_update = self.transformer_phase2.landing(data_transformed=contacts)
        hubspot_payloads = self.transformer_phase3.landing(data_transformed=contacts_to_update)
        data_transformed = {
            'contacts': contacts,
            'contacts_to_update': contacts_to_update,
            'hubspot_payloads': hubspot_payloads,
            'no_update': no_update
        }
        return data_transformed
    
    def load(self, data_transformed):
        data_loaded = []
        timestamp = datetime.now(ZoneInfo('America/New_York'))
        total = len(data_transformed['hubspot_payloads'])
        for i, contact in enumerate(data_transformed['hubspot_payloads']):
            prefix = f'{i+1}/{total}: '
            self.hubspot.update_object_by_id(object_type='contacts', object_id=contact['object_id'], property_payload=contact['payload'], log_prefix=prefix)
            data_loaded.append({'RecordID': contact['object_id'], 'Payload': json.dumps(contact['payload']), 'Timestamp': timestamp})
        data_loaded.extend([{**record, 'Timestamp': timestamp} for record in data_transformed['no_update']])
        self.centralstore.merge_table_paginated(table_name='hs.KlaviyoHubspotWritebackLog', data=data_loaded)
        return data_loaded
    
    def log_results(self, data_loaded):
        pass