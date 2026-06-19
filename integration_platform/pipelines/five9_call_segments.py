from integration_platform.pipelines.base import Pipeline
from integration_platform.connectors.sftp import SFTP
from integration_platform.transform.five9_call_segments import Transform
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo



class Five9CallSegments(Pipeline):
    def __init__(self, function: str, env: str='prod'):
        # function = 'consignment_reclassifications'
        super().__init__(pipeline_name='five9-call-segments', function=function, env=env)
        self.transformer = Transform(self)
        self.sftp = SFTP(self)

    def extract(self):
        five9_extract = self.sftp.get_csv_file_as_dataframe()
        now = datetime.now(ZoneInfo('America/New_York')).strftime('%Y%m%d')
        db_extract = self.centralstore.query_db(f"""select * from Five9CallSegments f where f.Timestamp >= '{now}'""")
        data_extract = {
            'five9_extract': five9_extract,
            'db_extract': db_extract
        }
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