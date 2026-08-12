

import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Any
class Load:
    def __init__(self, pipeline):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.Load')
        pass



    def landing_format_for_sql(self, data_transformed: dict):
        orders = [v for v in data_transformed.values()]
        bp = 'here'
        total = len(orders)
        for i, order in enumerate(orders):
            sql_order = self.format_for_sql(order)
            bp = 'here'
        return orders



    def format_for_sql(self, order: dict):
        bp = 'here'