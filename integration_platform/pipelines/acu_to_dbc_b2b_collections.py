
from integration_platform.pipelines.base import Pipeline
from integration_platform.transform.acu_to_dbc_b2b_collections import Transform
from datetime import datetime
from zoneinfo import ZoneInfo
import polars as pl
class AcuToDbcB2BCollections(Pipeline):
    def __init__(self, function, backfill: bool = False):
        super().__init__('acu-to-dbc-b2b-collections', function)
        self.transformer = Transform(self)
        self.backfill = backfill
        if self.backfill:
            self.logger.warning(f'Running in backfill mode!!!')

    def extract(self) -> pl.DataFrame:
        data_extract = self.acudb.query_to_dataframe(query=self.acudb.queries.AcuToDbc_B2BCollections)
        return data_extract
    

    def transform(self, data_extract) -> dict[str, pl.DataFrame]:
        data_transformed = self.transformer.landing(data_extract)
        return data_transformed
    

    def load(self, data_transformed: dict[str, pl.DataFrame]):
        collections_detail = data_transformed['detail'].with_columns(pl.lit(datetime.now(ZoneInfo('America/New_York')), pl.Datetime).alias('InsertedDT'))
        collections_summary = data_transformed['summary'].with_columns(pl.lit(datetime.now(ZoneInfo('America/New_York')), pl.Datetime).alias('InsertedDT'))
        balance_by_status = data_transformed['balance_by_status'].with_columns(pl.lit(datetime.now(ZoneInfo('America/New_York')), pl.Datetime).alias('InsertedDT'))
        balance_by_salesrep = data_transformed['balance_by_salesrep'].with_columns(pl.lit(datetime.now(ZoneInfo('America/New_York')), pl.Datetime).alias('InsertedDT'))
        collections_summary_snapshot = data_transformed['summary_snapshot']
        balance_by_status_snapshot = data_transformed['balance_by_status_snapshot']
        balance_by_salesrep_snapshot = data_transformed['balance_by_salesrep_snapshot']
        dfs = {
            'analytics.JHL_B2BCollectionsDetail': collections_detail,
            'analytics.JHL_B2BCollectionsSummary': collections_summary,
            'analytics.JHL_B2BCollectionsSummary_Snapshot': collections_summary_snapshot,
            'analytics.JHL_B2BCollectionsByStatus': balance_by_status,
            'analytics.JHL_B2BCollectionsByStatus_Snapshot': balance_by_status_snapshot,
            'analytics.JHL_B2BCollectionsBySalesRep': balance_by_salesrep,
            'analytics.JHL_B2BCollectionsBySalesRep_Snapshot': balance_by_salesrep_snapshot,
        }
        if self.backfill:
            self.load_backfill(dfs)
            return data_transformed
        
        frame_count = len(dfs)
        for i, (table, data) in enumerate(dfs.items()):
            prefix = f'{i+1}/{frame_count}: '
            data_dict = data.to_dicts()
            self.logger.info(f'{prefix}Upserting {len(data_dict)} rows to {table}...')
            self.centralstore.checked_upsert_paginated(table_name=table, data=data_dict)
        return data_transformed


    def load_backfill(self, dfs: dict[str, pl.DataFrame]):
        frame_count = len(dfs)
        for i, (table, data) in enumerate(dfs.items()):
            prefix = f'{i+1}/{frame_count}: '
            self.logger.info(f'{prefix}Deleting {data.height} rows from {table}...')
            self.centralstore.raw_execute(f'delete from {table}')
            self.logger.info(f'{prefix}Inserting {data.height} rows to {table}...')
            bp = 'here'
            self.centralstore.insert_df(df_data_loaded=data, table_name=table)
            bp = 'here'




    def log_results(self, data_loaded):
        pass