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
import copy
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
        return formatted_extract
        bp = 'here'

    #MARK: _get_klaviyo_profiles_
    def _get_klaviyo_profiles_(self, data_extract):
        bp = 'here'
        records = len(data_extract)
        extract_w_profiles = {'update': [], 'create': []}
        for i, customer in enumerate(data_extract):
            profiles = self.pipeline.klaviyo.get_profiles(filter=customer['filter'])
            if profiles == []:
                customer['klaviyo_profile'] = {}
                extract_w_profiles['create'].append(customer)
                continue
            customer['klaviyo_profile'] = profiles[0] 
            extract_w_profiles['update'].append(customer)
        return extract_w_profiles


    #MARK: _format_payloads_
    def _format_payloads_(self, extract_w_profiles):
        bp = 'here'
        payloads = {'create': [], 'update': []}
        for action, group in extract_w_profiles.items():
            for customer in group:
                bp = 'here'
                payload = self.pipeline.klaviyo.payload_profile if action == 'create' else {'data': customer['klaviyo_profile']}
                payload = self.__format_payload__(action=action, customer=customer, payload=payload)
                if payload != {}:
                    payloads[action].append(payload)
                bp = 'here'
        return payloads


    #MARK: __format_payload__
    def __format_payload__(self, action: Literal['update', 'create'], customer: dict, payload: dict) -> dict:
        phone = customer['PhoneNumber'] if customer['PhoneNumber'][:2] == '+1' else f'+1{customer['PhoneNumber']}'
        payload['data']['attributes']['email'] = customer['Email']
        payload['data']['attributes']['phone_number'] = phone
        if action == 'update':
            payload = self._format_update_payload_(customer=customer, payload=payload)
        else:
            payload = self._format_create_payload_(customer=customer, payload=payload)

        return payload

    #MARK: __format_update_payload__
    def _format_update_payload_(self, customer: dict, payload: dict):
        k_attr = {k: v for k, v in payload['data']['attributes'].items() if not isinstance(v, dict)}
        k_location = payload['data']['attributes'].get('location')
        k_properties = payload['data']['attributes'].get('properties')

        payload, present_prop_keys = self._compare_properties_(customer=customer, payload=payload)
        payload, present_attr_keys = self._compare_attributes_(customer=customer, payload=payload)
        return payload



    def _compare_attributes_(self, customer: dict, payload: dict):
        k_attr = {k: v for k, v in payload['data']['attributes'].items() if not isinstance(v, dict)}
        present_attr_keys = [k for k, v in k_attr.items()]
        for key, value in k_attr.items():
            was_list = False
            if isinstance(value, list):
                value = ','.join(value)
                was_list = True
            db_column_name = self.pipeline.klaviyo.map_attributes_update.get(key) or self.pipeline.klaviyo.map_attributes_update.get(key) or self.pipeline.klaviyo.map_attributes_update.get(key)
            db_value = customer.get(db_column_name) or customer.get(f'{db_column_name}_phone') or customer.get(f'{db_column_name}_email')
            if not db_value:
                # self.logger.info(f'{key}: Corresponding db value is blank{f', column not found' if not db_column_name else ''}')
                continue
            elif db_value != value:
                if value == '' or not value:                        
                    payload['data']['attributes'][key] = [db_value] if was_list else db_value
            elif db_value == value:
                self.logger.info(f'{key}: Klaviyo and db values match!')
            bp = 'here'
        return payload, present_attr_keys

    def _compare_properties_(self, customer: dict, payload: dict):
        k_properties = payload['data']['attributes'].get('properties')
        present_prop_keys = [k for k, v in k_properties.items()]
        for key, value in k_properties.items():
            was_list = False
            if isinstance(value, list):
                value = ','.join(value)
                was_list = True
            db_column_name = self.pipeline.klaviyo.map_properties_update.get(key) or self.pipeline.klaviyo.map_properties_update.get(key) or self.pipeline.klaviyo.map_properties_update.get(key)
            db_value = customer.get(db_column_name) or customer.get(f'{db_column_name}_phone') or customer.get(f'{db_column_name}_email')
            if not db_value:
                # self.logger.info(f'{key}: Corresponding db value is blank{f', column not found' if not db_column_name else ''}')
                continue
            elif db_value != value:
                if value == '' or not value:
                    self.logger.info(f'{key}: Updating klavio value from {value if value != '' else 'blank'} to {db_value}')
                    payload['data']['attributes']['properties'][key] = [db_value] if was_list else db_value
            elif db_value == value:
                self.logger.info(f'{key}: Klaviyo and db values match!')
            bp = 'here'
        return payload, present_prop_keys

    #MARK: __compare_values__
    def __compare_values__(self, klaviyo_dict: dict, kd_name: str, map: dict, customer: dict, payload: dict):
        update_db = []
        update_klaviyo = []
        email = customer['Email']
        self.logger.info(f"{email}: Comparing {len(klaviyo_dict)} Klaviyo {kd_name} values against db")
        for key, value in klaviyo_dict.items():
            date_value = None
            is_value_date = False if value is None or isinstance(value, int) or isinstance(value, float) else ':' in value and ('-' in value or '/' in value) and (isinstance(value, str)) 
            bp = 'here'
            map_key = map.get(key)
            if not map_key:
                self.logger.info(f'{email}: {key} not found')
                continue
            db_value =  customer.get(f'{map_key}_email') or customer.get(f'{map_key}_phone') or customer.get(map_key)
            if is_value_date:
                try:
                    date_value = self.default_transformer.parse_date_str(date_str=value, tries=0, format='%Y-%m-%dT%H:%M:%S', offset=True if '+' in str(value) else False) #type: ignore
                except Exception as e:
                    bp = 'here'

            if not db_value:
                # self.logger.info(f'{email}: No db value for {key}')
                update_db.append({key: value})
                continue
            elif db_value == value or (is_value_date and db_value == date_value):
                # self.logger.info(f'{email}: db and klaviyo {key} values match!')
                continue
            else:
                if date_value and is_value_date:
                    if  db_value <= date_value:
                        continue
                    else:
                        self.logger.info(f'{email}: Need to update klaviyo {key}')
                        bp = 'need to update klaviyo'
                bp = 'here'
            bp = 'here'
        self.logger.info(f'{len(update_klaviyo)} values need to be updated in Klaviyo')
        bp = 'here'



    #MARK: __format_create_payload__
    def _format_create_payload_(self, payload: dict, customer: dict):
        bp = 'do a compare or something here'
        for key, value in customer.items():
            if not value:
                continue
            k = key.replace('_phone', '').replace('_email', '')
            prop_match = self.pipeline.klaviyo.map_properties_create.get(key)
            attr_match = self.pipeline.klaviyo.map_attributes_create.get(key)
            loc_match = self.pipeline.klaviyo.map_location_create.get(key)
            if prop_match:
                bp = 'here'
                payload['data']['attributes']['properties'][prop_match] = value
                bp = 'here'
            if attr_match:
                bp = 'here'
                payload['data']['attributes'][attr_match] = value
                bp = 'here'
            if loc_match:
                bp = 'here'
                payload['data']['attributes']['location'][loc_match] = value
                bp = 'here'
            bp = 'here'
        return payload






    #MARK: __add_property__
    def __add_property__(self, payload_properties, key_name, db_value):
        if not db_value and db_value != 0:
            return payload_properties
        payload_properties[key_name] = db_value
        return payload_properties