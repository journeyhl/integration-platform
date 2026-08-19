import polars as pl
from integration_platform.pipelines import Pipeline

from integration_platform.connectors.sql import SQLConnector, AcumaticaDbQueries
from integration_platform.transform.link_b2b_cohorts_to_acu import Transform
class B2BCohortsLinkToAcu(Pipeline):
    '''`RMILinkToAcu`(Pipeline)
    ---
    <hr>

    Pipeline to populate Shipment attributes in Acumatica through the database, allowing for updates after the UI has disallowed them. Currently updates the AttributeLINK3PL value for RMI shipments that don't have that attribute populated

    # Extraction
     - Two data sources are used in extraction:
        - **acu_extract**: Retrieves any shipments from Acumatica that have RMI as the warehouse and a null Link3PL 
            - **RMI_Link3PL** query
        - **rmi_extract**: Pulls all distinct RMAIDs from **rmi_RMAStatus**

    # Transformation
     - Inner join the two extracted DataFrames. This leaves us with just the shipments that don't have a Link3PL attribute value in Acu, but have a record in our RMI status tracking table
     
    # Load
     - Load the Link3PL value from our RMI centralstore query to AcumaticaDB, in the SOShipmentKvExt table

    # Results Logging
     - None needed
    '''
    def __init__(self, function: str, env: str='prod'):
        super().__init__(pipeline_name='b2b-cohorts-link-to-acu', function=function, env=env)
        self.acudb: SQLConnector[AcumaticaDbQueries] = SQLConnector(
            pipeline=self, database_name='AcudevDb' if env == 'dev' else 'AcumaticaDb'
        )
        self.transformer = Transform(self)

    def extract(self):
        all_customers = self.acudb.query_to_dataframe(self.acudb.queries.B2BCohorts_CustomerNoteIDs)
        customer_attributes = self.centralstore.query_to_dataframe(self.centralstore.queries.B2BCohorts_GenerateAttributeIDs)
        data_extract = pl.SQLContext(all_customers = all_customers, customer_attributes = customer_attributes)
        return data_extract

    def transform(self, data_extract: pl.SQLContext):
        data_transformed = self.transformer.landing(data_extract=data_extract)
        return data_transformed
    
    def load(self, data_transformed):
        if len(data_transformed) > 0:
            self.acudb.checked_upsert_paginated('CSAnswers', data_transformed)
        else:
            self.logger.info(f'No rows to upsert')
        return data_transformed
    
    def log_results(self, data_loaded):
        pass