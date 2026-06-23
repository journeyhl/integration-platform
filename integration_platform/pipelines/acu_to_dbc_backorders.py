
from integration_platform.pipelines import Pipeline
from integration_platform.connectors import AcumaticaAPI
import polars as pl
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

class AcuToDbcBackordersPointInTime(Pipeline):
    '''`AcuToDbcSalesOrders`(Pipeline)
    ---
    <hr>

    Gets all Sales Orders from AcumaticaDb that were modified within the last few hours and loads them to **acu.SalesOrders**

    # Extraction
     - Gets all Sales Orders from AcumaticaDb that were modified within the last few hours
        - OrderType not in('QT', 'RA', 'RC', 'RR', 'RM')

    # Transformation
     - Transforms extracted data into a format needed for acu.SalesOrders

    # Load
     - Upsert to **acu.SalesOrders** via :class:`~connectors.sql.SQLConnector`.:meth:`~connectors.sql.SQLConnector.checked_upsert_paginated`

    # Results Logging
     - None needed
    '''
    def __init__(self, function: str):
        super().__init__('acu-to-dbc-backorders', function)


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
        for item in data_transformed:
            item['Timestamp'] = now
            item['Date'] = now.date()
        self.logger.info(f'{total} rows to upsert')
        self.centralstore.checked_upsert_paginated('acu.BackordersPointInTime', data_transformed, page_size= 100)
        return data_transformed
    
    def log_results(self, data_loaded):
        pass
