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
        b2b_customer_order_history = self.centralstore.query_to_dataframe(query=self.centralstore.queries.Metrics_B2BCustomerOrderHistory)
        customer_age = self.centralstore.query_to_dataframe(query=self.centralstore.queries.Metrics_B2BCustomerAge)
        data_extract = {
            'raw_b2b_sales': raw_b2b_sales,
            'int_b2b_sales': int_b2b_sales,
            'b2b_customer_order_history': b2b_customer_order_history,
            'customer_age': customer_age
        }
        return data_extract

    def transform(self, data_extract):
        data_transformed = self.transformer.landing(data_extract=data_extract)
        return data_transformed
    
    def load(self, data_transformed):
        bp = 'here'
        now = datetime.now(ZoneInfo('America/New_York'))
        frame_count = len(data_transformed)
        for key in data_transformed:
            print(key)
        bp = 'here'
        for i, (table, data) in enumerate(data_transformed.items()):
            if i < 4:
                continue
            prefix = f'{i+1}/{frame_count}: '
            db_data = data.to_dicts()
            if table in['analytics.JHL_B2BRevenueByCustomer', 'analytics.JHL_B2BRevenueByCustomerType']:
                db_data = self.centralstore.sql_helper.add_to_list(ldata=db_data, additions = {'InsertedDT': now, 'LastChecked': now})
            else:
                db_data = self.centralstore.sql_helper.add_to_list(ldata=db_data, additions={'InsertedDT': now})
            #TODO: left off on analytics.int_B2BCustomerAgeCategory
            self.centralstore.merge_table_paginated(table_name=table, data=db_data)
            # self.logger.info(f'{prefix}Deleting {data.height} rows from {table}...')
            # self.centralstore.raw_execute(f'delete from {table}')
            # self.logger.info(f'{prefix}Inserting {data.height} rows to {table}...')
            # bp = 'here'
            # self.centralstore.insert_df(df_data_loaded=data, table_name=table)
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