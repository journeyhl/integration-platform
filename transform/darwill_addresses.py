from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pipelines.darwill_addresses import DarwillAddresses
import logging
import polars as pl

class Transform:
    def __init__(self, pipeline: DarwillAddresses):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.transform')
        pass
    
    def transform(self, data_extract: pl.DataFrame):
        bp = 'here'
        ex_dicts = data_extract.to_dicts()
        data_extract = data_extract.with_columns(
            pl.col('ANI').alias('UnformattedANI'),
            pl.col('product').alias('Product')
        )
        for row in data_extract.iter_rows(named=True):
            return_nbr = row['KeyValue']
            bp = 'here'