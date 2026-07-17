from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.acu_to_dbc_b2b_collections import AcuToDbcB2BCollections
import logging
import polars as pl

class Transform:

    def __init__(self, pipeline: AcuToDbcB2BCollections):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.transform')
        pass


    def landing(self, data_extract: pl.DataFrame):
        #.with_columns(pl.lit(datetime.now(ZoneInfo('America/New_York')), pl.Datetime).alias('LastChecked'))
        bp = 'here'
        

        group_by_columns = [
            'CustomerID', 
            'CustomerName',
            'SalespersonID',
            'TermsID',
            'CustomerStatus',
            'State',
            'Email',
            'Phone'
        ]
        collections_detail = data_extract.group_by(group_by_columns, maintain_order=True).agg(
            pl.col('CurrentBalance').sum(), 
            pl.col('Balance_1_30d').sum(),
            pl.col('Balance_31_60d').sum(),
            pl.col('Balance_61_90d').sum(),
            pl.col('Balance_90d').sum(),
            pl.col('TotalBalance').sum()
        )
        self.pipeline.centralstore.__dataframe_to_table_create_statement__(collections_detail)
        bp = 'here'
        test = collections_detail.to_dicts()
        bp = 'here'
        # df_transformed = data_extract.group_by(group_by_columns, maintain_order=True).agg(
        #     pl.col('VendorPartNumber').drop_nulls().unique(maintain_order=True).str.join(', ')
        # )
        # data_transformed = df_transformed.to_dicts()
        data_transformed = data_extract
        return data_transformed
