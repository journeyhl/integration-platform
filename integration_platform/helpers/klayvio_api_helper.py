
from __future__ import annotations
from typing import TYPE_CHECKING, Literal
if TYPE_CHECKING:
    from integration_platform.connectors.klayvio import KlayvioAPI
import logging
import requests
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from requests import Response
import polars as pl

class KlayvioAPIHelper:
    def __init__(self, klayvio_api: KlayvioAPI) -> None:
        self.klayvio = klayvio_api
        if type(klayvio_api.pipeline) == str:
            self.logger = logging.getLogger(f'{klayvio_api.pipeline}.KlayvioAPIHelper')
        else:
            self.logger = logging.getLogger(f'{klayvio_api.pipeline.pipeline_name}.KlayvioAPIHelper')        
        pass

    def format_headers(self, api_key) -> dict:
        ''':class:`~integration_platform.connectors.klayvio.KlayvioAPI`.:class:`~KlayvioAPIHelper`.:meth:`~format_headers`
        ---
        
        Formats headers to be sent with each request to api
        
        Parameters
        ---
        :param (*str*) `api_key`: Klayvio API key from .env file
        
        Returns
        ---
        :return `headers` (dict): dict of headers to be used as KlayvioAPI's self.:attr:`~integration_platform.connectors.klayvio.KlayvioAPI.headers` value
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.connectors.klayvio.KlayvioAPI`.:meth:`~integration_platform.connectors.klayvio.KlayvioAPI.__init__`
        '''        
        headers = {
            'Authorization': f'Klaviyo-API-Key {api_key}',
            'revision': '2026-04-15',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        return headers



    def parse_response(self, response: Response, url: str = 'KlayvioAPI'):
        ''':class:`~integration_platform.connectors.klayvio.KlayvioAPI`.:class:`~KlayvioAPIHelper`.:meth:`~parse_response`
        ---
        
        Prases response from Klayvio and returns dictionary
        
        Parameters
        ---
        :param (*Response*) `response`: Response from Klayvio
        
                
           ### ***Optional***
        :param (*str = 'KlayvioAPI'*) `url`: Used for logging more precisely
        
        Returns
        ---
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.connectors.klayvio.KlayvioAPI`.:meth:`~integration_platform.connectors.klayvio.KlayvioAPI.get_data`
        '''
        
        try:
            jresponse = response.json()
            self.logger.info(f'Successfully parsed response from {url}')
            return jresponse
        except Exception as e:
            self.logger.error(f"Couldn't parse response from {url}!")
            return {}


