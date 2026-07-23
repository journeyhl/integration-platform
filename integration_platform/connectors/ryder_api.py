import logging
from integration_platform.config.settings import RYDER
import requests
import base64
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

class RyderAPI:
    def __init__(self, pipeline, env: str = 'prod'):
        self.pipeline = pipeline
        if type(pipeline) == str:
            self.logger = logging.getLogger(f'{pipeline}.RyderAPI')
        else:
            self.logger = logging.getLogger(f'{pipeline.pipeline_name}.RyderAPI')
        self.config = RYDER
        self.key = self.config['api_key'] if env == 'prod' else self.config['dev_api_key']
        self.secret = self.config['api_secret'] if env == 'prod' else self.config['dev_api_secret']
        self.session = requests.Session()
        self._auth_()
        pass




    def _auth_(self):
        bp = 'here'
        credentials = f"{self.key}:{self.secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "Authorization": f"Basic {encoded_credentials}",
            "Ocp-Apim-Subscription-Key": self.key,
        }
        body = {
            "grant_type": "client_credentials",
            "scope": "APIM",
        }
        try:
            response = self.session.post('https://api.ryder.com/identityservices/oauth2/default/v1/token', headers=headers, data=body)
            time = datetime.now(ZoneInfo('America/New_York'))
            response.raise_for_status()
            jresponse = response.json()
            self.auth_data = {
                **jresponse,
                'auth_time': time,
                'expiry_time': time + timedelta(seconds=jresponse['expires_in'])
            }
            self.headers = {
                "Authorization": f'{jresponse['token_type']} {jresponse['access_token']}',
                "Ocp-Apim-Subscription-Key": self.key,

            }
            return jresponse['access_token']
        except Exception as e:
            self.logger.info(f"Couldn't authenticate!")
            bp = 'here'