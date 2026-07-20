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
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.transform')
        pass


    def landing(self, data_extract: pl.DataFrame):
        #.with_columns(pl.lit(datetime.now(ZoneInfo('America/New_York')), pl.Datetime).alias('LastChecked'))
        bp = 'here'
        data_extract = data_extract.with_columns(pl.lit(datetime.now(ZoneInfo('America/New_York')), pl.Datetime).alias('LastChecked'))
        self.data_extract = data_extract
        collections_summary, collections_summary_snapshot = self._get_summary_data_()
        balance_by_status = self._aggregate_by_metric_(group_by_columns=['CustomerStatus'])
        balance_by_salesrep = self._aggregate_by_metric_(group_by_columns=['SalespersonID'])
        # df_transformed = data_extract.group_by(group_by_columns, maintain_order=True).agg(
        #     pl.col('VendorPartNumber').drop_nulls().unique(maintain_order=True).str.join(', ')
        # )
        # self.pipeline.centralstore.__dataframe_to_table_create_statement__(data_extract)
        # self.pipeline.centralstore.__dataframe_to_table_create_statement__(collections_summary)
        data_transformed = {
            'detail': data_extract,
            'summary': collections_summary,
            'summary_snapshot': collections_summary_snapshot,
            'balance_by_status': balance_by_status,
            'balance_by_salesrep': balance_by_salesrep,
        }
        return data_transformed



    def _get_summary_data_(self):
        group_by_columns = [
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
        collections_summary = self.data_extract.group_by(group_by_columns, maintain_order=True).agg(
            pl.col('CurrentBalance').sum(), 
            pl.col('Balance_1_30d').sum(),
            pl.col('Balance_31_60d').sum(),
            pl.col('Balance_61_90d').sum(),
            pl.col('Balance_90d').sum(),
            pl.col('TotalBalance').sum()
        )
        collections_summary_snapshot = collections_summary.with_columns(pl.col('LastChecked').alias('Timestamp')).drop('LastChecked')
        return collections_summary, collections_summary_snapshot
    
    def _aggregate_by_metric_(self, group_by_columns: list = []):
        aggregate_data = self.data_extract.group_by(group_by_columns, maintain_order=True).agg(
            pl.col('CurrentBalance').sum(), 
            pl.col('Balance_1_30d').sum(),
            pl.col('Balance_31_60d').sum(),
            pl.col('Balance_61_90d').sum(),
            pl.col('Balance_90d').sum(),
            pl.col('TotalBalance').sum()

        ).with_columns(pl.lit(datetime.now(ZoneInfo('America/New_York')), pl.Datetime).alias('LastChecked'))
        return aggregate_data