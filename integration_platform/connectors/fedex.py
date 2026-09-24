import logging
from integration_platform.config.settings import FEDEX
from datetime import datetime, timedelta
import requests
class Fedex:
    def __init__(self, pipeline):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.CriteoAPI')
        self.ep_rates = 'https://apis.fedex.com/rate/v1/rates/quotes'
        self._authenticate_()



    def _authenticate_(self):
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