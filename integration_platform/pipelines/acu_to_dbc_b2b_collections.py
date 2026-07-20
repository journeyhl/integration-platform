
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
    

    def transform(self, data_extract) -> dict[str, pl.DataFrame]:
        data_transformed = self.transformer.landing(data_extract)
        return data_transformed
    

    def load(self, data_transformed: dict[str, pl.DataFrame]):
        collections_detail = data_transformed['detail'].with_columns(pl.lit(datetime.now(ZoneInfo('America/New_York')), pl.Datetime).alias('InsertedDT')).to_dicts()
        collections_summary = data_transformed['summary'].with_columns(pl.lit(datetime.now(ZoneInfo('America/New_York')), pl.Datetime).alias('InsertedDT')).to_dicts()
        collections_detail_snapshot = data_transformed['summary_snapshot']

        bp = 'here'
        self.centralstore.insert_df(df_data_loaded=collections_detail_snapshot, table_name = 'analytics.B2BCollectionsSummary_Snapshot')
        self.centralstore.checked_upsert_paginated(table_name='analytics.B2BCollectionsDetail', data=collections_detail)
        self.centralstore.checked_upsert_paginated(table_name='analytics.B2BCollectionsSummary', data=collections_summary)
        bp = 'here'

        # self.centralstore.insert_df(df_data_loaded=collections_detail, table_name = 'acu.B2BCollectionDetail')
        # self.centralstore.insert_df(df_data_loaded=collections_summary, table_name = 'acu.B2BCollectionSummary')
        # self.logger.info(f'{total} rows to upsert')
        return data_transformed


    def log_results(self, data_loaded):
        pass