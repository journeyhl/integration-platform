from pipelines import Pipeline
from connectors import AcumaticaAPI
import polars as pl
import time



class CreateAcuShipment(Pipeline):
    def __init__(self, function: str, env: str='prod'):
        # function = 'consignment_reclassifications'
        super().__init__(pipeline_name='create-shipments', function=function, env=env)
        self.acu_api = AcumaticaAPI(self, env=env)

    def extract(self):
        data_extract = self.acudb.query_to_dataframe(self.acudb.queries.CreateShipments)
        return data_extract

    def transform(self, data_extract: pl.DataFrame):
        data_transformed = data_extract.to_dicts()
        return data_transformed
    
    def load(self, data_transformed):
        for i, order in enumerate(data_transformed):
            order['properties'] = {
                "WarehouseID": {"value": order['Warehouse']}
            }
            if order['OrderShippableLines'] > 1:
                self.logger.info(f'Order has multiple warehouses, sleeping 10 seconds then creating next shipment for order.')
                time.sleep(10)
            self.acu_api.order_create_shipment(order_data=order)
            bp = 'here'
        data_loaded = data_transformed
        return data_loaded
    
    def log_results(self, data_loaded):
        pass