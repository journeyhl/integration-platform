from integration_platform.pipelines import Pipeline
from integration_platform.connectors.ryder_api import RyderAPI
from integration_platform.transform.ryder_to_dbc import Transform
import polars as pl
from pathlib import Path
import json

class RyderToDbc(Pipeline):
    def __init__(self, function: str, env: str='prod'):
        super().__init__(pipeline_name='ryder-to-dbc', function=function, env=env)
        self.ryder = RyderAPI(self, env=env)
        self.transformer = Transform(self)
        # self.loader = AcuAPILoader(self)

    def extract(self):
        test_files = list(Path(r'C:\Users\jordanj\Desktop\Ryder').iterdir())
        data_extract = []
        for file in test_files:
            with open(file, 'r') as f:
                contents = f.read()
            jfile = json.loads(contents)
            data_extract.append(jfile)
        return data_extract

    def transform(self, data_extract :pl.DataFrame):
        # data_transformed = self.transformer.transform(data_extract)
        status_groups = data_extract.sql('select Status, count(distinct OrderNbr) OrderCount from self group by Status').to_dicts()
        extract_dicts = data_extract.to_dicts()
        data_transformed = {sg['Status']: {'OrderCount': sg['OrderCount'], 'Orders': [ex for ex in extract_dicts if ex['Status'] == sg['Status']]} for sg in status_groups}
       
        return data_transformed
    
    def load(self, data_transformed):
        return data_transformed
    
    def log_results(self, data_loaded):
        pass