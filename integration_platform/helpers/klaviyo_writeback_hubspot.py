
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
from integration_platform.config.klaviyo_hubspot_map import properties as property_map


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
            if profile['klaviyo'] == {}:
                self.logger.info(f'{self.prefix}No Klaviyo profile found, skipping')
                continue
            self.hubspot_id = profile['hubspot']['id']
            self.klaviyo_id = profile['klaviyo']['id']
            bp = 'here'
            hubspot = profile['hubspot']
            klaviyo_attributes = profile['klaviyo']['attributes']
            klaviyo_location = profile['klaviyo']['location']
            klaviyo_properties = profile['klaviyo']['properties']
            klaviyo_subscriptions = profile['klaviyo']['subscriptions']

            profile['diffs'] = {
                'attributes': self._compare_attributes_(h=hubspot, k=klaviyo_attributes),
                'location': self._compare_location_(h=hubspot, k=klaviyo_location),
                'properties': self._compare_properties_(h=hubspot, k=klaviyo_properties),
                'subscriptions': self._compare_subscriptions_(h=hubspot, k=klaviyo_subscriptions),
            }
        return contact_profiles


    #MARK: 
    def _compare_attributes_(self, h: dict, k: dict):
        bp = 'here'
        attributes = {
            'email': self._entry_formatter_(kvalue=k['email'], hvalue=h['email'], kkey='email', hkey='email'),
            'first_name': self._entry_formatter_(kvalue=k['first_name'], hvalue=h['firstname'], kkey='first_name', hkey='firstname'),
            'last_name': self._entry_formatter_(kvalue=k['last_name'], hvalue=h['lastname'], kkey='last_name', hkey='lastname'),
            'phone_number': self._entry_formatter_(kvalue=k['phone_number'], hvalue=h['phone'], kkey='phone_number', hkey='phone'),
        }
        return attributes

    #MARK: _compare_location_
    def _compare_location_(self, h: dict, k: dict):
        location = {
            'address1': self._entry_formatter_(kvalue=k['address1'], hvalue=h.get('shipping_address') or h.get('billing_address'), kkey='address1', hkey='shipping_address//billing_address'),
            # 'address2': self._entry_formatter_(kvalue=k['address2'], hvalue=h['shipping_'] or h['billing_']),
            'city': self._entry_formatter_(kvalue=k['city'], hvalue=h.get('shipping_city') or h.get('billing_city'), kkey='city', hkey='shipping_city//billing_city'),
            'country': self._entry_formatter_(kvalue=k['country'], hvalue=h['country'], kkey='country', hkey='country'),
            'region': self._entry_formatter_(kvalue=k['region'], hvalue=h.get('shipping_state') or h.get('billing_state'), kkey='region', hkey='shipping_state//billing_state'),
            'zip': self._entry_formatter_(kvalue=k['zip'], hvalue=h.get('shipping_zip') or h.get('billing_zip'), kkey='zip', hkey='shipping_zip//billing_zip'),
            # 'ip': self._entry_formatter_(kvalue=k['ip'], hvalue=h.get('shipping_city') or h.get('billing_city')),
        }
        return location
    
    #MARK: _compare_properties_
    def _compare_properties_(self, h: dict, k: dict):
        properties = {}
        map = property_map
        for kk, hk in map.items():
            if k.get(kk):
                if isinstance(hk, list):
                    for hkey in hk:
                        prop = self._entry_formatter_(k[kk], h.get(hkey), kkey=kk, hkey=hkey)
                        if prop['hubspot'] != None:
                            properties[kk] = prop
                            break
                        bp = 'here'
                else:
                    properties[kk] = self._entry_formatter_(k[kk], h.get(hk), kkey=kk, hkey=hk)
        bp = 'here'
        return properties

    #MARK: _compare_subscriptions_
    def _compare_subscriptions_(self, h: dict, k: dict):
        subscriptions = {
            'email':
            {
                # 'can_receive_marketing': 
            }
        }
        bp = 'here'
        return subscriptions

    #MARK: 
    def _entry_formatter_(self, kvalue, hvalue, kkey, hkey):
        entry = {'klaviyo': kvalue, 'hubspot': hvalue, 'update_hubspot': True, 'klaviyo_key': kkey, 'hubspot_key': hkey}
        if kvalue == hvalue:
            entry['update_hubspot'] = False
        return entry