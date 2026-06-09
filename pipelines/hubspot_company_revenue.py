from pipelines import Pipeline
from connectors import HubSpotAPI
from transform.hubspot_company_revenue import Transform




class HubspotCompanyRevenue(Pipeline):
    def __init__(self, function: str, env: str='prod'):
        # function = 'consignment_reclassifications'
        super().__init__(pipeline_name='consignment-reclassifications', function=function, env=env)
        self.hubspot = HubSpotAPI(self)
        self.transformer = Transform(self)

    def extract(self):
        hubspot_extract = self.hubspot.retrieve_companies(limit=100)        
        data_extract = {
            'hubspot_extract': hubspot_extract,
            'revenue_extract': self.centralstore.query_to_dataframe(self.centralstore.queries.HubSpot_RevenueByCustomer)
        }
        return data_extract

    def transform(self, data_extract):
        data_transformed = self.transformer.transform(data_extract)
        return data_transformed
    
    def load(self, data_transformed):
        data_loaded = data_transformed
        return data_loaded
    
    def log_results(self, data_loaded):
        pass