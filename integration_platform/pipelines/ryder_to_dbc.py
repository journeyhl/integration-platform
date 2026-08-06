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
        orders = ['087465', '087449', '087353', '087442']
        data_extract = {}
        for order in orders:
            order_history = self.ryder.get_order_history(shipment_nbr=order)
            order_milestones = self.ryder.get_order_milestones(shipment_nbr=order)
            # if order_history.get('error') == None:
            data_extract[order] = {
                'history': order_history,
                'milestones': order_milestones
            }
            bp = 'here'
        return data_extract

    def transform(self, data_extract: dict):
        data_transformed = self.transformer.landing(data_extract=data_extract)       
        return data_transformed
    
    def load(self, data_transformed):
        return data_transformed
    
    def log_results(self, data_loaded):
        pass



    def testing_extract(self):        
        test_files = list(Path(r'C:\Users\derfj\Desktop\Ryder').iterdir())
        data_extract = []
        for file in test_files:
            with open(file, 'r') as f:
                contents = f.read()
            jfile = json.loads(contents)
            data_extract.append(jfile)
        return data_extract