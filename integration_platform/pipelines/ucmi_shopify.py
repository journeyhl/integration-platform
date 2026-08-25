from integration_platform.pipelines import Pipeline
from integration_platform.transform.ucmi_shopify import Transform



class UCMI_ShopifyCustomers(Pipeline):
    def __init__(self, function: str, env: str='prod'):
        super().__init__(pipeline_name='ucmi-shopify-customers', function=function, env=env)
        # self.hubspot = HubSpotAPI(self)
        self.transformer = Transform(self)

    def extract(self):
        data_extract = {}
        return data_extract

    def transform(self, data_extract):
        data_transformed = self.transformer.landing(data_extract=data_extract)
       
        return data_transformed
    
    def load(self, data_transformed):
        data_loaded = {}
        return data_loaded
    
    def log_results(self, data_loaded):
        pass