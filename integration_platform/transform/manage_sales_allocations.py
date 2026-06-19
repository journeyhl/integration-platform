from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines import AllocateSalesOrders
import logging
import polars as pl

class Transform:
    def __init__(self, pipeline: AllocateSalesOrders):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.transform')
        pass
    
    def transform(self, data_extract: pl.DataFrame):
        summarized_extract = data_extract.sql('''
select distinct OrderType
			  , OrderNbr
			  , SiteCD
from self
''') #I may not need...Adding AccountCD = 5000 to where limited to same number of rows as header level select

#also...For posterity, to filter out stuff that that will have already been reclassified, i should query GLTran. Match on the RefNbr and OrigBatchNbr
        bp = 'here'
        for row in data_extract.iter_rows(named=True):
            self.pipeline.acu_api.manage_sales_allocations(order_data=row)
            bp = 'here'
        bp = 'here'
