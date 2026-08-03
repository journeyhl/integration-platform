from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.rmi_inventory import RMIInventory
import logging
import json
import polars as pl

class Transform:
    def __init__(self, pipeline: RMIInventory):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.Transform')
        pass

    def landing(self, data_extract: dict[str, list]):
        bp = 'here'
        self.parse_facility(inventory_by_facility=data_extract['inv_facility'])
        self.location_data = self.parse_location(inventory_by_location=data_extract['inv_location'])
        self.serial_data = self.parse_serials(inventory_with_serials=data_extract['inv_serials'])
        self._join_location_serials_()
        self._snapshot_to_dataframe_()

        data_transformed = {
            'inv.RMI_Summary': self.summary,
            'inv.RMI_SummarySnapshot': self.df_summary_snapshot,
            'inv.RMI_Detail': self.detail,
            'inv.RMI_DetailSnapshot': self.df_detail_snapshot
        }
        return data_transformed


    def _join_location_serials_(self):
        df_location = pl.DataFrame(self.location_data, infer_schema_length=None)
        df_serial = pl.DataFrame(self.serial_data, infer_schema_length=None)
        df_detail = df_location.join(df_serial, how='left', on=['Location', 'InventoryCD'], suffix='_').select(['Location', 'InventoryCD', 'Qty', 'Serials', 'Timestamp', 'LastChecked'])

        self.detail = df_detail.to_dicts()
        self.detail_snapshot = df_detail.drop('LastChecked').to_dicts()


    def _snapshot_to_dataframe_(self):
        self.df_summary_snapshot = pl.DataFrame(data=self.summary_snapshot, infer_schema_length=None)
        self.df_detail_snapshot = pl.DataFrame(data=self.detail_snapshot, infer_schema_length=None)
        bp = 'here'




    def parse_facility(self, inventory_by_facility: list):
        ''':class:`~Transform`.:meth:`~parse_facility` (self, inventory_by_facility: *list*, ):
        ---
        <hr>
        
        Given a list of Inventory by Facility data from RMI, format for SQL. Facility will always be RMI, so dropping from the transformed dataset
        
        ### Upstream Calls 
         #### :class:`~integration_platform.transform.rmi_inventory.Transform`.:meth:`~integration_platform.transform.rmi_inventory.Transform.landing`
            
        <hr>
        
        Parameters
        ---
        :param (*list*) `inventory_by_facility`: list of all inventory items at RMI with each's aggregated quantity
        
        <hr>
        
        Sets
        ---
         - #### :class:`~integration_platform.transform.rmi_inventory.Transform`.:attr:`~integration_platform.transform.rmi_inventory.Transform.summary_data`
            - list of aggregated RMI inventory data to be upserted to SQL
        '''        
        self.summary = []
        self.summary_snapshot = []
        for row in inventory_by_facility:
            self.summary.append(
                {
                    'InventoryCD': row['itemNumber'],
                    'Qty': row['quantity'],
                    'LastChecked': self.pipeline.ts_extract
                }
            )
            self.summary_snapshot.append(
                {
                    'InventoryCD': row['itemNumber'],
                    'Qty': row['quantity'],
                    'Timestamp': self.pipeline.ts_extract
                }
            )



    def parse_location(self, inventory_by_location: list):
        ''':class:`~Transform`.:meth:`~parse_location` (self, inventory_by_location: *list*):
        ---
        <hr>
        
        Given a list of Inventory by Location data from RMI, format for SQL. 
        
        May have multiple rows for some items depending on how many distinct locations it can be found

        ### Upstream Calls 
         #### _______replace_me_______
            - Description
         #### _______replace_me_______
            - Description
            
        <hr>
        
        Parameters
        ---
        :param (*list*) `inventory_by_location`: List of inventory items by specific location at RMI
        
        <hr>
        
        Returns
        ---
        :return `transformed_location` (_list_): list of RMI inventory data by specific location
        '''
        transformed_location = [
            {
                'Location': row['location'],
                'InventoryCD': row['itemNumber'],
                'Qty': row['quantity'],
                'Timestamp': self.pipeline.ts_extract,
                'LastChecked': self.pipeline.ts_extract,
            }
        for row in inventory_by_location
        ]
        return transformed_location



    def parse_serials(self, inventory_with_serials: list):
        ''':class:`~Transform`.:meth:`~parse_serials` (self, inventory_with_serials: *list*, ):
        ---
        <hr>
        
        Given a list of Inventory by Location data of Serialized items from RMI, format for SQL
        
        ### Downstream Calls 
         #### _______replace_me_______
            - Description
         #### _______replace_me_______
            - Description
        
        ### Upstream Calls 
         #### _______replace_me_______
            - Description
         #### _______replace_me_______
            - Description
            
        <hr>
        
        Parameters
        ---
        :param (*list*) `inventory_with_serials`: List of inventory items by specific location at RMI with serial numbers of items included
        
        <hr>
        
        Returns
        ---
        :return `transformed_serials` (_list_): _description_
        '''        
        transformed_serials = []
        transformed_serials = [
            {
                'Location': row['location'],
                'InventoryCD': row['itemNumber'],
                'Qty': row['quantity'],
                'Serials': json.dumps(row['serials']),
            }
        for row in inventory_with_serials
        ]
        return transformed_serials