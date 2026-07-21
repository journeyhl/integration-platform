import polars as pl
from integration_platform.pipelines import Pipeline

class AftershipLinkToAcu(Pipeline):
    '''`AftershipLinkToAcu`(Pipeline)
    ---
    <hr>

    Pipeline to populate Order attributes in Acumatica through the database, allowing for updates after the UI has disallowed them. Currently updates the AttributeAFTSHIPID value for orders that don't have the value populated

    # Extraction
     - Two data sources are used in extraction:

    # Transformation
     
    # Load
     - Load the Link3PL value from our RMI centralstore query to AcumaticaDB, in the SOOrderKvExt table

    # Results Logging
     - None needed
    '''
    def __init__(self, function: str):
        super().__init__('aftership-link-to-acu', function)
        
    def extract(self):
        acu_extract = self.acudb.query_to_dataframe(self.acudb.queries.Aftership_LinkID_Acu)
        aftership_extract = self.centralstore.query_to_dataframe(self.centralstore.queries.Aftership_LinkID)
        

        data_extract = pl.SQLContext(acu = acu_extract, aftership = aftership_extract)
        return data_extract

    def transform(self, data_extract: pl.SQLContext):
        data_transformed = data_extract.execute(
        '''
        select *
        from acu a
        inner join aftership s on a.OrderNbr = s.OrderNbr
        where a.AfterShipID != s.ValueString or a.AfterShipID is null
        ''',
        eager =True
        )     
        bp = 'here'
        distinct_columns = [column for column in data_transformed.columns if column not in['ValueString']]
        df_transformed = data_transformed.group_by(distinct_columns, maintain_order=True).agg(
            pl.col('ValueString').drop_nulls().unique(maintain_order=True).str.join(', ').str.slice(0, 255)
        )
        data_transformed = df_transformed.to_dicts()

        return data_transformed
    
    def load(self, data_transformed):
        if len(data_transformed) > 0:
            self.acudb.checked_upsert_paginated('SOOrderKvExt', data_transformed)
        else:
            self.logger.info(f'No rows to upsert')
        return data_transformed
    
    def log_results(self, data_loaded):
        pass