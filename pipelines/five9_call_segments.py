from pipelines import Pipeline
from connectors import SFTP
from transform.five9_call_segments import Transform




class Five9CallSegments(Pipeline):
    def __init__(self, function: str, env: str='prod'):
        # function = 'consignment_reclassifications'
        super().__init__(pipeline_name='five9-call-segments', function=function, env=env)
        self.transformer = Transform(self)
        self.sftp = SFTP(self)

    def extract(self):
        data_extract = self.sftp.get_csv_file_as_dataframe()
        return data_extract

    def transform(self, data_extract):
        data_transformed = self.transformer.transform(data_extract)
        return data_transformed
    
    def load(self, data_transformed):
        self.centralstore.checked_upsert_paginated('Five9CallSegments', data_transformed)
        data_loaded = data_transformed
        return data_loaded
    
    def log_results(self, data_loaded):
        pass