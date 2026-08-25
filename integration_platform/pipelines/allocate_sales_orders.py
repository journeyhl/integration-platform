from integration_platform.pipelines import Pipeline
from integration_platform.connectors import AcumaticaAPI
from integration_platform.transform.manage_sales_allocations import Transform

from integration_platform.connectors.sql import SQLConnector, AcumaticaDbQueries



class AllocateSalesOrders(Pipeline):
    def __init__(self, function: str, env: str='prod'):
        # function = 'allocate_sales_orders'
        super().__init__(pipeline_name='allocate-sales-orders', function=function, env=env)
        self.acudb: SQLConnector[AcumaticaDbQueries] = SQLConnector(
            pipeline=self, database_name='AcudevDb' if env == 'dev' else 'AcumaticaDb'
        )
        # self.acudb: SQLConnector[AcumaticaDbQueries] = SQLConnector(pipeline=self, database_name='AcumaticaDb')
        # self.acudev: SQLConnector[AcumaticaDbQueries] = SQLConnector(pipeline=self, database_name='AcudevDb')
        self.acu_api = AcumaticaAPI(self, env=env)
        self.transformer = Transform(self)

    def extract(self):
        order_extract = self.acudb.query_to_dataframe(self.acudb.queries.AllocateSalesOrders)
        sync_history_extract = self.acudb.query_to_dataframe(self.acudb.queries.ProductSyncHistory)
        data_extract = {
            'order_extract': order_extract,
            'sync_history_extract': sync_history_extract
        }
        return data_extract

    def transform(self, data_extract):
        data_transformed = self.transformer.transform(data_extract)
        return data_transformed
    
    def load(self, data_transformed):
        data_loaded = data_transformed
        return data_loaded
    
    def log_results(self, data_loaded):
        pass