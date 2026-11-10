from integration_platform.pipelines import Pipeline
from integration_platform.connectors.sql import SQLConnector, AcumaticaDbQueries
import polars as pl
from datetime import datetime
from zoneinfo import ZoneInfo

class UCMI_AcumaticaCustomers(Pipeline):
    def __init__(self, function: str, env: str='prod'):
        super().__init__(pipeline_name='UCMI_AcumaticaCustomers', function=function, env=env)
        self.acudb: SQLConnector[AcumaticaDbQueries] = SQLConnector(
            pipeline=self, database_name='AcudevDb' if env == 'dev' else 'AcumaticaDb'
        )

    def extract(self):
        data_extract = self.acudb.query_to_dataframe(query=self.acudb.queries.ucmi_AcumaticaCustomers)
        return data_extract

    def transform(self, data_extract: pl.DataFrame):
        data_transformed = data_extract.with_columns(
            pl.lit('Acumatica').alias('Source'),
            pl.lit(value=datetime.now(ZoneInfo('America/New_York')), dtype=pl.Datetime).alias('InsertedDT'),
            pl.lit(value=datetime.now(ZoneInfo('America/New_York')), dtype=pl.Datetime).alias('LastChecked')

        ).to_dicts()
       
        return data_transformed
    
    def load(self, data_transformed):
        data_loaded = self.centralstore.merge_table_paginated(table_name='ucmiraw.Customers_Acu', data=data_transformed)
        return data_loaded
    
    def log_results(self, data_loaded):
        pass