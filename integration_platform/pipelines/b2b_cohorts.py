

from integration_platform.pipelines import Pipeline
from integration_platform.connectors import AcumaticaAPI
from integration_platform.transform.b2b_cohorts import Transform
import polars as pl
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from integration_platform.connectors.sql import SQLConnector, AcumaticaDbQueries

class B2BCohorts(Pipeline):
    '''`B2BCohorts`(Pipeline)
    ---
    <hr>

    Gets all ____ and upserts to **acu.TrialBalance**

    '''
    def __init__(self, function: str, env: str='prod'):
        super().__init__('acu-to-dbc-trial-balance', function=function, env=env)
        self.acudb: SQLConnector[AcumaticaDbQueries] = SQLConnector(
            pipeline=self, database_name='AcudevDb' if env == 'dev' else 'AcumaticaDb'
        )
        self.transformer = Transform(self)


    def extract(self) -> dict[str, pl.DataFrame]:
        order_history = self.centralstore.query_to_dataframe(self.centralstore.queries.B2BCohorts_OrderHistory)
        data_extract = {
            'order_history': order_history,
        }
        return data_extract

    def transform(self, data_extract: dict[str, pl.DataFrame]):
        customers_with_cohort = self.transformer.landing(data_extract)
        return customers_with_cohort
    
    def load(self, data_transformed: list[dict]):
        now =  datetime.now(ZoneInfo('America/New_York'))
        b2b_customer_cohorts = self.default_loader.add_to_list(data_transformed, {'InsertedDT': now, 'LastChecked': now})
        b2b_customer_cohort_snapshot = self.default_loader.add_to_list(data_transformed, {'Timestamp': now})
        self.centralstore.checked_upsert_paginated('analytics.JHL_B2BCustomerCohorts', data_transformed, page_size= 100)
        self.centralstore.checked_upsert_paginated('analytics.JHL_B2BCustomerCohort_Snapshot', data_transformed, page_size= 100)
        return data_transformed
    
    def log_results(self, data_loaded):
        pass
