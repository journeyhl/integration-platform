from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pipelines import ConsignmentReclassification
import logging
import polars as pl

class Transform:
    def __init__(self, pipeline: ConsignmentReclassification):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.transform')
        pass
    
    def transform(self, data_extract: pl.DataFrame):
        summarized_extract = data_extract.sql('''
select distinct Module
	 , BatchType
	 , JournalStatus
	 , BatchNbr
	 , InvRefNbr
	 , TranDate
	 , InvRef_OrderNbr OrderNbr
	 , InvRef_OrderLineNbr OrderLineNbr
	 , InvRef_ShipmentNbr ShipmentNbr
	 , InvRef_ShipmentLineNbr ShipmentLineNbr
	 , InvRef_UnitPrice
	 , InvRef_Qty
	 , InvRef_UnitCost
	 , InvRef_TranTotalPrice
from self
''') #I may not need...Adding AccountCD = 5000 to where limited to same number of rows as header level select

#also...For posterity, to filter out stuff that that will have already been reclassified, i should query GLTran. Match on the RefNbr and OrigBatchNbr
        bp = 'here'
        for row in data_extract.iter_rows(named=True):
            self.pipeline.acu_api.reclassify_transaction(cogs_entry=row)
            bp = 'here'
        bp = 'here'
