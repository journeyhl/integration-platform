from polars.io.avro import read_avro

from integration_platform.pipelines import Pipeline
from integration_platform.connectors import AcumaticaAPI
from integration_platform.load.acu_api_loader import AcuAPILoader
import polars as pl



class ShipChairRemovalSeparate(Pipeline):
    def __init__(self, function: str, env: str='prod'):
        # function = 'ship_chair_removal_separate'
        super().__init__(pipeline_name='ship-chair-removal-separate', function=function, env=env)
        self.acu_api = AcumaticaAPI(self, env=env)
        self.loader = AcuAPILoader(self)

    def extract(self) -> pl.DataFrame:
        data_extract = self.acudb.query_to_dataframe(self.acudb.queries.ShipChairRemovalSeparate)
        return data_extract

    def transform(self, data_extract :pl.DataFrame):
        # data_transformed = self.transformer.transform(data_extract)
        status_groups = data_extract.sql('select Status, count(distinct OrderNbr) OrderCount from self group by Status').to_dicts()
        extract_dicts = data_extract.to_dicts()
        data_transformed = {sg['Status']: {'OrderCount': sg['OrderCount'], 'Orders': [ex for ex in extract_dicts if ex['Status'] == sg['Status']]} for sg in status_groups}
       
        return data_transformed
    
    def load(self, data_transformed):
        data_loaded = self.loader.landing_ship_chair_removal_separate(data_transformed)
        return data_loaded
    
    def log_results(self, data_loaded):
        pass