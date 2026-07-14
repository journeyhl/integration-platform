
from integration_platform.pipelines.base import Pipeline
from integration_platform.transform.acu_to_dbc_inventory_summary import Transform
from datetime import datetime
from zoneinfo import ZoneInfo
import polars as pl
class AcuToDbcInventorySummary(Pipeline):
    def __init__(self, function):
        super().__init__('acu-to-dbc-inventory-summary', function)
        self.transformer = Transform(self)

    def extract(self) -> pl.DataFrame:
        data_extract = self.acudb.query_to_dataframe(query=self.acudb.queries.AcuToDbc_InventorySummary)
        return data_extract
    

    def transform(self, data_extract):
        data_transformed = self.transformer.landing(data_extract)
        return data_transformed
    

    def load(self, data_transformed):
        total = len(data_transformed)
        for item in data_transformed:
            item['InsertedDT'] = datetime.now(ZoneInfo('America/New_York'))
            item['LastChecked'] = datetime.now(ZoneInfo('America/New_York'))
        self.logger.info(f'{total} rows to upsert')
        self.centralstore.checked_upsert_paginated('acu.InventorySummary', data_transformed, page_size= 100)
        bp = 'here'
        return data_transformed


    def log_results(self, data_loaded):
        pass