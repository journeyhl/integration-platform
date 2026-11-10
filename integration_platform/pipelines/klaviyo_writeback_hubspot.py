from integration_platform.pipelines import Pipeline
from integration_platform.transform.klaviyo_writeback_hubspot import Transform
from integration_platform.connectors.hubspot_api import HubSpotAPI
from integration_platform.connectors.klaviyo import KlaviyoAPI



class KlaviyoWritebackHubspot(Pipeline):
    def __init__(self, function: str, env: str='prod'):
        super().__init__(pipeline_name='KlaviyoWritebackHubspot', function=function, env=env)
        self.hubspot = HubSpotAPI(self)
        self.klaviyo = KlaviyoAPI(self)
        self.transformer = Transform(self)

    def extract(self):
        contacts = self.centralstore.query_to_dataframe(query=self.centralstore.queries.KlaviyoWritebackHubspot)
        merged_contacts = self.centralstore.query_db(query="""
        select RecordID, MergedContactIDs
        from ucmiraw.HubspotCustomers
        where mergedcontactids is not null
        """)
        data_extract = {
            'contacts': contacts.to_dicts(),
            'merged_contacts': merged_contacts.to_dicts()
        }
        return data_extract

    def transform(self, data_extract):
        data_transformed = self.transformer.landing(data_extract=data_extract)
       
        return data_transformed
    
    def load(self, data_transformed):
        data_loaded = {}
        return data_loaded
    
    def log_results(self, data_loaded):
        pass