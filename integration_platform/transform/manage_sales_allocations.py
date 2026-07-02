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
        bp = 'here'
        for row in data_extract.iter_rows(named=True):
            if row['QtyAvail'] in [None, 0]:
                self.logger.warning(f'No units of {row['InventoryCD']} available to allocate to {row['OrderNbr']}!')
                continue
            self.pipeline.acu_api.manage_sales_allocations(order_data=row)
            bp = 'here'
        bp = 'here'




    # def transform(self, data_extract: pl.DataFrame):
    #     bp = 'here'
    #     item_levels = {}
    #     for row in data_extract.iter_rows(named=True):
    #         if item_levels.get(row['InventoryCD']) == None:
    #             item_levels[row['InventoryCD']] = row['QtyAvail']
    #         if row['QtyAvail'] in [None, 0] or item_levels[row['InventoryCD']] == 0:
    #             self.logger.warning(f'No units of {row['InventoryCD']} available to allocate to {row['OrderNbr']}!')
    #             continue
    #         self.pipeline.acu_api.manage_sales_allocations(order_data=row)
    #         item_levels[row['InventoryCD']] = row['QtyAvail'] - row['QtyOrdered'] if row['QtyAvail'] != 0 else 0
    #         bp = 'here'
    #     bp = 'here'