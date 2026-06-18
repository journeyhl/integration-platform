
from integration_platform.pipelines import Pipeline
from integration_platform.connectors import AcumaticaAPI
from integration_platform.transform.audit_fulfillment import Transform
import polars as pl
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

class AcuToDbcShipments(Pipeline):
    '''`AcuToDbcShipments`(Pipeline)
    ---
    <hr>

    Gets all ____ and upserts to **acu.Shipments**

    # Extraction
     - Gets all QT type Sales Orders from AcumaticaDb that were modified within the last day and loads them to **acu.Shipments**

    # Transformation
     - Transforms extracted data into a format needed for **acu.Shipments**

    # Load
     - Upsert to **acu.Shipments** via :class:`~connectors.sql.SQLConnector`.:meth:`~connectors.sql.SQLConnector.checked_upsert_paginated`

    # Results Logging
     - None needed
    '''
    def __init__(self, function: str):
        super().__init__('acu-to-dbc-shipments', function)


    def extract(self) -> dict[str, pl.DataFrame]:
        acu_extract = self.acudb.query_to_dataframe(self.acudb.queries.AcuToDbc_Shipments)
        # dbc_extract = self.centralstore.query_db('select distinct ShipmentNbr from acu.Shipments where LastChecked is not null')
        data_extract = {
            'acu_extract': acu_extract,
            'dbc_extract': '' #dbc_extract
        }
        return data_extract

    def transform(self, data_extract: dict[str, pl.DataFrame]):
        dbc_extract = data_extract['dbc_extract']
        acu_extract = data_extract['acu_extract']
        # acu_extract = data_extract['acu_extract'].join(
        #     dbc_extract, on='ShipmentNbr', how='anti'
        # )
        acu_extract = acu_extract.to_dicts()


        data_transformed = acu_extract
        return data_transformed
    
    def load(self, data_transformed):
        total = len(data_transformed)
        for item in data_transformed:
            item['InsertedDT'] = datetime.now(ZoneInfo('America/New_York'))
            item['LastChecked'] = datetime.now(ZoneInfo('America/New_York'))
        self.logger.info(f'{total} rows to upsert')
        self.centralstore.checked_upsert_paginated('acu.Shipments', data_transformed, page_size= 100)
        return data_transformed
    
    def log_results(self, data_loaded):
        pass
