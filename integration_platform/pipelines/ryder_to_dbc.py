from integration_platform.pipelines import Pipeline
from integration_platform.connectors.sql import SQLConnector, AcumaticaDbQueries
from integration_platform.connectors.ryder_api import RyderAPI
from integration_platform.transform.ryder_to_dbc_v3 import Transform
from integration_platform.load.ryder_to_dbc import Load
import polars as pl
from pathlib import Path
import json
from datetime import datetime
from zoneinfo import ZoneInfo
class RyderToDbc(Pipeline):
    def __init__(self, function: str, env: str='prod'):
        super().__init__(pipeline_name='ryder-to-dbc', function=function, env=env)
        self.acudb: SQLConnector[AcumaticaDbQueries] = SQLConnector(
            pipeline=self, database_name='AcudevDb' if env == 'dev' else 'AcumaticaDb'
        )
        self.ryder = RyderAPI(self, env=env)
        self.transformer = Transform(self)
        self.loader = Load(pipeline=self)

    def extract(self):
        #'087276', '087442', '087353'
        orders = ['087997', ]#'087575', '087465', '087449', '087509', '087479', '087451', '087733', '087647', '087646']

        orders = self.acudb.query_to_dataframe(query=self.acudb.queries.RyderToDbc).to_dicts()
        # orders = ['088077','088077','088025','088010','088004','088004','087927','087923','087943','087921','088027','087846','087834','088123','088123','087736','087738','087738','087733','087732','087718','088326','087711','087693','087688','087667','087647','087646','087645','087709','087593','087509','087509','087479','087478','087541','087465','087451','087442','087353','087301','087299','087290','087276','087276','087246','087924','087210','087203','087203','087194','087147','087147','087141','087090','087090','087195','087029','086997','086981','088048','086929','086918','086918','086914','086914','086910','086910','086906','086904','086902','086882','086866','086819','086808','086772','086720','086698','086698','086635','086635','086611','086545','086569','086569','086531','086530','086817','086529','086498','086481','086450','086816','087125','086438','086355','086345','086333','086333','086233','086233','086233','086202','086194','086194','086190','086064','086827','085561','085079','086107','086106','084894','084893','086105','085338',]
        total = len(orders)
        data_extract = {}
        for i, order in enumerate(orders):
            order_nbr = order['ShipmentNbr']
            log_prefix = f'{order_nbr}, {i+1}/{total}: '
            extract_time = datetime.now(ZoneInfo('America/New_York'))
            order_history = self.ryder.get_order_history(shipment_nbr=order_nbr, log_prefix=log_prefix)
            order_milestones = self.ryder.get_order_milestones(shipment_nbr=order_nbr, log_prefix=log_prefix)
            # if order_history.get('error') == None:
            data_extract[order_nbr] = {
                'history': order_history,
                'milestones': order_milestones,
                'extract_time': extract_time
            }
            bp = 'here'
        return data_extract

    def transform(self, data_extract: dict):
        data_transformed = self.transformer.landing(data_extract=data_extract)       
        return data_transformed
    
    def load(self, data_transformed: dict):
        data_sql_fmt = self.loader.landing_format_for_sql(data_transformed=data_transformed)
        for table, data in data_sql_fmt.items():
            self.centralstore.checked_upsert_paginated(table_name=table, data=data)

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