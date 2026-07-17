
from integration_platform.pipelines.base import Pipeline
from integration_platform.transform.acu_to_dbc_b2b_collections import Transform
from datetime import datetime
from zoneinfo import ZoneInfo
import polars as pl
class AcuToDbcB2BCollections(Pipeline):
    def __init__(self, function):
        super().__init__('acu-to-dbc-b2b-collections', function)
        self.transformer = Transform(self)

    def extract(self) -> pl.DataFrame:
        data_extract = self.acudb.query_to_dataframe(query=self.acudb.queries.AcuToDbc_B2BCollections)
        return data_extract
    

    def transform(self, data_extract):
        data_transformed = self.transformer.landing(data_extract)
        return data_transformed
    

    def load(self, data_transformed):
        collections_summary = data_transformed['summary']
        collections_detail = data_transformed['detail']
        self.centralstore.insert_df(df_data_loaded=collections_summary, table_name = 'acu.B2BCollectionSummary')
        self.centralstore.insert_df(df_data_loaded=collections_detail, table_name = 'acu.B2BCollectionDetail')

        # total = len(data_transformed)
        # for item in data_transformed:
        #     item['InsertedDT'] = datetime.now(ZoneInfo('America/New_York'))
        #     item['LastChecked'] = datetime.now(ZoneInfo('America/New_York'))
        # self.logger.info(f'{total} rows to upsert')
        # self.centralstore.checked_upsert_paginated('acu.InventorySummary', data_transformed, page_size= 100)
        bp = 'here'
        return data_transformed


    def log_results(self, data_loaded):
        pass