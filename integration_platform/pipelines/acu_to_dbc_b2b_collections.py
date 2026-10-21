
from integration_platform.pipelines.base import Pipeline
from integration_platform.transform.acu_to_dbc_b2b_collections import Transform
from datetime import datetime
from zoneinfo import ZoneInfo
import polars as pl
from integration_platform.connectors.sql import SQLConnector, AcumaticaDbQueries
class AcuToDbcB2BCollections(Pipeline):
    ''':class:`~integration_platform.pipelines.acu_to_dbc_b2b_collections.AcuToDbcB2BCollections`
    ---
    
    ## Initialization

    Sets transformer, 

    <hr>

    ## Extraction
    
    Pulls all open Accounts Receivable documents belonging to B2B customers and each document's outstanding balance

    <hr>

    ## Transformation

    Summarized the outstanding balance by Customer and also Salesperson, then splits into buckets based on how overdue that balance is

    <hr>

    ## Load

    Loads to db_CentralStore via merge:

    - analytics.JHL_B2BCollectionsDetail
    - analytics.JHL_B2BCollectionsSummary
    - analytics.JHL_B2BCollectionsSummary_Snapshot
    - analytics.JHL_B2BCollectionsByStatus
    - analytics.JHL_B2BCollectionsByStatus_Snapshot
    - analytics.JHL_B2BCollectionsBySalesRep
    - analytics.JHL_B2BCollectionsBySalesRep_Snapshot

    '''
    def __init__(self, function, env: str = 'prod'):
        super().__init__(pipeline_name='acu-to-dbc-b2b-collections', function=function, env=env)
        self.transformer = Transform(self)
        self.acudb: SQLConnector[AcumaticaDbQueries] = SQLConnector(
            pipeline=self, database_name='AcudevDb' if env == 'dev' else 'AcumaticaDb'
        )

    def extract(self) -> pl.DataFrame:
        data_extract = self.acudb.query_to_dataframe(query=self.acudb.queries.AcuToDbc_B2BCollections)
        return data_extract
    

    def transform(self, data_extract) -> dict[str, pl.DataFrame]:
        data_transformed = self.transformer.landing(data_extract)
        return data_transformed
    

    def load(self, data_transformed: dict):
        frame_count = len(data_transformed)
        for i, (table, data) in enumerate(data_transformed.items()):
            prefix = f'{i+1}/{frame_count}: '
            self.logger.info(f'{prefix}Merging {len(data)} rows to {table}...')
            self.centralstore.merge_table_paginated(table_name=table, data=data)
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