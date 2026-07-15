from . import Pipeline
from integration_platform.load.call_center_mfr import Load
import polars as pl
from datetime import datetime
from zoneinfo import ZoneInfo
from integration_platform.transform.sales_summary_b2b import Transform

class SalesSummaryMetrics(Pipeline):
    def __init__(self, function: str):
        super().__init__('sales-summary-metrics', function)
        self.b2b_transformer = Transform(self)

    def extract(self):
        raw_summary = self.centralstore.query_to_dataframe(self.centralstore.queries.raw_SalesSummary)
        int_summary = self.centralstore.query_to_dataframe(self.centralstore.queries.int_SalesSummary)
        jhl_summary = self.centralstore.query_to_dataframe(self.centralstore.queries.jhl_SalesSummary)
        data_extract = {
            'upsert':{                
                'analytics.JHL_SalesSummary': jhl_summary.to_dicts(),
                'analytics.int_SalesSummary': int_summary.to_dicts(),
            },
            'delinsert':{
                'analytics.raw_SalesSummary': raw_summary
            }
        }
        return data_extract

    def transform(self, data_extract):
        data_extract['delinsert']['analytics.raw_SalesSummary'] = data_extract['delinsert']['analytics.raw_SalesSummary'].with_columns(
            pl.lit(datetime.now(ZoneInfo('America/New_York')), pl.Datetime).alias('LastChecked'),
            pl.lit(datetime.now(ZoneInfo('America/New_York')), pl.Datetime).alias('InsertedDT')
            )
        return data_extract
    
    def load(self, data_transformed):
        
        for table_name, data in data_transformed['upsert'].items():
            for item in data:
                item['InsertedDT'] = datetime.now(ZoneInfo('America/New_York'))
                item['LastChecked'] = datetime.now(ZoneInfo('America/New_York'))
            self.logger.info(f'Beginning upsert to {table_name}')
            data_loaded = self.centralstore.checked_upsert_paginated(table_name=table_name, data=data)


        for table, data in data_transformed['delinsert'].items():
            self.logger.info(f'Deleting {data.height} rows from {table}...')
            self.centralstore.raw_execute(f'delete from {table}')
            self.logger.info(f'Inserting {data.height} rows to {table}...')
            bp = 'here'
            self.centralstore.insert_df(df_data_loaded=data, table_name=table)
            bp = 'here'



        return data_transformed
    
    def log_results(self, data_loaded):
        pass