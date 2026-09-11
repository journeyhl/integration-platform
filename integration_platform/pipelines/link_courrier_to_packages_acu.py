import polars as pl
from integration_platform.pipelines import Pipeline

from integration_platform.connectors.sql import SQLConnector, AcumaticaDbQueries
from integration_platform.transform.link_b2b_cohorts_to_acu import Transform
class CourierPackage_Backfill(Pipeline):
    ''':class:`~integration_platform.pipelines.link_courrier_to_packages_acu.LinkCourierPackage_Backfill`
    ---
    
    Adds the courier to packages in Acumatica where applicable
    
    
    Parameters
    ---
    :param (*_type_*) `Pipeline`: Inherits base Pipeline superclass
    '''
    def __init__(self, function: str, env: str='prod'):
        super().__init__(pipeline_name='courier-package-backfill', function=function, env=env)
        self.acudb: SQLConnector[AcumaticaDbQueries] = SQLConnector(
            pipeline=self, database_name='AcudevDb' if env == 'dev' else 'AcumaticaDb'
        )

    def extract(self):
        all_customers = self.acudb.query_to_dataframe(self.acudb.queries.B2BCohorts_CustomerNoteIDs)
        customer_attributes = self.centralstore.query_to_dataframe(self.centralstore.queries.B2BCohorts_GenerateAttributeIDs)
        data_extract = pl.SQLContext(all_customers = all_customers, customer_attributes = customer_attributes)
        return data_extract

    def transform(self, data_extract: pl.SQLContext):
        # data_transformed = self.transformer.landing(data_extract=data_extract)
        data_transformed = []
        return data_transformed
    
    def load(self, data_transformed):
        if len(data_transformed) > 0:
            self.acudb.checked_upsert_paginated('SOPackageDetail', data_transformed)
        else:
            self.logger.info(f'No rows to upsert')
        return data_transformed
    
    def log_results(self, data_loaded):
        pass