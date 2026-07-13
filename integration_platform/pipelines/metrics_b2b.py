from . import Pipeline
from integration_platform.load.call_center_mfr import Load
import polars as pl
from datetime import datetime
from zoneinfo import ZoneInfo
from integration_platform.transform.sales_summary_b2b import Transform

class B2BMetrics(Pipeline):
    def __init__(self, function: str):
        super().__init__('b2b-metrics', function)
        self.transformer = Transform(self)

    def extract(self):
        raw_b2b_sales = self.centralstore.query_to_dataframe(self.centralstore.queries.raw_B2BSalesSummary)
        int_b2b_sales = self.centralstore.query_to_dataframe(self.centralstore.queries.int_B2BSalesSummary)
        b2b_customers = self.centralstore.query_to_dataframe(query=self.centralstore.queries.Metrics_B2BCustomers)
        customer_age = self.centralstore.query_to_dataframe(query=self.centralstore.queries.Metrics_B2BCustomerAge)
        data_extract = {
            # 'analytics.int_SalesSummaryB2B': b2b_sales,
            'raw_b2b_sales': raw_b2b_sales,
            'int_b2b_sales': int_b2b_sales,
            'b2b_customers': b2b_customers,
            'customer_age': customer_age
        }
        return data_extract

    def transform(self, data_extract):
        data_transformed = self.transformer.landing(data_extract=data_extract)
        return data_transformed
    
    def load(self, data_transformed):
        bp = 'here'
        
        for table, data in data_transformed.items():
            # self.logger.info(f'Deleting {data.height} rows from {table}...')
            # self.centralstore.raw_execute(f'delete from {table}')
            self.logger.info(f'Inserting {data.height} rows to {table}...')
            bp = 'here'
            self.centralstore.insert_df(df_data_loaded=data, table_name=table)
            bp = 'here'

        # for table_name, data in data_transformed['upsert'].items():
        #     for item in data:
        #         item['InsertedDT'] = datetime.now(ZoneInfo('America/New_York'))
        #         item['LastChecked'] = datetime.now(ZoneInfo('America/New_York'))
        #     self.logger.info(f'Beginning upsert to {table_name}')
        #     data_loaded = self.centralstore.checked_upsert_paginated(table_name=table_name, data=data)


        # for table, data in data_transformed['delinsert'].items():
        #     self.logger.info(f'Deleting {data.height} rows from {table}...')
        #     self.centralstore.raw_execute(f'delete from {table}')
        #     self.logger.info(f'Inserting {data.height} rows to {table}...')
        #     bp = 'here'
        #     self.centralstore.insert_df(df_data_loaded=data, table_name=table)
        #     bp = 'here'



        return data_transformed
    
    def log_results(self, data_loaded):
        pass