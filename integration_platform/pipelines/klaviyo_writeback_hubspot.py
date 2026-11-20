from integration_platform.pipelines import Pipeline
from integration_platform.transform.klaviyo_writeback_hubspot import Transform
from integration_platform.transform.klaviyo_writeback_hubspot_phase2 import TransformPhase2
from integration_platform.transform.klaviyo_writeback_hubspot_phase3 import TransformPhase3
from integration_platform.connectors.hubspot_api import HubSpotAPI
from integration_platform.connectors.klaviyo import KlaviyoAPI
from integration_platform.helpers.klaviyo_writeback_hubspot import KlaviyoHubspotComparer


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
        contacts_to_update = self.transformer_phase2.landing(data_transformed=contacts)
        hubspot_payloads = self.transformer_phase3.landing(data_transformed=contacts_to_update)
        data_transformed = {
            'contacts': contacts,
            'contacts_to_update': contacts_to_update,
            'hubspot_payloads': hubspot_payloads,
        }
        return data_transformed
    
    def load(self, data_transformed):
        data_loaded = []
        for i, contact in enumerate(data_transformed['hubspot_payloads']):
            self.hubspot.update_object_by_id(object_type='contacts', object_id=contact['object_id'], property_payload=contact['payload'])
            data_loaded.append(contact)
        return data_loaded
    
    def log_results(self, data_loaded):
        pass