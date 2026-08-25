from integration_platform.pipelines import Pipeline



class UCMI_EcometryCustomers(Pipeline):
    def __init__(self, function: str, env: str='prod'):
        super().__init__(pipeline_name='ucmi-ecometry-customers', function=function, env=env)
        # self.hubspot = HubSpotAPI(self)

    def extract(self):
        data_extract = {}
        return data_extract

    def transform(self, data_extract):
        data_transformed = {}
       
        return data_transformed
    
    def load(self, data_transformed):
        data_loaded = {}
        return data_loaded
    
    def log_results(self, data_loaded):
        pass