import logging
from integration_platform.config.settings import RYDER
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Any, Literal
from integration_platform.helpers.ryder_api_helper import RyderAPIHelper

class RyderAPI:
    def __init__(self, pipeline, env: str = 'prod'):
        self.pipeline = pipeline
        if type(pipeline) == str:
            self.logger = logging.getLogger(f'{pipeline}.RyderAPI')
        else:
            self.logger = logging.getLogger(f'{pipeline.pipeline_name}.RyderAPI')
        self.config = RYDER
        '''Get Ryder config from config/settings.py - :mod:`~integration_platform.config.settings.RYDER`'''
        self.key = self.config['api_key'] if env == 'prod' else self.config['dev_api_key'] 
        '''Ryder API key'''
        self.secret = self.config['api_secret'] if env == 'prod' else self.config['dev_api_secret']
        '''Ryder API secret'''

        self.uri_env = 'api' if env == 'prod' else 'apiqa'
        '''If dev, prepend base uri with apiqa instead of prod value, api.'''

        self.base_import_uri = f'https://{self.uri_env}.ryder.com/rcsc/order-requests/v1'
        self.base_status_uri = f'https://{self.uri_env}.ryder.com/rcsc/order-status/v1'

        self.ep_history_since_last_poll = f'{self.base_status_uri}/orders?partnerId=JOURHL&clientId=JOURHL'
        '''Best to just not use this one lol...trust'''

        self.ep_order_history_by_orderRef = f'{self.base_status_uri}/orders?orderRef='
        '''Retrieve current and historical status updates by appending an orderRef (Acu ShipmentNbr) to string'''

        self.ep_order_status_by_orderRef = f'{self.base_status_uri}/tracks?orderRef='
        '''Retrieve Milestone/High-level status updates by appending an orderRef (Acu ShipmentNbr) to string'''

        self.session = requests.Session()
        self.helper = RyderAPIHelper(ryder_api=self)
        self._auth_()
        pass




    def _auth_(self):
        headers, body = self.helper._pre_auth_()
        response = self.session.post(f'https://{self.uri_env}.ryder.com/identityservices/oauth2/default/v1/token', headers=headers, data=body)
        self.auth_data, self.headers = self.helper._post_auth_(response=response)
        pass


    def get_order_history(self, shipment_nbr: str, log_prefix: str = ''):
        url = f'{self.ep_order_history_by_orderRef}{shipment_nbr}'
        normalized_response = self._target_api_(url=url, operation='get', sender='get_order_history', descr=f'{shipment_nbr}: Get full history', log_prefix=log_prefix)
        bp = 'here'
        return normalized_response

    def get_order_milestones(self, shipment_nbr: str, log_prefix: str = ''):
        url = f'{self.ep_order_status_by_orderRef}{shipment_nbr}'
        normalized_response = self._target_api_(url=url, operation='get', sender='get_order_milestones', descr=f'{shipment_nbr}: Get milestones', log_prefix=log_prefix)
        bp = 'here'
        return normalized_response





    def _target_api_(self, url: str, operation: Literal['get', 'post', 'put', 'delete'], sender: str, payload: dict = {}, descr: str = '', log_prefix: str = ''):
        ''':class:`~RyderAPI`.:meth:`~_target_api_` (self, endpoint: *str*, operation: *str*, ):
        ---
        <hr>
        
        Modular method to hit RyderAPI at any endpoint
        
        ### Downstream Calls 
         #### :class:`~integration_platform.helpers.ryder_api_helper.RyderAPIHelper`.:meth:`~integration_platform.helpers.ryder_api_helper.RyderAPIHelper.parse_get`
            - Description
         #### _______replace_me_______
            - Description
        
        ### Upstream Calls 
         #### :class:`~integration_platform.connectors.ryder_api.RyderAPI`.:meth:`~integration_platform.connectors.ryder_api.RyderAPI.get_order_history`
            - Retrieves an order's full history from Ryder API
         #### _______replace_me_______
            - Description
            
        <hr>
        
        Parameters
        ---
        :param (*str*) `url`: Absolute URL to hit Ryder api at 
        :param (*str*) `operation`: Type of operation
        :param (*dict = {}*) `payload`: _Optional payload to send to Ryder api_
        :param (*str = ''*) `descr`: _Optional description of what this call will be doing when targeting Ryder api_
        
        <hr>
        
        Returns
        ---
        '''
        bp = 'here'
        self.logger.info(f'{log_prefix}Hitting Ryder API with a {operation} request at {url}')
        if operation.lower() == 'get':
            response = self.session.get(url=url, headers=self.headers)
            parsed_response = self.helper.parse_get(response=response, sender=sender) or {}
            return parsed_response
        elif operation.lower() == 'post':
            response = self.session.post(url=url, headers=self.headers)
        elif operation.lower() == 'put':
            response = self.session.put(url=url, headers=self.headers)
        elif operation.lower() == 'delete':
            response = self.session.delete(url=url, headers=self.headers)
        return {}