import logging
from integration_platform.config.settings import FEDEX
from integration_platform.helpers.fedex_helper import FedexHelper
from datetime import datetime, timedelta
import requests
class Fedex:
    def __init__(self, pipeline):
        self.pipeline = pipeline
        if isinstance(pipeline, str):
            self.logger = logging.getLogger(f'{pipeline}.FedexAPI')
        else:
            self.logger = logging.getLogger(f'{pipeline.pipeline_name}.CriteoAPI')
        self.helper = FedexHelper(self)
        self.ep_rates = 'https://apis.fedex.com/rate/v1/rates/quotes'
        self._authenticate_()



    def _authenticate_(self):
        self.account_id = FEDEX['account_id']
        response = requests.post(
            url='https://apis.fedex.com/oauth/token',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data={
                'grant_type': 'client_credentials',
                'client_id': FEDEX['client_id'],
                'client_secret': FEDEX['client_secret']
            }
        )
    
        tokenData = response.json()
        token = tokenData['access_token']
        self.tokenExpiry = datetime.now() + timedelta(seconds=tokenData.get('expires_in', 3600) - 60)
        self.headers ={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        self.logger.info(f'FedexAPI online')
        bp = 'here'


    def get_rate(self):
        payload = self.helper.format_rate_payload()
        response = requests.post(url=self.ep_rates, json=payload, headers=self.headers)
        parsed_response = self.helper.parse_rate_response(response=response)
        bp = 'here'