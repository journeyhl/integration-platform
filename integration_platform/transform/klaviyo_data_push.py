from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.klaviyo_data_push import KlaviyoDataPush
import logging
import polars as pl
from datetime import datetime
from zoneinfo import ZoneInfo
import json
from typing import Literal
class Transform:
    def __init__(self, pipeline: KlaviyoDataPush):
        self.pipeline = pipeline
        self.default_transformer = pipeline.default_transformer
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.Transform')
        self.date_formats = {}
        pass

    #MARK: landing
    def landing(self, data_extract: pl.DataFrame):
        bp = 'here'
        data_extract_dicts = [
            {
                **r,
                'filter': f"equals(email,'{r['Email']}')",
            }
            for r in data_extract.to_dicts()
        ]
        extract_w_profiles = self._get_klaviyo_profiles_(data_extract=data_extract_dicts)
        formatted_extract = self._format_payloads_(extract_w_profiles=extract_w_profiles)
        bp = 'here'

    def _get_klaviyo_profiles_(self, data_extract):
        bp = 'here'
        records = len(data_extract)
        extract_w_profiles = {'update': [], 'create': []}
        for i, customer in enumerate(data_extract):
            profiles = self.pipeline.klaviyo.get_profiles(filter=customer['filter'])
            if profiles == []:
                customer['klavio_profile'] = {}
                extract_w_profiles['create'].append(customer)
                continue
            customer['klavio_profile'] = profiles[0] 
            extract_w_profiles['update'].append(customer)
        return extract_w_profiles


    def _format_payloads_(self, extract_w_profiles):
        bp = 'here'
        customers = extract_w_profiles['create']
        for i, customer in enumerate(customers):
            bp = 'here'
            payload = self.__format_payload__(customer=customer)
            bp = 'here'


    def __format_payload__(self, customer) -> dict:
        phone = customer['PhoneNumber'] if customer['PhoneNumber'][:2] == '+1' else f'+1{customer['PhoneNumber']}'
        payload = {
            'data': {
                'type': 'profile',
                'attributes': {
                    'email': customer['Email'],
                    'phone_number': phone,
                    'location': {
                        'city': customer['City'],
                        'region': customer['State'],
                        'zip': customer['ShippingZipCode']
                    },
                    'properties': {
                        'shipping_zip': customer['ShippingZipCode'],
                        
                    }
                }
            }
        }
        payload_properties = self.__add_property__(payload_properties=payload['data']['attributes']['properties'], key_name='Number of Orders', db_value=customer['NumberOfPurchases'])
        payload_properties = self.__add_property__(payload_properties=payload['data']['attributes']['properties'], key_name='$consent', db_value=customer['Consent'])
        payload_properties = self.__add_property__(payload_properties=payload['data']['attributes']['properties'], key_name='Accepts Marketing', db_value=customer['Consent'])
        payload_properties = self.__add_property__(payload_properties=payload['data']['attributes']['properties'], key_name='', db_value=customer[''])

        return payload

    def __add_property__(self, payload_properties, key_name, db_value):
        if not db_value and db_value != 0:
            return payload_properties
        payload_properties[key_name] = db_value
        return payload_properties