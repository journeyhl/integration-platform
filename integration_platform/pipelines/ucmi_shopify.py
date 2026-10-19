from integration_platform.pipelines import Pipeline
from integration_platform.transform.ucmi_shopify import Transform
from integration_platform.connectors.shopify import ShopifyAPI
from datetime import datetime
from zoneinfo import ZoneInfo
import polars as pl

class UCMI_ShopifyCustomers(Pipeline):
    def __init__(self, function: str, env: str='prod'):
        super().__init__(pipeline_name='ucmi-shopify-customers', function=function, env=env)
        self.shopify = ShopifyAPI(self)
        self.transformer = Transform(self)

    def extract(self):
        self.ts_extract = datetime.now(ZoneInfo('America/New_York'))
        data_extract = self.shopify.get_customers_bulk()
        return data_extract

    def transform(self, data_extract):
        data_transformed = self.transformer.landing(data_extract=data_extract)
        return data_transformed
    
    def load(self, data_transformed):
        self.centralstore.reconnect()
        data_loaded = {}
        for table, rows in data_transformed.items():
            rows = self.default_loader.add_InsertedDT_to_list(ldata=rows)
            self.centralstore.merge_table_paginated(table_name=table, data=rows)
            bp = 'here'
        return data_loaded
    
    def log_results(self, data_loaded):
        pass