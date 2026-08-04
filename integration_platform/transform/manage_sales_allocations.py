from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines import AllocateSalesOrders
import logging
import polars as pl

class Transform:
    def __init__(self, pipeline: AllocateSalesOrders):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.Transform')
        pass
    
    def transform(self, data_extract: dict[str, pl.DataFrame]):
        self._set_context_(data_extract)
        order_item_sync_history = self.items_on_orders()
        bp = 'here'
        data_transformed = {
            'orders': self.orders,
            'order_item_sync_history': order_item_sync_history
        }
        return data_transformed

    def _set_context_(self, data_extract: dict[str, pl.DataFrame]):
        self.logger.info(f'Setting context (self.orders and self.tables)...')
        self.orders = data_extract['order_extract'].to_dicts()
        self.tables = pl.SQLContext(
            Orders = data_extract['order_extract'],
            SyncHistory = data_extract['sync_history_extract']
        )

    def items_on_orders(self):
        self.logger.info(f'Querying distinct items found in order extract, then retrieving sync records for each...')
        df_order_items_sync_history = self.tables.execute(
            query=f"""
        with TopLevel as(
            select distinct InventoryCD, Descr
            from Orders
        )
        select s.SyncID
             , s.EntityType
             , s.Entity
             , s.InventoryCD
             , s.ExternID
             , s.PendingSync
             , s.Status
             , s.LastOperation
             , s.Deleted
             , s.SyncInProcess
             , s.AttemptCount
             , s.HasSyncDetailRecord
             , s.ExternDescription
             , t.Descr
             , s.acuStatus
             , s.LocalID
             , s.NoteID
             , s.LocalTS
             , s.LastOperationTS
        from SyncHistory s
        inner join TopLevel t on s.InventoryCD = t.InventoryCD
"""
        ).collect()

        self.tables.register(name='ItemsOnOrders', frame=df_order_items_sync_history)
        self.logger.info(f'ItemsOnOrders registered with {df_order_items_sync_history.height} rows.')
        order_items_sync_history = df_order_items_sync_history.to_dicts()
        return order_items_sync_history



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