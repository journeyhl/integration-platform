from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.klaviyo_data_push import KlaviyoDataPush
import logging
import time
import polars as pl
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import json
from typing import Literal
class PostLoad:
    def __init__(self, pipeline: KlaviyoDataPush):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.Load')
        bp = 'here'


    def landing(self, data_transformed):
        def print_dict_items(k, v, prefix: str):
            if isinstance(v, dict):
                for k2, v2 in v.items():
                    print_dict_items(k=k2, v=v2, prefix=f"{prefix}['{k}']")
            else:
                self.logger.info(f"{prefix}['{k}']: '{v}'")
        customer_records = data_transformed['customer_records']
        bp = 'here'
        for i, customer in enumerate(customer_records):
            klaviyo = customer['klaviyo_response']['data']['attributes']
            hubspot = customer['hubspot_response']
            bp = 'here'
            for k, v in klaviyo.items():
                print_dict_items(k=k, v=v, prefix='klaviyo')
            bp = 'here'
            for k, v in hubspot.items():
                self.logger.info(f'hubspot[{k}]: {v}')
            bp = 'here'




    