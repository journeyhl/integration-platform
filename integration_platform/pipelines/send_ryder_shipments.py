from integration_platform.pipelines import Pipeline
from integration_platform.connectors import RyderAPI, AcumaticaAPI
from integration_platform.transform.ryder_send import Transform
# from integration_platform.load.load_ryder_send import Load
import json

from integration_platform.connectors.sql import SQLConnector, AcumaticaDbQueries
class SendRyderShipments(Pipeline):
    
    def __init__(self, function: str, env: str='prod'):
        super().__init__(pipeline_name='ryder-send-shipments', function=function, env=env)
        self.acudb: SQLConnector[AcumaticaDbQueries] = SQLConnector(
            pipeline=self, database_name='AcudevDb' if env == 'dev' else 'AcumaticaDb'
        )
        self.transformer = Transform(self)
        self.ryder = RyderAPI(self)
        self.acu_api = AcumaticaAPI(self)
        # self.loader = Load(self)

    def extract(self):
        data_extract = self.acudb.query_to_dataframe(query=self.acudb.queries.SendRyderShipments)
        return data_extract
    
    def transform(self, data_extract):
        data_transformed = self.transformer.landing(data_extract)
        return data_transformed
    

    def load(self, data_transformed):
        data_loaded = {}
        return data_loaded
    
    def log_results(self, data_loaded):
        self.acu_api._logout_()

        self.logger.info(f'Logging acu_api interactions...')
        pass



