from integration_platform.pipelines.base import Pipeline
from integration_platform.connectors.sftp import SFTP
from integration_platform.transform.darwill_addresses import Transform

import polars as pl
from datetime import datetime
from zoneinfo import ZoneInfo


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

    def transform(self, data_extract: pl.DataFrame):
        data_transformed = self.transformer.transform(data_extract)
        return data_transformed
    
    def load(self, data_transformed):
        self.centralstore.checked_upsert_paginated('ucmi.DarwillAddresses', data_transformed)
        data_loaded = data_transformed
        return data_loaded
    
    def log_results(self, data_loaded):
        pass





    def etl_with_csv(self, csv_file_path: str, source_file: str):
        db_extract = self.centralstore.query_to_dataframe(query=self.centralstore.queries.DarwillAddresses)
        file_extract = pl.read_csv(csv_file_path, infer_schema_length=None)
        file_extract = file_extract.with_columns(pl.col('CustomerID').cast(pl.String).alias('CustomerID'))
        ready, needed_lookup = self.transformer.transform_etl_with_csv(db_extract=db_extract, file_extract=file_extract, source_file=source_file)

        self.centralstore.checked_upsert_paginated(table_name='ucmi.DarwillAddresses', data=ready, page_size=250)
        bp = 'here'
        self.centralstore.checked_upsert_paginated(table_name='ucmi.DarwillAddresses', data=needed_lookup, page_size=250)
        bp = 'here'
        try:
            self.centralstore.insert_df(pl.DataFrame(self.logs), '_util.Logs')
        except Exception as e:
            self.logger.warning(f"{e}: Couldn't insert logs to SQL but pipeline execution was successful")