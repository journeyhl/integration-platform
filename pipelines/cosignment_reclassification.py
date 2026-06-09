from pipelines import Pipeline
from connectors import AcumaticaAPI
from transform.consignment_reclassification import Transform




class ConsignmentReclassification(Pipeline):
    def __init__(self, function: str, env: str='prod'):
        # function = 'consignment_reclassifications'
        super().__init__(pipeline_name='consignment-reclassifications', function=function, env=env)
        self.acu_api = AcumaticaAPI(self, env=env)
        self.transformer = Transform(self)

    def extract(self):
        data_extract = self.acudb.query_to_dataframe(self.acudb.queries.CosignmentReclassification)
        return data_extract

    def transform(self, data_extract):
        data_transformed = self.transformer.transform(data_extract)
        return data_transformed
    
    def load(self, data_transformed):
        data_loaded = data_transformed
        return data_loaded
    
    def log_results(self, data_loaded):
        pass