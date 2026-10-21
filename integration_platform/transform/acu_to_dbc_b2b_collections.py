from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.acu_to_dbc_b2b_collections import AcuToDbcB2BCollections
import logging
import polars as pl
from datetime import datetime
from zoneinfo import ZoneInfo
class Transform:

    def __init__(self, pipeline: AcuToDbcB2BCollections):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.Transform')
        self.summary_group_by_columns= [
            'CustomerID', 
            'CustomerName',
            'SalespersonID',
            'TermsID',
            'CustomerStatus',
            'State',
            'Email',
            'Phone',
            'LastChecked'
        ]
        pass


    def landing(self, data_extract: pl.DataFrame):
        #.with_columns(pl.lit(datetime.now(ZoneInfo('America/New_York')), pl.Datetime).alias('LastChecked'))
        bp = 'here'
        data_extract = data_extract.with_columns(pl.lit(datetime.now(ZoneInfo('America/New_York')), pl.Datetime).alias('LastChecked'))
        self.data_extract = data_extract
        collections_summary, collections_summary_snapshot = self._aggregate_by_metric_(self.summary_group_by_columns)
        balance_by_status, balance_by_status_snapshot = self._aggregate_by_metric_(group_by_columns=['LastChecked', 'CustomerStatus'])
        balance_by_salesrep, balance_by_salesrep_snapshot = self._aggregate_by_metric_(group_by_columns=['LastChecked', 'SalespersonID'])
        # self.pipeline.centralstore.__dataframe_to_table_create_statement__(balance_by_status)


        data_transformed = {
            'analytics.JHL_B2BCollectionsDetail': data_extract,
            'analytics.JHL_B2BCollectionsSummary': collections_summary,
            'analytics.JHL_B2BCollectionsSummary_Snapshot': collections_summary_snapshot,
            'analytics.JHL_B2BCollectionsByStatus': balance_by_status,
            'analytics.JHL_B2BCollectionsByStatus_Snapshot': balance_by_status_snapshot,
            'analytics.JHL_B2BCollectionsBySalesRep': balance_by_salesrep,
            'analytics.JHL_B2BCollectionsBySalesRep_Snapshot': balance_by_salesrep_snapshot,
        }
        data_transformed = self._to_lists_(data_transformed=data_transformed)
        return data_transformed

    def _to_lists_(self, data_transformed: dict):
        now = datetime.now(ZoneInfo(key='America/New_York'))
        for table, frame in data_transformed.items():
            frame = frame.to_dicts()
            self.pipeline.default_loader.add_InsertedDT_to_list(ldata=frame, now=now)
            data_transformed[table] = frame
        return data_transformed


    
    def _aggregate_by_metric_(self, group_by_columns: list = []):
        aggregate_data = self.data_extract.group_by(group_by_columns, maintain_order=True).agg(
            pl.col('CurrentBalance').sum(), 
            pl.col('Balance_1_30d').sum(),
            pl.col('Balance_31_60d').sum(),
            pl.col('Balance_61_90d').sum(),
            pl.col('Balance_90d').sum(),
            pl.col('TotalBalance').sum()
        )
        aggregate_data_snapshot = aggregate_data.with_columns(pl.col('LastChecked').alias('Timestamp')).drop('LastChecked')
        return aggregate_data, aggregate_data_snapshot