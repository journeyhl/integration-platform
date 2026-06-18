from pipelines.base import Pipeline
from connectors.sftp import SFTP
from transform.darwill_addresses import Transform




class DarwillAddresses(Pipeline):
    def __init__(self, function: str, env: str='prod'):
        # function = 'consignment_reclassifications'
        super().__init__(pipeline_name='darwill-addresses', function=function, env=env)
        self.transformer = Transform(self)
        self.sftp = SFTP(self, server='Darwill')

    def extract(self):
        dir_list = self.sftp.list_directories()
        file_list = self.sftp.list_directory(directory='/downloads')
        file_list.sort(key=lambda x: x['dt_added'], reverse=True)
        self.most_recent_file = file_list[0]
        data_extract = self.sftp.get_csv_file_as_dataframe(path=self.most_recent_file['path'])
        return data_extract

    def transform(self, data_extract):
        data_transformed = self.transformer.transform(data_extract)
        return data_transformed
    
    def load(self, data_transformed):
        self.centralstore.checked_upsert_paginated('.', data_transformed)
        data_loaded = data_transformed
        return data_loaded
    
    def log_results(self, data_loaded):
        pass