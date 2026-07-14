import logging
import polars as pl

class Transform:

    def __init__(self, pipeline):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.transform')
        pass


    def landing(self, data_extract: pl.DataFrame):

        distinct_columns = [column for column in data_extract.columns if column not in['VendorPartNumber']]
        df_transformed = data_extract.group_by(distinct_columns, maintain_order=True).agg(
            pl.col('VendorPartNumber').drop_nulls().unique(maintain_order=True).str.join(', ')
        )
        data_transformed = df_transformed.to_dicts()
        return data_transformed
