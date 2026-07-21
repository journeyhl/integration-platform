
from integration_platform.pipelines.base import Pipeline
from integration_platform.transform.acu_to_dbc_b2b_collections import Transform
from datetime import datetime
from zoneinfo import ZoneInfo
import polars as pl
class AcuToDbcB2BCollections(Pipeline):
    def __init__(self, function):
        super().__init__('acu-to-dbc-b2b-collections', function)
        self.transformer = Transform(self)

    def extract(self) -> pl.DataFrame:
        data_extract = self.acudb.query_to_dataframe(query=self.acudb.queries.AcuToDbc_B2BCollections)
        return data_extract
    

    def transform(self, data_extract) -> dict[str, pl.DataFrame]:
        data_transformed = self.transformer.landing(data_extract)
        return data_transformed
    

    def load(self, data_transformed: dict[str, pl.DataFrame]):
        collections_detail = data_transformed['detail'].with_columns(pl.lit(datetime.now(ZoneInfo('America/New_York')), pl.Datetime).alias('InsertedDT')).to_dicts()
        collections_summary = data_transformed['summary'].with_columns(pl.lit(datetime.now(ZoneInfo('America/New_York')), pl.Datetime).alias('InsertedDT')).to_dicts()
        collections_detail = data_transformed['detail'].with_columns(pl.lit(datetime.now(ZoneInfo('America/New_York')), pl.Datetime).alias('InsertedDT')).to_dicts()
        collections_summary = data_transformed['summary'].with_columns(pl.lit(datetime.now(ZoneInfo('America/New_York')), pl.Datetime).alias('InsertedDT')).to_dicts()
        balance_by_status = data_transformed['balance_by_status'].with_columns(pl.lit(datetime.now(ZoneInfo('America/New_York')), pl.Datetime).alias('InsertedDT')).to_dicts()
        balance_by_salesrep = data_transformed['balance_by_salesrep'].with_columns(pl.lit(datetime.now(ZoneInfo('America/New_York')), pl.Datetime).alias('InsertedDT')).to_dicts()
        
        collections_summary_snapshot = data_transformed['summary_snapshot'].to_dicts()
        balance_by_status_snapshot = data_transformed['balance_by_status_snapshot'].to_dicts()
        balance_by_salesrep_snapshot = data_transformed['balance_by_salesrep_snapshot'].to_dicts()
        
        
        self.centralstore.checked_upsert_paginated(table_name='analytics.JHL_B2BCollectionsDetail', data=collections_detail)
        self.centralstore.checked_upsert_paginated(table_name='analytics.JHL_B2BCollectionsSummary', data=collections_summary)
        self.centralstore.checked_upsert_paginated(table_name='analytics.JHL_B2BCollectionsSummary_Snapshot', data=collections_summary_snapshot)
        self.centralstore.checked_upsert_paginated(table_name='analytics.JHL_B2BCollectionsByStatus', data=balance_by_status)
        self.centralstore.checked_upsert_paginated(table_name='analytics.JHL_B2BCollectionsByStatus_Snapshot', data=balance_by_status_snapshot)        
        self.centralstore.checked_upsert_paginated(table_name='analytics.JHL_B2BCollectionsBySalesRep', data=balance_by_salesrep)
        self.centralstore.checked_upsert_paginated(table_name='analytics.JHL_B2BCollectionsBySalesRep_Snapshot', data=balance_by_salesrep_snapshot)
        bp = 'here'

        # self.logger.info(f'{total} rows to upsert')
        return data_transformed


    def log_results(self, data_loaded):
        pass