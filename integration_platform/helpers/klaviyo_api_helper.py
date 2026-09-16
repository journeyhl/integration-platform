
from __future__ import annotations
from typing import TYPE_CHECKING, Literal
if TYPE_CHECKING:
    from integration_platform.connectors.klaviyo import KlaviyoAPI
import logging
import requests
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from requests import Response
import polars as pl

class KlaviyoAPIHelper:
    ''':class:`~integration_platform.connectors.klaviyo.KlaviyoAPI`.:class:`~integration_platform.helpers.klaviyo_api_helper.KlaviyoAPIHelper`
    ---
    
    Helper class for :class:`~integration_platform.connectors.klaviyo.KlaviyoAPI`
    
    <hr>
    
    Methods
    ---
    
    - ## :meth:`~integration_platform.helpers.klaviyo_api_helper.KlaviyoAPIHelper.format_headers`
    - ## :meth:`~integration_platform.helpers.klaviyo_api_helper.KlaviyoAPIHelper.parse_response`
    - ## :meth:`~integration_platform.helpers.klaviyo_api_helper.KlaviyoAPIHelper.consolidate_profiles`
    '''
    def __init__(self, klaviyo_api: KlaviyoAPI) -> None:
        self.klaviyo = klaviyo_api
        self.pipeline = klaviyo_api.pipeline
        if type(klaviyo_api.pipeline) == str:
            self.logger = logging.getLogger(f'{klaviyo_api.pipeline}.KlaviyoAPIHelper')
        else:
            self.logger = logging.getLogger(f'{klaviyo_api.pipeline.pipeline_name}.KlaviyoAPIHelper')        
        pass

    #MARK: format_headers
    def format_headers(self, api_key: str) -> dict:
        ''':class:`~integration_platform.connectors.klaviyo.KlaviyoAPI`.:class:`~KlaviyoAPIHelper`.:meth:`~format_headers`
        ---
        
        Formats headers to be sent with each request to api
        
        Parameters
        ---
        :param (*str*) `api_key`: Klaviyo API key from .env file
        
        Returns
        ---
        :return `headers` (dict): dict of headers to be used as KlaviyoAPI's self.:attr:`~integration_platform.connectors.klaviyo.KlaviyoAPI.headers` value
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.connectors.klaviyo.KlaviyoAPI`.:meth:`~integration_platform.connectors.klaviyo.KlaviyoAPI.__init__`
        '''        
        headers = {
            'Authorization': f'Klaviyo-API-Key {api_key}',
            'revision': '2026-04-15',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        return headers



    #MARK: parse_response
    def parse_response(self, response: Response, url: str = 'KlaviyoAPI'):
        ''':class:`~integration_platform.connectors.klaviyo.KlaviyoAPI`.:class:`~KlaviyoAPIHelper`.:meth:`~parse_response`
        ---
        
        Prases response from Klaviyo and returns dictionary containing `data` and `links`. If error, returns empty dict
        
        Parameters
        ---
        :param (*Response*) `response`: Response from Klaviyo
        
                
           ### ***Optional***
        :param (*str = 'KlaviyoAPI'*) `url`: Used for logging more precisely
        
        Returns
        ---
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.connectors.klaviyo.KlaviyoAPI`.:meth:`~integration_platform.connectors.klaviyo.KlaviyoAPI.get_data`
        '''
        if '?' in url:
            url = url.split('?')[0]
        try:
            jresponse = response.json()
            self.logger.info(f'Successfully parsed response from {url}')
            return jresponse
        except Exception as e:
            self.logger.error(f"Couldn't parse response from {url}!")
            return {}

    #MARK: consolidate_profiles
    def consolidate_profiles(self, profiles: list[dict]):

        parsed_profiles = []
        for p in profiles:
            bp = 'here'
            parent = {
                'id': p['id'],
                'created': p['attributes']['created'],
                'phone_number': p['attributes']['phone_number'],
                'email': p['attributes']['email'],
                'first_name': p['attributes']['first_name'],
                'last_name': p['attributes']['last_name'],
                'joined_group_at': p['attributes']['joined_group_at'],
                'last_event_date': p['attributes']['last_event_date'],
                'organization': p['attributes']['organization'],
                'created': p['attributes']['created'],
                'updated': p['attributes']['updated'],
                'title': p['attributes']['title'],
                'external_id': p['attributes']['external_id'],
                'locale': p['attributes']['locale'],
            }
            parent['properties'] = p['attributes']['properties']    
            parent['subscriptions'] = p['attributes']['subscriptions']
            parent['relationships'] = {parent: values for parent, entries in p['relationships'].items() for key, values in entries.items()}

            parsed_profiles.append(parent)
        return parsed_profiles



    mapping = {

'phone_number': 'PhoneNumber',
'email': 'Email',
'first_name': 'FirstName',
'last_name': 'LastName',
'joined_group_at': 'JoinedGroupAt',
'last_event_date': 'LastEventDate',
'organization': 'Organization',
'created': 'Created',
'updated': 'Updated',
'title': 'Title',
'external_id': 'ExternalId',
'locale': 'Locale',
'image': 'Image',

    'predictive_analytics': 'PredictiveAnalytics',
    'properties': 'Properties',
    'subscriptions': 'Subscriptions',
    'location': 'Location',

    }