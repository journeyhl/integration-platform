
from __future__ import annotations
from typing import TYPE_CHECKING, Literal
if TYPE_CHECKING:
    from integration_platform.connectors.klaviyo import KlaviyoAPI
import logging
import requests
import time
from datetime import datetime, timedelta, date
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
                'joined_group_at': p['attributes'].get('joined_group_at'),
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



    #MARK: parse_errors
    def parse_errors(self, response: requests.Response):
        bp = 'here'
        try:
            jresponse = response.json()
        except Exception as e:
            self.logger.error(f"Error! Couldn't parse response as JSON! {e}")
        bp = 'here'
        try:
            errors = jresponse['errors']
        except Exception as e:
            self.logger.error(f'Error! No `errors` dict found in response!')
            return
        for error in errors:
            self.logger.warning(f'Error! {error.get('detail')}')
        return

    #MARK: _parse_and_compare_dates_
    def __parse_and_compare_dates__(self, klaviyo_date: str) -> datetime | None:
        ''':class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform.__parse_and_compare_dates__`
        ---
        
        Handles the date parsing of different formatted dates from klaviyo
        
        Parameters
        ---
        :param (*str*) `klaviyo_date`: klavio date as string
        
        Returns
        ---
        :return `date_value` (datetime | None): klaviyo date value, datetime if parsaed successfully, None if not
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform._compare_attributes_properties_dates_`
        
        ## Downstream Calls (Methods/Functions called)
        
         ### :class:`~integration_platform.transform.default_transformer.DefaultTransformer`.:meth:`~integration_platform.transform.default_transformer.DefaultTransformer.parse_date_str`
        '''
        def retry(date_str):
            formats = [
                '%Y/%m/%dT%H:%M:%SZ',    '%m/%d/%YT%H:%M:%SZ',
                '%Y/%m/%d %H:%M',        '%m/%d/%Y %H:%M',
                '%Y-%m-%d %H:%M',        '%m-%d-%Y %H:%M',
                '%Y-%m-%d %H:%M %p',     '%m-%d-%Y %H:%M %p',
                '%Y/%m/%d %H:%M %p',     '%m/%d/%Y %H:%M %p',
                '%Y-%m-%dT%H:%M:%S.%fZ', '%m-%d-%YT%H:%M:%S.%fZ',
                '%m/%d/%Y', '%Y-%m-%d'
            ]
            for format in formats:
                date_value = self.pipeline.default_transformer.parse_date_str(date_str=klaviyo_date, tries=0, format=format)
                if date_value:
                    return date_value
            return date_value
        kdate_len = len(klaviyo_date)
        kdate_dash = klaviyo_date.find('-')
        kdate_slash = klaviyo_date.find('/')
        kdate_plus = klaviyo_date.find('+')
        kdate_T = klaviyo_date.find('T')
        kdate_Z = klaviyo_date.find('Z')
        kdate_space = klaviyo_date.find(' ')
        d_or_s = '-' if kdate_dash != -1 and kdate_slash == -1 else '/'
        if kdate_dash == 2 or kdate_slash == 2:
            datepart = f'%m{d_or_s}%d{d_or_s}%Y'
        else:
            datepart = f'%Y{d_or_s}%m{d_or_s}%d'
        date_value = self.pipeline.default_transformer.parse_date_str(date_str=klaviyo_date, tries=0)
        if kdate_space != -1:
            date_value = self.pipeline.default_transformer.parse_date_str(date_str=klaviyo_date, tries=0, format=f'{datepart} %H:%M')
        elif kdate_len in [25, 26]:
            z = '' if kdate_len == 25 else 'Z'
            date_value = self.pipeline.default_transformer.parse_date_str(date_str=klaviyo_date, tries=0, format=f'{datepart}T%H:%M:%S{z}', offset=True)
        elif kdate_len == 10:
            date_value = self.pipeline.default_transformer.parse_date_str(date_str=klaviyo_date, tries=0, format=datepart)
        if ' AM' in klaviyo_date or ' PM' in klaviyo_date:
            fmt = f'{datepart} %H:%M %p'
            date_value = self.pipeline.default_transformer.parse_date_str(date_str=klaviyo_date, tries=0, format=fmt)
            bp = 'here'
        if isinstance(date_value, date):
            date_value = datetime(year=date_value.year, month=date_value.month, day=date_value.day)
        if not date_value:
            date_value = retry(date_str=klaviyo_date)
        return date_value