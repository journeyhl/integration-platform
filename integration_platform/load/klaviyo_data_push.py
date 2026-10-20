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


    #TODO add subscription data
    def landing_loader(self, data_transformed: dict):
        bp = 'here'
        self._load_customer_records_(customer_records=data_transformed['customer_records'])
        # self._load_consent_updates_(consent_updates=data_transformed['consent_updates'])
        return data_transformed



    def _load_customer_records_(self, customer_records: list):
        total = len(customer_records)
        for i, customer_record in enumerate(customer_records):
            prepend = f'{customer_record['action'][:-1]}ing'
            if not customer_record['fields_added'] and not customer_record['fields_changed']:
                self.logger.info(f'Skipping profile {i+1}/{total} {customer_record['db']['Email']}...No fields added, nor changed')
                customer_record['klaviyo_response'] = None
                continue
            self.logger.info(f'{prepend} profile {i+1}/{total}... {customer_record['db']['Email']}{f' (https://www.klaviyo.com/profile/{customer_record['payload']['data']['id']})' if customer_record['action'] == 'Update' else ''}')
            response = self.pipeline.klaviyo.create_or_update_profile(payload=customer_record['payload'])
            if response.status_code == 201:
                self.logger.info(f'{customer_record['db']['Email']} created successfully')
            elif response.status_code == 200:
                self.logger.info(f'{customer_record['db']['Email']} updated successfully')
            else:
                self.logger.error(f'Error {response.status_code}! {response.text}')
            bp = 'here'
            customer_record['klaviyo_response'] = response.status_code

    def _load_consent_updates_(self, consent_updates: dict):
        bp = 'here'
        self.logger.info(f'Updating consent to subscribed for {len(consent_updates['profiles']['data'])} profiles')
        payload = {
            'data':{
                'type': 'profile-subscription-bulk-create-job',
                'attributes': consent_updates,
            }
        }
        response = self.pipeline.klaviyo.subscribe_profiles(payload=payload)
        resp_str = f'{response.status_code} {response.text}'
        if response.status_code == 200:
            self.logger.info(f'{resp_str}')
        else:
            self.pipeline.klaviyo.helper.parse_errors(response=response)
        bp = 'here'