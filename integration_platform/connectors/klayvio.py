from __future__ import annotations
from typing import TYPE_CHECKING,  Any, Iterator
# if TYPE_CHECKING:
    # from integration_platform.pipelines
import logging
from integration_platform.config.settings import KLAYVIO
from integration_platform.helpers.klayvio_api_helper import KlayvioAPIHelper
import requests

class KlayvioAPI:
    def __init__(self, pipeline) -> None:
        self.pipeline = pipeline
        if type(pipeline) == str:
            self.logger = logging.getLogger(f'{pipeline}.KlayvioAPI')
        else:
            self.logger = logging.getLogger(f'{pipeline.pipeline_name}.KlayvioAPI')
        self.helper = KlayvioAPIHelper(self)
        self.headers = self.helper.format_headers(api_key=KLAYVIO['api_key'])
        self.base_url = 'https://a.klaviyo.com/api'
        self._set_urls_()
        pass


    def _set_urls_(self):
        self.url_lists = f'{self.base_url}/lists'
        self.url_profiles = f'{self.base_url}/profiles'



    def get_profiles(self):
        profiles = []
        parsed_reponse = self._get_data_(url=self.url_profiles)



    def _get_data_(self, url: str, params: str = '?page[size]=100'):
        full_url = f'{url}{params}'
        response = requests.get(url=full_url, headers=self.headers)
        parsed_response = self.helper.parse_response(response=response, url=full_url)
        return parsed_response



    def __page__(self, parsed_response: dict):
        paging_links = parsed_response.get('links')
        if paging_links == None:
            self.logger.info(f'No more pages found')
        bp = 'here'