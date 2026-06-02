
from typing import Any

from pipelines import Pipeline
from connectors import RedStagAPI, AcumaticaAPI
from transform.redstag_order_search import Transform
from transform import redstag_send



class RedStagOrderSearch(Pipeline):
    '''`RedStagOrderSearch`(Pipeline)
    ---
    <hr>

    Pipeline to retrieve inventory levels from RedStag 3PL through their API and load to db_CentralStore (**RedstagInventorySummary** and **RedstagInventoryDetail**)
    
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
        super().__init__('redstag-order-search', function)
        self.transformer = Transform(self)
        self.transformer2 = redstag_send.Transform(self)
        self.redstag = RedStagAPI(self)
        # self.acu_api = AcumaticaAPI(self)
        self.payload_target = [
            "inventory.detailed",
            [
                None, #Specific SKUS
                None  #Updated Since value. If populated, will only return values updated since that date.
            ]
        ]
        # self.loader = Load(self)

    def extract(self):
        base_extract = self.acudb.query_to_dataframe(self.acudb.queries.RedstagOrderSearch)
        distinct_extract = base_extract.sql('select distinct ShipmentNbr from self').to_dicts()
        data_extract = {
            'base_extract': base_extract.to_dicts(),
            'distinct_extract': distinct_extract
        }
        # data_extract = self.redstag.target_api(payload_target=self.payload_target, operation='inventory.detailed')
        return data_extract

    def transform(self, data_extract):
        data_transformed = []
        data_transformed = self.transformer.transform(data_extract)
        bp = 'here'
        return data_transformed
    
    def load(self, data_transformed):
        summary = data_transformed['item_summary']
        # self.centralstore.checked_upsert(table_name='RedstagInventorySummary', data=summary)
        # detail = data_transformed['item_detail']
        # self.centralstore.checked_upsert(table_name='RedstagInventoryDetail', data=detail)
        
        return data_transformed
    
    def log_results(self, data_loaded):
        pass

    def run_as_extract(self):
        data_extract = self.extract()
        data_transformed = self.transform(data_extract)
        return data_transformed