
from integration_platform.pipelines import Pipeline
from integration_platform.connectors import AcumaticaAPI
from integration_platform.transform.audit_fulfillment import Transform
import polars as pl
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

class AcuToDbcTrialBalance(Pipeline):
    '''`AcuToDbcTrialBalance`(Pipeline)
    ---
    <hr>

    Gets all ____ and upserts to **acu.TrialBalance**

    '''
    def __init__(self, function: str):
        super().__init__('acu-to-dbc-trial-balance', function)


    def extract(self) -> dict[str, pl.DataFrame]:
        acu_extract = self.acudb.query_to_dataframe(self.acudb.queries.AcuToDbc_TrialBalance)
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
        self.centralstore.checked_upsert_paginated('acu.TrialBalance', data_transformed, page_size= 100)
        return data_transformed
    
    def log_results(self, data_loaded):
        pass
