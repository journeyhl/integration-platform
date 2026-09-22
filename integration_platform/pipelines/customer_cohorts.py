

from integration_platform.pipelines import Pipeline
from integration_platform.connectors import AcumaticaAPI
from integration_platform.transform.b2b_cohorts import Transform
import polars as pl
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from integration_platform.connectors.sql import SQLConnector, AcumaticaDbQueries
from typing import Literal
class CustomerCohorts(Pipeline):
    ''':class:`~integration_platform.pipelines.customer_cohorts.CustomerCohorts`
    ---
    <hr>

    '''
    def __init__(self, function: str, b2b_d2c: Literal['B2B', 'D2C', 'Both'], env: str='prod'):
        super().__init__('Cohorts', function=function, env=env)
        self.acudb: SQLConnector[AcumaticaDbQueries] = SQLConnector(
            pipeline=self, database_name='AcudevDb' if env == 'dev' else 'AcumaticaDb'
        )
        self.b2b_d2c = b2b_d2c
        self.transformer = Transform(self)
        if b2b_d2c == 'B2B':
            self.extract_query = self.centralstore.queries.B2BCohorts_OrderHistory
        elif b2b_d2c == 'D2C':
            self.extract_query = self.centralstore.queries.D2CCohorts_OrderHistory
        else:
            self.b2b_d2c = ''
            self.extract_query = self.centralstore.queries.Cohorts_OrderHistory


    def extract(self) -> dict[str, list[dict]]:
        order_history = self.centralstore.query_to_dataframe(self.extract_query).to_dicts()
        data_extract = {
            'customer_order_history': order_history,
        }
        return data_extract

    def transform(self, data_extract: dict[str, list[dict]]):
        customers_with_cohort = self.transformer.landing(data_extract)
        data_transformed = {
            'customer_order_history': data_extract['customer_order_history'],
            'customer_cohorts': customers_with_cohort
        }

        return data_transformed
    
    def load(self, data_transformed):
        order_history = data_transformed['customer_order_history']
        cohorts = data_transformed['customer_cohorts']
        self.ts_load =  datetime.now(ZoneInfo('America/New_York'))
        self._load_order_history_(order_history=order_history)
        self._load_cohorts_(cohorts=cohorts)

        return data_transformed

    def _load_order_history_(self, order_history: list[dict]):
        order_history = self.default_loader.add_to_list(ldata=order_history, additions={'InsertedDT': self.ts_load, 'LastChecked': self.ts_load})
        self.centralstore.merge_table_paginated(table_name=f'analytics.JHL_{self.b2b_d2c}CustomerOrderHistory', data=order_history, page_size=500)
        self.logger.info('Order history load complete!')
        bp = 'here'
        
    
    def _load_cohorts_(self, cohorts: list[dict]):
        cohorts = self.default_loader.add_to_list(ldata=cohorts, additions={'InsertedDT': self.ts_load, 'LastChecked': self.ts_load})
        cohort_snapshot = self.default_loader.add_to_list(ldata=cohorts, additions={'Timestamp': self.ts_load})
        self.centralstore.merge_table_paginated(table_name=f'analytics.JHL_{self.b2b_d2c}CustomerCohorts', data=cohorts, page_size= 750)
        self.centralstore.merge_table_paginated(table_name=f'analytics.JHL_{self.b2b_d2c}CustomerCohort_Snapshot', data=cohort_snapshot, page_size= 750)
        self.logger.info(f'Cohort load complete!')
    
    def log_results(self, data_loaded):
        pass
