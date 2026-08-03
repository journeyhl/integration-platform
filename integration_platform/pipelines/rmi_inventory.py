
from typing import Any
from integration_platform.pipelines import Pipeline
from integration_platform.connectors import RMIAPI
from integration_platform.transform.rmi_inventory import Transform
from datetime import datetime
from zoneinfo import ZoneInfo


class RMIInventory(Pipeline):
    '''`RMIInventory`(Pipeline)
    ---
    <hr>

    Pipeline to retrieve inventory details from RMI and load to CentralStore

    # Extraction
     - Extracts detailed inventory data from RedStag via :class:`~connectors.redstag_api.RedStagAPI`.:meth:`~connectors.redstag_api.RedStagAPI.target_api`

    # Transformation
     - Transforms response from RedStag to a dictionary containing two lists of dicts for upsert to **RedstagInventorySummary** and **RedstagInventoryDetail**

    # Load
     - Loads Inventory Summary and Detail level data to **RedstagInventorySummary** and **RedstagInventoryDetail** via :class:`~connectors.sql.SQLConnector`.:meth:`~connectors.sql.SQLConnector.checked_upsert`
     
    # Results Logging
     - None needed
    '''

    def __init__(self, function: str):
        super().__init__('redstag-inventory', function)
        self.transformer = Transform(self)
        self.rmi = RMIAPI(self)

    def extract(self):
        data_extract ={
            'inv_facility': self.rmi.get_inventory_data(url=self.rmi.ep_inventory_by_facility),
            'inv_location': self.rmi.get_inventory_data(url=self.rmi.ep_inventory_by_location),
            'inv_serials': self.rmi.get_inventory_data(url=self.rmi.ep_inventory_with_serials),
        }
        self.ts_extract = datetime.now(ZoneInfo('America/New_York'))
        return data_extract

    def transform(self, data_extract):
        data_transformed = self.transformer.landing(data_extract)
        return data_transformed
    
    def load(self, data_transformed):
        summary = self.default_loader.add_InsertedDT_to_list(data_transformed['inv.RMI_Summary'])
        detail = self.default_loader.add_InsertedDT_to_list(data_transformed['inv.RMI_Detail'])
        self.centralstore.checked_upsert_paginated(table_name='inv.RMI_Summary', data=summary)
        self.centralstore.checked_upsert_paginated(table_name='inv.RMI_Detail', data=detail)

        summary_snapshot = data_transformed['inv.RMI_SummarySnapshot']
        detail_snapshot = data_transformed['inv.RMI_DetailSnapshot']

        self.centralstore.insert_df(df_data_loaded=summary_snapshot, table_name='inv.RMI_SummarySnapshot')
        self.centralstore.insert_df(df_data_loaded=detail_snapshot, table_name='inv.RMI_DetailSnapshot')

        
        return data_transformed
    
    def log_results(self, data_loaded):
        pass
