from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.klaviyo_data_push import KlaviyoDataPush
import logging
import polars as pl
from datetime import datetime
from datetime import date
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
        customer_records = self._format_payloads_(extract_w_profiles=extract_w_profiles)
        return customer_records

    #MARK: _get_klaviyo_profiles_
    def _get_klaviyo_profiles_(self, data_extract):
        bp = 'here'
        records = len(data_extract)
        #region ood
        # extract_w_profiles = {'update': [], 'create': []}
        # for i, customer in enumerate(data_extract):
        #     profiles = self.pipeline.klaviyo.get_profiles(filter=f'filter={customer['filter']}')
        #     if profiles == []:
        #         customer['Action'] = 'Create'
        #         customer['klaviyo_profile'] = {}
        #         extract_w_profiles['create'].append(customer)
        #         continue
        #     customer['Action'] = 'Update'
        #     customer['klaviyo_profile'] = profiles[0] 
        #     extract_w_profiles['update'].append(customer)
        #endregion
        profile_extract = []
        for i, customer in enumerate(data_extract):
            profiles = self.pipeline.klaviyo.get_profiles(filter=f'filter={customer['filter']}')
            if profiles == []:
                customer['Action'] = 'Create'
                customer['klaviyo_profile'] = {}
            else:                
                customer['Action'] = 'Update'
                customer['klaviyo_profile'] = profiles[0] 
            profile_extract.append(customer)
        return profile_extract


    #MARK: _format_payloads_
    def _format_payloads_(self, extract_w_profiles):
        bp = 'here'
        #region ood
        # customers = {'create': [], 'update': []}
        # for action, group in extract_w_profiles.items():
        #     for customer in group:
        #         bp = 'here'
        #         payload = self.pipeline.klaviyo.payload_profile if action == 'create' else {'data': customer['klaviyo_profile']}
        #         customer_record = self.__format_payload__(action=action, customer=customer, payload=payload)
        #         customers[action].append(customer_record)
        #         bp = 'here'
        #endregion    
        bp = 'here'
        customers = []
        for customer in extract_w_profiles:
            bp = 'here'
            payload = self.pipeline.klaviyo.payload_profile if customer['Action'] == 'Create' else {'data': customer['klaviyo_profile']}
            customer_record = self.__format_payload__(action=customer['Action'], customer=customer, payload=payload)
            customers.append(customer_record)
            bp = 'here'
        return customers


    #MARK: __format_payload__
    def __format_payload__(self, action: Literal['Update', 'Create'], customer: dict, payload: dict) -> dict:
        fields_changed = None
        customer_record = {}
        phone = customer['PhoneNumber'] if customer['PhoneNumber'][:2] == '+1' else f'+1{customer['PhoneNumber']}'
        payload['data']['attributes']['email'] = customer['Email']
        payload['data']['attributes']['phone_number'] = phone
        if action == 'Update':
            customer_record = self._format_update_payload_(customer=customer, payload=payload)
            fields_changed = customer_record['fields_changed'] if customer_record['fields_changed'] != [] else None
            bp = 'here'
        customer_record = self._format_create_payload_(customer=customer, payload=payload, action=action, update_customer_record=customer_record)
        customer_record['fields_changed'] = fields_changed
        return customer_record

    #MARK: __format_update_payload__
    def _format_update_payload_(self, customer: dict, payload: dict):
        k_location = payload['data']['attributes'].get('location')
        
        prop_record = self._compare_attributes_or_properties_(customer=customer, payload=payload, attr_or_prop='properties')
        attr_record = self._compare_attributes_or_properties_(customer=customer, payload=prop_record['payload'], attr_or_prop='attributes')
        fields_changed = prop_record['_updated'] + (attr_record['_updated'] or [])
        check_these = prop_record['_check_these'] + (attr_record['_check_these'] or [])
        matches = prop_record['_matches'] + (attr_record['_matches'] or [])

        customer_record = {
            'action': 'Update',
            'payload': attr_record['payload'],
            'db': attr_record['db'],
            'fields_changed': fields_changed,
            'check_these': check_these,
            'matches': matches,
        }
        return customer_record

    #MARK: _compare_attributes_or_properties_
    def _compare_attributes_or_properties_(self, customer: dict, payload: dict, attr_or_prop: Literal['attributes', 'properties']):
        klaviyo_values = payload['data']['attributes'].get('properties') if attr_or_prop == 'properties' else {k: v for k, v in payload['data']['attributes'].items() if not isinstance(v, dict)}
        self._updated = []
        self._check_these = []
        self._matched = []
        for i, (key, value) in enumerate(klaviyo_values.items()):
            dict_key = f'{attr_or_prop}.{key}'
            was_list = False
            if isinstance(value, list):
                value = ','.join(value)
                was_list = True
            db_column_name = self.pipeline.klaviyo.map_attributes_update.get(key) or self.pipeline.klaviyo.map_properties_update.get(key)
            db_value = customer.get(db_column_name) or customer.get(f'{db_column_name}_phone') or customer.get(f'{db_column_name}_email')
            if not db_value:
                continue
            elif db_value != value:
                if value == '' or not value:
                    self.logger.info(f'{key}: Updating from blank to {db_value}')
                    self._updated.append({dict_key: {'old': value, 'new': db_value}})
                    payload = self._add_profile_datapoint_(payload=payload, attr_or_prop=attr_or_prop, was_list=was_list, key=key, db_value=db_value, old_value=value)
                    continue
                else:
                    if isinstance(db_value, datetime) or isinstance(db_value, date):
                        payload = self._compare_attributes_properties_dates_(customer=customer, payload=payload, attr_or_prop=attr_or_prop, was_list=was_list, key=key, db_value=db_value, value=value)
                        continue
                    elif isinstance(value, int):
                        if key == '$source':
                            continue
                        if key == '$consent_form_version':
                            db_value = self.default_transformer.string_to_int(db_value)
                            if value == db_value:
                                continue
                            else:
                                payload = self._add_profile_datapoint_(payload=payload, attr_or_prop=attr_or_prop, was_list=was_list, key=key, db_value=db_value, old_value=value)
                                continue
                            
                    elif isinstance(value, str):
                        if isinstance(db_value, str) and value.replace(' ', '').lower() == db_value.lower():
                            continue
                        elif 'zip' in key.lower():
                            v = value[:5]
                            if v == db_value:
                                continue
                            else:
                                payload = self._add_profile_datapoint_(payload=payload, attr_or_prop=attr_or_prop, was_list=was_list, key=key, db_value=db_value, old_value=value)
                                continue
                        elif key == 'Hubspot Record ID':
                            payload = self._add_profile_datapoint_(payload=payload, attr_or_prop=attr_or_prop, was_list=was_list, key=key, db_value=db_value, old_value=value)
                            continue
                        elif key == 'phone_number':
                            value = f'{'+1' if value[:2] != '+1' else ''}{value.replace('-', '')}'
                            db_value = f'{'+1' if db_value[:2] != '+1' else ''}{db_value.replace('-', '')}'
                            if value != db_value:
                                bp = 'here'
                        elif isinstance(db_value, int):
                            if self.default_transformer.string_to_int(value) == db_value:
                                payload = self._add_profile_datapoint_(payload=payload, attr_or_prop=attr_or_prop, was_list=was_list, key=key, db_value=db_value, old_value=value)
                                continue
                        else:
                            payload = self._add_profile_datapoint_(payload=payload, attr_or_prop=attr_or_prop, was_list=was_list, key=key, db_value=db_value, old_value=value)
                            continue

                    self._check_these.append({dict_key: {'klaviyo': value, 'db': db_value}})
                    # self.logger.info(f"{key}: Values don't match, but not updating...")
                    bp = 'here'
            elif db_value == value:
                self._matched.append({dict_key: value})
                bp = 'here'
        bp = 'here'
        payload['data'].pop('links', None)
        payload['data'].pop('relationships', None)
        payload['data']['attributes'].pop('subscriptions', None)
        payload['data']['attributes'].pop('predictive_analytics', None)
        payload['data']['attributes'].pop('updated', None)
        payload['data']['attributes'].pop('created', None)
        payload['data']['attributes'].pop('last_event_date', None)
        

        customer_record = {
            'payload': payload,
            'db': customer,
            '_updated': self._updated,
            '_check_these': self._check_these,
            '_matches': self._matched,
        }
        return customer_record

        

    #MARK: _compare_attributes_properties_dates_
    def _compare_attributes_properties_dates_(self, customer: dict, payload: dict, attr_or_prop: Literal['attributes', 'properties'], was_list, key, db_value, value):
        if isinstance(db_value, date):
            db_value = datetime(year=db_value.year, month=db_value.month, day=db_value.day)
        date_value = self._parse_and_compare_dates_(klaviyo_date=value, db_date=db_value)
        if date_value:
            if date_value < db_value:
                db_value = db_value.strftime('%Y/%m/%dT%H:%M:%SZ')
                self.logger.info(f'{key}: Updating from {date_value} to {db_value}')
                self._updated.append({f'{attr_or_prop}.{key}': {'old': value, 'new': db_value}})
                payload = self._add_profile_datapoint_(payload=payload, attr_or_prop=attr_or_prop, was_list=was_list, key=key, db_value=db_value, old_value=value)
            elif date_value > db_value:
                self.logger.info(f'{key}: Updating from {date_value} to {db_value}')
                self._check_these.append({f'{attr_or_prop}.{key}': {'klaviyo': value, 'db': db_value}})
        return payload
            
    #MARK: _parse_and_compare_dates_
    def _parse_and_compare_dates_(self, klaviyo_date: str, db_date: datetime | date) -> datetime | None:
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
        date_value = self.default_transformer.parse_date_str(date_str=klaviyo_date, tries=0)
        if kdate_space != -1:
            date_value = self.default_transformer.parse_date_str(date_str=klaviyo_date, tries=0, format=f'{datepart} %H:%M')
        elif kdate_len in [25, 26]:
            z = '' if kdate_len == 25 else 'Z'
            date_value = self.default_transformer.parse_date_str(date_str=klaviyo_date, tries=0, format=f'{datepart}T%H:%M:%S{z}', offset=True)
        elif kdate_len == 10:
            date_value = self.default_transformer.parse_date_str(date_str=klaviyo_date, tries=0, format=datepart)
        if ' AM' in klaviyo_date or ' PM' in klaviyo_date:
            fmt = f'{datepart} %H:%M %p'
            date_value = self.default_transformer.parse_date_str(date_str=klaviyo_date, tries=0, format=fmt)
            bp = 'here'
        if isinstance(date_value, date):
            date_value = datetime(year=date_value.year, month=date_value.month, day=date_value.day)

        return date_value


    #MARK: _add_profile_datapoint_
    def _add_profile_datapoint_(self, payload: dict, attr_or_prop: Literal['attributes', 'properties'], was_list: bool,  key: str, db_value, old_value):
        ''':class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform._add_profile_datapoint_`
        ---
        
        Given the klaviyo profile payload, the subdict within the payload that will be 
        updated, whether or not the value is a list, the key and the actual value to
        change to, add the key and new value to payload
        
        Parameters
        ---
        :param (*dict*) `payload`: payload to be sent to klaviyo
        :param (*Literal['attributes', 'properties']*) `attr_or_prop`: `attributes` or `properties` portion of profile payload
        :param (*bool*) `was_list`: was this value a list in the data pull from klaviyo? If yes, we'll need to make sure its a list when we send again
        :param (*str*) `key`: the property's id in klaviyo
        :param (*_type_*) `db_value`: value from db that we will be sending to klaviyo
        
        Returns
        ---
        :return `variablename` (dict): `payload` with added key and value
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform._compare_attr_prop_`
        '''        
        self.logger.info(f'{key}: Updating from {old_value if old_value and old_value != '' else 'blank'} to {db_value}')
        self._updated.append({f'{attr_or_prop}.{key}': {'old': old_value, 'new': db_value}})
        if attr_or_prop == 'properties':
            payload['data']['attributes']['properties'][key] = [db_value] if was_list else db_value
        else:
            payload['data']['attributes'][key] = [db_value] if was_list else db_value
        return payload

        



    #MARK: __format_create_payload__
    def _format_create_payload_(self, payload: dict, customer: dict, action: Literal['Create', 'Update'], update_customer_record: dict):
        bp = 'do a compare or something here'
        fields_added = []
        for key, value in customer.items():
            if not value:
                continue
            k = key.replace('_phone', '').replace('_email', '')
            prop_match = self.pipeline.klaviyo.map_properties_create.get(key)
            attr_match = self.pipeline.klaviyo.map_attributes_create.get(key)
            loc_match = self.pipeline.klaviyo.map_location_create.get(key)
            if prop_match:
                payload['data']['attributes']['properties'], fields_added = self._match_payload_values_(payload_section=payload['data']['attributes']['properties'], match_key=prop_match, value=value, matched=fields_added, list_prepend='properties.')
            if attr_match and attr_match != 'email':
                payload['data']['attributes'], fields_added = self._match_payload_values_(payload_section=payload['data']['attributes'], match_key=attr_match, value=value, matched=fields_added, list_prepend='attributes.')
            if loc_match:
                payload['data']['attributes']['location'], fields_added = self._match_payload_values_(payload_section=payload['data']['attributes']['location'], match_key=loc_match, value=value, matched=fields_added, list_prepend='location.')
            bp = 'here'
        customer_record = {
            'action': action,
            'payload': payload,
            'db': customer,
            'fields_added': fields_added if fields_added != [] else None
        }
        return customer_record

    #MARK: _match_payload_values_
    def _match_payload_values_(self, payload_section: dict, match_key: str, value, matched: list, list_prepend: str):
        klaviyo_value = payload_section.get(match_key)
        if isinstance(klaviyo_value, str) and isinstance(value, str):
            klaviyo_value = klaviyo_value.lower()
            value = value.lower()
        if klaviyo_value != value:
            if match_key == 'phone_number':
                if klaviyo_value and value in klaviyo_value: #If the db's tfn is within klaviyos. (db doesn't have +1 and klaviyo does)
                    return payload_section, matched
            payload_section[match_key] = value
            self.logger.info(f'{match_key} updated from {klaviyo_value} to {value}')
            matched.append({f'{list_prepend}{match_key}': {'old': klaviyo_value, 'new': value}})
        return payload_section, matched
            





    #MARK: __add_property__
    def __add_property__(self, payload_properties, key_name, db_value):
        if not db_value and db_value != 0:
            return payload_properties
        payload_properties[key_name] = db_value
        return payload_properties