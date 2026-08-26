from integration_platform.pipelines import Pipeline
from integration_platform.connectors import HubSpotAPI, SFTP
from integration_platform.transform.ucmi_hubspot import Transform



class UCMI_HubspotCustomers(Pipeline):
    def __init__(self, function: str, env: str='prod'):
        super().__init__(pipeline_name='ucmi-hubspot-customers', function=function, env=env)
        self.hubspot = HubSpotAPI(self)
        self.sftp = SFTP(self)
        self.transformer = Transform(self)

    def extract(self):
        # for i in range(1, 6):
        #     extract = self.sftp.get_file_as_dataframe(type='xlsx', path=f'/apps/ucmi/hubspot_8.26_{i}.xlsx')
        #     bp = 'here'
        data_extract = self.sftp.get_file_as_dataframe(type='xlsx', path='/apps/ucmi/hubspot_8.26_7.xlsx')
        return data_extract

    def transform(self, data_extract):
        data_transformed = self.transformer.landing(data_extract=data_extract)
       
        return data_transformed
    
    def load(self, data_transformed):
        data_loaded = {}
        self.centralstore.insert_df(data_transformed, 'hubspot_test')
        return data_loaded
    
    def log_results(self, data_loaded):
        pass