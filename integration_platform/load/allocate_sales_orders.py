from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.allocate_sales_orders import AllocateSalesOrders
import logging
import time





class Load:
    def __init__(self, pipeline: AllocateSalesOrders):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.Load')
        pass



    def landing(self, data_transformed: dict):
        bp = 'here'
        put_on_hold = []
        orders = data_transformed['orders']
        successful_allocations = self.allocate_orders(orders)
        order_item_sync_history = data_transformed['order_item_sync_history']

        bp = 'here'

    def allocate_orders(self, orders: list[dict]):
        successful_allocations = []
        for i, row in enumerate(orders):
            if row['QtyAvail'] in [None, 0]:
                self.logger.warning(f'No units of {row['InventoryCD']} available to allocate to {row['OrderNbr']}!')
                continue
            success = self.pipeline.acu_api.manage_sales_allocations(order_data=row)
            if success:
                bp = 'here'
                successful_allocations.append(row)
        bp = 'here'
        return successful_allocations





