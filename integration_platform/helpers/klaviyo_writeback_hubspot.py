
from __future__ import annotations
from typing import TYPE_CHECKING, Literal
if TYPE_CHECKING:
    from integration_platform.pipelines.klaviyo_writeback_hubspot import KlaviyoWritebackHubspot
import logging
import requests
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from requests import Response
import polars as pl
from integration_platform.config.klaviyo_hubspot_map import properties


class KlaviyoHubspotComparer:
    def __init__(self, pipeline: KlaviyoWritebackHubspot) -> None:
        ''':class:`~integration_platform.helpers.klaviyo_writeback_hubspot.KlaviyoHubspotComparer`
        ---
        
        Used to compare properties from klaviyo to the corresponding property in hubspot
        
        

        # Methods

        - ### :class:`~integration_platform.helpers.klaviyo_writeback_hubspot.KlaviyoHubspotComparer`.:meth:`~integration_platform.helpers.klaviyo_writeback_hubspot.KlaviyoHubspotComparer.landing`
        - ### :class:`~integration_platform.helpers.klaviyo_writeback_hubspot.KlaviyoHubspotComparer`.:meth:`~integration_platform.helpers.klaviyo_writeback_hubspot.KlaviyoHubspotComparer._compare_attributes_`
        '''        
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.KlaviyoHubspotComparer')        


    def landing(self, contact_profiles: list):
        bp = 'here'
        total = len(contact_profiles)
        for i, profile in enumerate(contact_profiles):
            self.prefix = f'{i+1}/{total}, {profile['db']['ID']}-{profile['db']['HubspotRecordID']}: '
            if profile['hubspot'] == {}:
                self.logger.info(f'{self.prefix}No hubspot profile found, skipping')
                continue
            self.hubspot_id = profile['hubspot']['id']
            self.klaviyo_id = profile['klaviyo']['id']
            bp = 'here'
            hubspot = profile['hubspot']
            klaviyo_attributes = profile['klaviyo']['attributes']
            klaviyo_location = profile['klaviyo']['location']
            klaviyo_properties = profile['klaviyo']['properties']
            klaviyo_subscriptions = profile['klaviyo']['subscriptions']

            diff_attributes = self._compare_attributes_(h=hubspot, k=klaviyo_attributes)
            diff_location = self._compare_location_(h=hubspot, k=klaviyo_location)
            diff_properties = self._compare_properties_(h=hubspot, k=klaviyo_properties)
            diff_subscriptions = self._compare_subscriptions_(h=hubspot, k=klaviyo_subscriptions)
            bp = 'here'
        bp = 'here'



    def _compare_attributes_(self, h: dict, k: dict):
        bp = 'here'
        attributes = {
            'email': self._entry_formatter_(kvalue=k['email'], hvalue=h['email']),
            'first_name': self._entry_formatter_(k['first_name'], h['firstname']),
            'last_name': self._entry_formatter_(k['last_name'], h['lastname']),
            'phone_number': self._entry_formatter_(k['phone_number'], h['phone'])
        }
        return attributes

    def _compare_location_(self, h: dict, k: dict):
        location = {
            'address1': self._entry_formatter_(kvalue=k['address1'], hvalue=h.get('shipping_address') or h.get('billing_address')),
            # 'address2': self._entry_formatter_(kvalue=k['address2'], hvalue=h['shipping_'] or h['billing_']),
            'city': self._entry_formatter_(kvalue=k['city'], hvalue=h.get('shipping_city') or h.get('billing_city')),
            'country': self._entry_formatter_(kvalue=k['country'], hvalue=h['country']),
            'region': self._entry_formatter_(kvalue=k['region'], hvalue=h.get('shipping_state') or h.get('billing_state')),
            'zip': self._entry_formatter_(kvalue=k['zip'], hvalue=h.get('shipping_zip') or h.get('billing_zip')),
            # 'ip': self._entry_formatter_(kvalue=k['ip'], hvalue=h.get('shipping_city') or h.get('billing_city')),
        }
        bp = 'here'
    
    def _compare_properties_(self, h: dict, k: dict):
        properties = {

        }
        bp = 'here'

    def _compare_subscriptions_(self, h: dict, k: dict):
        subscriptions = {

        }
        bp = 'here'

    def _entry_formatter_(self, kvalue, hvalue):
        entry = {'klaviyo': kvalue, 'hubspot': hvalue}
        return entry