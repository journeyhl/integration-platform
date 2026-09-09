from integration_platform.pipelines import Pipeline
from integration_platform.connectors import HubSpotAPI, SFTP
from integration_platform.transform.ucmi_hubspot import Transform
from datetime import datetime
from zoneinfo import ZoneInfo


class UCMI_HubspotCustomers(Pipeline):
    def __init__(self, function: str, env: str='prod'):
        super().__init__(pipeline_name='ucmi-hubspot-customers', function=function, env=env)
        self.hubspot = HubSpotAPI(self)
        self.sftp = SFTP(self)
        self.transformer = Transform(self)

    def extract(self):
        for i in range(1, 6):
            extract = self.sftp.get_file_as_dataframe(type='xlsx', path=f'/apps/ucmi/hubspot_8.26_{i}.xlsx')
            bp = 'here'
        # data_extract = self.sftp.get_file_as_dataframe(type='xlsx', path='/apps/ucmi/hubspot_8.26_7.xlsx')
        data_extract = self.sftp.get_file_as_dataframe(type='xlsx', path='/apps/ucmi/hubspot_8.26_6.xlsx')
        return data_extract

    def transform(self, data_extract):
        data_transformed = self.transformer.landing(data_extract=data_extract)
       
        return data_transformed
    
    def load(self, data_transformed):
        data_loaded = {}
        test = self.centralstore.__dataframe_to_table_create_statement__(df=data_transformed, table_name='ucmi.HubspotCustomers')
        now =  datetime.now(ZoneInfo('America/New_York'))
        data_transformed = self.default_loader.add_to_list(data_transformed, {'InsertedDT': now, 'LastChecked': now})
        self.centralstore.checked_upsert_paginated(table_name='ucmiraw.HubspotCustomers', data=data_transformed)
        return data_loaded
    
    def log_results(self, data_loaded):
        pass