
from integration_platform.pipelines import Pipeline
from integration_platform.connectors import AcumaticaAPI
import polars as pl
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from integration_platform.connectors.sql import SQLConnector, AcumaticaDbQueries

class AcuToDbcBackordersPointInTime(Pipeline):
    '''`AcuToDbcSalesOrders`(Pipeline)
    ---
    <hr>

    Gets all Sales Orders from AcumaticaDb that are in Back Order status **acu.BackordersPointInTime**

    # Extraction
     - Gets all Backordered Sales Orders
        - OrderType not in('QT')

    # Transformation
     - Casts dataframe as dict 

    # Load
     - Upsert to **acu.BackordersPointInTime** via :class:`~connectors.sql.SQLConnector`.:meth:`~connectors.sql.SQLConnector.checked_upsert_paginated`

    # Results Logging
     - None needed
    '''
    def __init__(self, function: str, env: str='prod'):
        super().__init__(pipeline_name='acu-to-dbc-backorders', function=function, env=env)
        self.acudb: SQLConnector[AcumaticaDbQueries] = SQLConnector(
            pipeline=self, database_name='AcudevDb' if env == 'dev' else 'AcumaticaDb'
        )


    def extract(self) -> dict[str, pl.DataFrame]:
        acu_extract = self.acudb.query_to_dataframe(self.acudb.queries.AcuToDbc_BackordersPointInTime)
        data_extract = {
            'acu_extract': acu_extract,
            'dbc_extract': '' #dbc_extract 
        }
        return data_extract

    def transform(self, data_extract: dict[str, pl.DataFrame]):
        acu_extract = data_extract['acu_extract'].to_dicts()


        data_transformed = acu_extract
        return data_transformed
    
    def load(self, data_transformed):
        total = len(data_transformed)
        now = datetime.now(ZoneInfo('America/New_York'))
        data_transformed = self.default_loader.add_to_list(data_transformed, {'Timestamp': now, 'Date': now.date()})
        self.logger.info(f'{total} rows to upsert')
        self.centralstore.checked_upsert_paginated('acu.BackordersPointInTime', data_transformed, page_size= 100)
        return data_transformed
    
    def log_results(self, data_loaded):
        pass
