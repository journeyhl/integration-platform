from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.klaviyo_data_push import KlaviyoDataPush
import logging
import time
import polars as pl
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

class Load:
    def __init__(self, pipeline: KlaviyoDataPush):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.Load')
        bp = 'here'



    def landing_loader(self, data_transformed: list):
        bp = 'here'
        total = len(data_transformed)
        for i, customer_record in enumerate(data_transformed):
            prepend = f'{customer_record['action'][:-1]}ing'
            self.logger.info(f'{prepend} profile {i+1}/{total}...{customer_record['db']['Email']}')
            response = self.pipeline.klaviyo.create_or_update_profile(payload=customer_record['payload'])
            if response.status_code == 201:
                self.logger.info(f'{customer_record['db']['Email']} created successfully')
            elif response.status_code == 200:
                self.logger.info(f'{customer_record['db']['Email']} updated successfully')
            else:
                self.logger.error(f'Error {response.status_code}! {response.text}')
            bp = 'here'
            customer_record['klaviyo_response'] = response.status_code
        return data_transformed
            