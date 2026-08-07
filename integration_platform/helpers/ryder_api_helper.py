
from __future__ import annotations
from typing import TYPE_CHECKING, Literal
if TYPE_CHECKING:
    from integration_platform.connectors.ryder_api import RyderAPI
import logging
import requests
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from requests import Response
import polars as pl
import base64

class RyderAPIHelper:
    def __init__(self, ryder_api: RyderAPI) -> None:
        self.ryder = ryder_api
        if type(ryder_api.pipeline) == str:
            self.logger = logging.getLogger(f'{ryder_api.pipeline}.RyderAPIHelper')
        else:
            self.logger = logging.getLogger(f'{ryder_api.pipeline.pipeline_name}.RyderAPIHelper')        
        pass
    

    def _pre_auth_(self):
        
        credentials = f"{self.ryder.key}:{self.ryder.secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "Authorization": f"Basic {encoded_credentials}",
            "Ocp-Apim-Subscription-Key": self.ryder.key,
        }
        body = {
            "grant_type": "client_credentials",
            "scope": "APIM",
        }
        return headers, body

    def _post_auth_(self, response: Response):        
        try:
            time = datetime.now(ZoneInfo('America/New_York'))
            response.raise_for_status()
            jresponse = response.json()
            auth_data = {
                **jresponse,
                'auth_time': time,
                'expiry_time': time + timedelta(seconds=jresponse['expires_in'])
            }
            headers = {
                "Authorization": f'{jresponse['token_type']} {jresponse['access_token']}',
                "Ocp-Apim-Subscription-Key": self.ryder.key,
            }
            self.logger.info(f'Ryder API is online and authenticated')
            return auth_data, headers
        except Exception as e:
            self.logger.info(f"Couldn't authenticate!")
            bp = 'here'
            return {}, {}



    def parse_get(self, response: Response, sender: str):
        rstr = f'{response.status_code} {response.reason}'
        if rstr == '200 OK':
            self.logger.info(msg=rstr)
        else:
            bp = 'here'
        if 'no order is found' in response.text.lower() or 'no shipment status is found' in response.text.lower():
            self.logger.warning(f'{response.text}, returning empty dict...')
            return {}

        try:
            jresponse = response.json()
        except Exception as e:
            self.logger.error(f"Error! returning empty dict...{e}")
            return {}

        if sender in ['get_order_history', 'get_order_milestones']:
            return jresponse[0]

    




    #region In development
    def parse_post(self, response: Response, sender: str):
        pass
    def parse_put(self, response: Response, sender: str):
        pass
    def parse_delete(self, response: Response, sender: str):
        pass
    #endregion

