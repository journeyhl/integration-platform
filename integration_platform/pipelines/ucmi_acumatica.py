from integration_platform.pipelines import Pipeline
from integration_platform.connectors.sql import SQLConnector, AcumaticaDbQueries



class UCMI_AcumaticaCustomers(Pipeline):
    def __init__(self, function: str, env: str='prod'):
        super().__init__(pipeline_name='ucmi-acumatica-customers', function=function, env=env)
        self.acudb: SQLConnector[AcumaticaDbQueries] = SQLConnector(
            pipeline=self, database_name='AcudevDb' if env == 'dev' else 'AcumaticaDb'
        )

    def extract(self):
        data_extract = {}
        return data_extract

    def transform(self, data_extract):
        data_transformed = {}
       
        return data_transformed
    
    def load(self, data_transformed):
        data_loaded = {}
        return data_loaded
    
    def log_results(self, data_loaded):
        pass