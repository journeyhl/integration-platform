import polars as pl
from integration_platform.pipelines import Pipeline

from integration_platform.connectors.sql import SQLConnector, AcumaticaDbQueries
from integration_platform.transform.link_courier_to_packages_acu_backfill import Transform
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
        self.transformer = Transform(self)

    def extract(self):
        acu_packages = self.acudb.query_to_dataframe(self.acudb.queries.backfill_PackageCouriers)
        dbc_packages = self.centralstore.query_to_dataframe(self.centralstore.queries.backfill_PackageCouriers)
        data_extract = {
            'acu': acu_packages,
            'dbc': dbc_packages
        }
        return data_extract

    def transform(self, data_extract):
        #TODO left off here friday, 9/11. pick back up
        data_transformed = self.transformer.landing(data_extract=data_extract)
        return data_transformed
    
    def load(self, data_transformed):
        if len(data_transformed) > 0:
            self.acudb.update_table_paginated(table_name='SOPackageDetail', data=data_transformed)
        else:
            self.logger.info(f'No rows to upsert')
        return data_transformed
    
    def log_results(self, data_loaded):
        pass