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
from decimal import Decimal
class Transform:
    def __init__(self, pipeline: KlaviyoDataPush):
        self.pipeline = pipeline
        self.default_transformer = pipeline.default_transformer
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.Transform')
        self.date_formats = {}
        pass

    #MARK: landing
    def landing(self, data_extract: pl.DataFrame):
        ''':class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform.landing`
        ---
        
        Landing method called from :meth:`~integration_platform.pipelines.klaviyo_data_push.KlaviyoDataPush.transform` step of :class:`~integration_platform.pipelines.klaviyo_data_push.KlaviyoDataPush` pipeline. We'll return our completed output from here
        
        Parameters
        ---
        :param (*pl.DataFrame*) `data_extract`: dataframe of customers returned from sql query. Query pulls hubspot customers left joined to Klaviyo tables
        
        Returns
        ---
        :return `customer_records` (list): list of dicts of customer data. Contains **`action`**, **`payload`**, **`db`**, **`fields_added`** and **`fields_changed`**
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.pipelines.klaviyo_data_push.KlaviyoDataPush`.:meth:`~integration_platform.pipelines.klaviyo_data_push.KlaviyoDataPush.transform`
        
        ## Downstream Calls (Methods/Functions called)
        
         ### :class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform._get_klaviyo_profiles_`
        
          - Gets profile data from klaviyo
        
         ### :class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform._format_payloads_`
           
          - Drives transformation of payloads to send back to klaviyo
        '''        
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
        customer_records = self.consolidate_duplicates(customer_records=customer_records)
        consent = self._check_consent_(customer_records=customer_records)
        consent_updates, historic_consent_updates, customer_records = self._compare_consent_(customer_records=customer_records)
        customers_and_subscriptions = {
            'customer_records': customer_records,
            'consent_updates': consent_updates,
            'historic_consent_updates': historic_consent_updates
        }
        return customers_and_subscriptions

    def consolidate_duplicates(self, customer_records: list[dict]) -> list[dict]:
        ''':class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform.consolidate_duplicates`
        ---
        
        Given the list of customer records, check to make sure that we only have one record per email
        
        Parameters
        ---
        :param (*list[dict]*) `customer_records`: list of customer_records with db data, fields_added, fields_changed, and payload
        
        Returns
        ---
        :return `variablename` (list[dict]): _description_
        
        <hr>
        
        Sets
        ---
        - #### ____replace_with_class_level_variable_pls____
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform.landing`
        
          - Called before checking consent data
           
        '''        
        emails = {}
        for record in customer_records:
            email = record['db']['Email']
            if emails.get(email):
                if record['fields_added'] == emails[email]['fields_added'] and record['fields_changed'] == emails[email]['fields_changed'] :
                    continue
                elif not record['fields_added'] and not record['fields_changed']:
                    continue
                else:
                    if not emails[email]['fields_added']:
                        emails[email]['fields_added'] = record['fields_added']
                    if not emails[email]['fields_changed']:
                        emails[email]['fields_changed'] = record['fields_changed']
                bp = 'here'
            else:
                emails[email] = record
        customer_records = [value for k, value in emails.items()]
        return customer_records
        # test = pl.DataFrame(payloads, infer_schema_length=None)

    #MARK: _get_klaviyo_profiles_
    def _get_klaviyo_profiles_(self, data_extract: list[dict]):
        ''':class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform._get_klaviyo_profiles_`
        ---
        
        First method called from :class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform.landing`

        For each customer extracted from the database, hits KlaviyoAPI's profiles endpoint and checks for a profile match by email

        If a match is found, we'll go about updating the record, if not, we'll create one
        
        Parameters
        ---
        :param (*list[dict]*) `data_extract`: list of dicts(rows) extracted from the database of customers to look for in klaviyo
        
        Returns
        ---
        :return `profile_extract` (list[dict]): same list of dicts, but with the profile data from klaviyo if found, or an empty dict if not, as `klaviyo_profile`
        
        <hr>
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform.landing`
        
        ## Downstream Calls (Methods/Functions called)
        
         ### :class:`~integration_platform.connectors.klaviyo.KlaviyoAPI`.:meth:`~integration_platform.connectors.klaviyo.KlaviyoAPI.get_profiles`
        '''        
        records = len(data_extract)
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
    def _format_payloads_(self, extract_w_profiles: list[dict]):
        ''':class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform._format_payloads_`
        ---
        
        Formats the header level structure for the payload depending on if the profile should be created or updated, then passes to :meth:`~integration_platform.transform.klaviyo_data_push.Transform.__format_payload__` 
        
        Parameters
        ---
        :param (*list[dict]*) `extract_w_profiles`: list of dicts that was returned from :class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform._get_klaviyo_profiles_`.
        
        Returns
        ---
        :return `customer_records` (list[dict]): list of dicts of customer data. Each dict contains **`action`**, **`payload`**, **`db`**, **`fields_added`** and **`fields_changed`**
        
        <hr>
        
        Sets
        ---
        - #### self.:attr:`~integration_platform.transform.klaviyo_data_push.Transform.current_customer_email`
        - #### self.:attr:`~integration_platform.transform.klaviyo_data_push.Transform.current_prefix`

        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform.landing`
        
          - Called **second** from :class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform.landing`,  after look up of klaviyo profile
        
        ## Downstream Calls (Methods/Functions called)
        
         ### :class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform.__format_payload__`
        
          - Does all the work of formatting the payload, determining what values should be sent and so on
        '''        
        customer_records = []
        total = len(extract_w_profiles)
        for i, customer in enumerate(extract_w_profiles):
            self.current_customer_email = customer['Email']
            self.current_prefix = f'{i+1}/{total}, {self.current_customer_email}: '
            payload = self.pipeline.klaviyo.payload_profile if customer['Action'] == 'Create' else {'data': customer['klaviyo_profile']}
            customer_record = self.__format_payload__(action=customer['Action'], customer=customer, payload=payload)
            customer_records.append(customer_record)
        return customer_records

    #MARK: __format_payload__
    def __format_payload__(self, action: Literal['Update', 'Create'], customer: dict, payload: dict) -> dict:
        ''':class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform.__format_payload__`
        ---
        
        Base level of iteration through database extract. We're passed a single customer, payload and action, which we then pass on to submethods and functions that
        handle the parsing and formatting. After that's returned, we do one last step of formatting to each customer's dict of data, then pass it back to our main iterator
        
        Parameters
        ---
        :param (Literal[`Update`, `Create`]) `action`: Whether or not the klaviyo profile is to be updated or created
        :param (*dict*) `customer`: A particular customer's data that was extracted from the db
        :param (*dict*) `payload`: The payload to be sent to klaviyo containing that customer's profile data
        
        Returns
        ---
        :return `customer_record` (list[dict]): dict of customer data. Contains **`action`**, **`payload`**, **`db`**, **`fields_added`** and **`fields_changed`**
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform._format_payloads_`
        
          - Called from to get a payload for each customer
        
        ## Downstream Calls (Methods/Functions called)
        
         ### :class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform._format_update_payload_`
        
          - If the profile exists, handle the field update portion, skip if we're creating profile
        
         ### :class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform._format_create_payload_`
           
          - Checks for any non-null db values we can add in the payload to klaviyo
        '''        
        fields_changed = None
        klaviyo_response = None
        customer_record = {}
        phone = customer['PhoneNumber'] or customer['RawPhoneNumber_email']
        if phone:
            phone = phone if phone[:2] == '+1' else f'+1{phone}'
        payload['data']['attributes']['phone_number'] = phone

        payload['data']['attributes']['email'] = customer['Email']

        if action == 'Update':
            customer_record = self._format_update_payload_(customer=customer, payload=payload)
            fields_changed = customer_record['fields_changed'] if customer_record['fields_changed'] != [] else None
            klaviyo_response = customer_record['klaviyo_response']
        customer_record = self._format_create_payload_(customer=customer, payload=payload, action=action, update_customer_record=customer_record)
        customer_record['fields_changed'] = fields_changed
        customer_record['klaviyo_response'] = klaviyo_response
        customer_record['payload'] = self._pop_fields_(payload=payload)
        return customer_record

    #MARK: __format_update_payload__
    def _format_update_payload_(self, customer: dict, payload: dict) -> dict:
        ''':class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform._format_update_payload_`
        ---
        
        If the action is update, format the payload to be sent to update the customer's profile in klaviyo
        
        Parameters
        ---
        :param (*dict*) `customer`: A particular customer's data that was extracted from the db
        :param (*dict*) `payload`: The payload to be sent to klaviyo containing that customer's profile data
        
        Returns
        ---
        :return `customer_record` (list[dict]): dict of customer data. Contains **`action`**, **`payload`**, **`db`**, **`fields_changed`**, **`check_these`** and **`matches`**
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform.__format_payload__`
        
          - Called if action == `Update`
        
        ## Downstream Calls (Methods/Functions called)
        
         ### :class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform._format_update_payload_`
        
          - Called twice, once to compare properties, and once for attribute comparison
        '''        
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
            'klaviyo_response': prop_record['klaviyo_response'],
        }
        return customer_record

    #MARK: _compare_attributes_or_properties_
    def _compare_attributes_or_properties_(self, customer: dict, payload: dict, attr_or_prop: Literal['attributes', 'properties']):
        ''':class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform._compare_attributes_or_properties_`
        ---
        
        Given customer data from the database, `customer`, the profile data retrieved from klaviyo, `payload`, and the dict to look at, compare the values from klaviyo and the db
        
        Parameters
        ---
        :param (*dict*) `customer`: A particular customer's data that was extracted from the db
        :param (*dict*) `payload`: The payload to be sent to klaviyo containing that customer's profile data
        :param (*Literal[`attributes`, `properties`]*) `attr_or_prop`: Which part of klaviyo's profile payload are we comparing
        
        Returns
        ---
        :return `customer_record` (dict): dict of customer data. Contains **`action`**, **`payload`**, **`db`**, **`_updated`**, **`_check_these`** and **`_matches`**

        <hr>
        
        Sets
        ---
        - #### self.:attr:`~integration_platform.transform.klaviyo_data_push.Transform._updated`
        - #### self.:attr:`~integration_platform.transform.klaviyo_data_push.Transform._check_these`
        - #### self.:attr:`~integration_platform.transform.klaviyo_data_push.Transform._matched`

        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform._format_update_payload_`
        
          - Calls twice, once to compare properties, and once for attribute comparison
        
        ## Downstream Calls (Methods/Functions called)
        
         ### :class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform._add_profile_datapoint_`
        
          - Adds new value to klaviyo payload
        
         ### :class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform._compare_attributes_properties_dates_`
           
          - Compares a date value from the db to a text value from klaviyo
        '''        
        klaviyo_values = payload['data']['attributes'].get('properties') if attr_or_prop == 'properties' else {k: v for k, v in payload['data']['attributes'].items() if not isinstance(v, dict)}
        self._updated = []
        self._check_these = []
        self._matched = []
        for i, (key, value) in enumerate(klaviyo_values.items()):
            dict_key = f'{attr_or_prop}.{key}'
            was_list = False
            if isinstance(value, list):
                if len(value) > 0 and isinstance(value[0], dict): continue
                value = ','.join(value)
                was_list = True
            db_column_name = self.pipeline.klaviyo.map_attributes_update.get(key) or self.pipeline.klaviyo.map_properties_update.get(key)
            db_value = customer.get(db_column_name) or customer.get(f'{db_column_name}_phone') or customer.get(f'{db_column_name}_email')
            if not db_value:
                continue
            elif db_value != value:
                if value == '' or not value:
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
                            if 'e+' in db_value.lower():
                                continue
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
        payload_fmt = self._pop_fields_(payload=payload)
        

        customer_record = {
            'payload': payload_fmt,
            'db': customer,
            '_updated': self._updated,
            '_check_these': self._check_these,
            '_matches': self._matched,
            'klaviyo_response': payload
        }
        return customer_record

    def _pop_fields_(self, payload: dict):
        payload_fmt = copy.deepcopy(payload)
        payload_fmt['data'].pop('links', None)
        payload_fmt['data'].pop('relationships', None)
        payload_fmt['data']['attributes'].pop('subscriptions', None)
        payload_fmt['data']['attributes'].pop('predictive_analytics', None)
        payload_fmt['data']['attributes'].pop('updated', None)
        payload_fmt['data']['attributes'].pop('created', None)
        payload_fmt['data']['attributes'].pop('last_event_date', None)
        return payload_fmt


    #MARK: _compare_attributes_properties_dates_
    def _compare_attributes_properties_dates_(self, customer: dict, payload: dict, attr_or_prop: Literal['attributes', 'properties'], was_list, key, db_value, value):
        ''':class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform._compare_attributes_properties_dates_`
        ---
        
        If the value from the database to compare to klaviyo is a date, this method is called to cast klaviyo's value as a date, then compare
        
        Parameters
        ---
        :param (*dict*) `customer`: A particular customer's data that was extracted from the db
        :param (*dict*) `payload`: The payload to be sent to klaviyo containing that customer's profile data
        :param (*Literal[`attributes`, `properties`]*) `attr_or_prop`: Which part of klaviyo's profile payload are we comparing
        :param (*_type_*) `was_list`: Was this value a list type?
        :param (*_type_*) `key`: the klaviyo dict key
        :param (*_type_*) `db_value`: the value from the database
        :param (*_type_*) `value`: the value from klaviyo
        
        Returns
        ---
        :return `payload` (dict): Updated (or not) payload of profile data to send to klaviyo
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform._compare_attributes_or_properties_`
        
          - Called when comparing klaviyo values to those of db, when db value is a datetime
        
        ## Downstream Calls (Methods/Functions called)
        
         ### :class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform.__parse_and_compare_dates__`
        
          - Does the actual parsing of the string from klaviyo, then casts as datetime
        
         ### :class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform._add_profile_datapoint_`
           
          - Adds new value to klaviyo payload and appends to :attr:
        '''
        if isinstance(db_value, date):
            db_value = datetime(year=db_value.year, month=db_value.month, day=db_value.day)
        date_value = self.__parse_and_compare_dates__(klaviyo_date=value)
        if date_value:
            if date_value < db_value:
                db_value = db_value.strftime('%Y/%m/%dT%H:%M:%SZ')
                payload = self._add_profile_datapoint_(payload=payload, attr_or_prop=attr_or_prop, was_list=was_list, key=key, db_value=db_value, old_value=value)
            elif date_value > db_value:
                self.logger.warning(f'{self.current_prefix} {key}: CHECK THIS! from {date_value} to {db_value}')
                self._check_these.append({f'{attr_or_prop}.{key}': {'klaviyo': value, 'db': db_value}})
        return payload
            
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
                date_value = self.default_transformer.parse_date_str(date_str=klaviyo_date, tries=0, format=format)
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
        if not date_value:
            date_value = retry(date_str=klaviyo_date)
        return date_value


    #MARK: _add_profile_datapoint_
    def _add_profile_datapoint_(self, payload: dict, attr_or_prop: Literal['attributes', 'properties'], was_list: bool,  key: str, db_value, old_value):
        ''':class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform._add_profile_datapoint_`
        ---
        
        Given the klaviyo profile payload, **`payload`**, the subdict within the payload that will be 
        updated ,**`attr_or_prop`**, whether or not the value is a list, **`was_list`**, the key, **`key`**, and the actual value to
        change to, **`db_value`**, add the key and new value to payload
        
        Parameters
        ---
        :param (*dict*) `payload`: payload to be sent to klaviyo
        :param (*Literal['attributes', 'properties']*) `attr_or_prop`: `attributes` or `properties` portion of profile payload
        :param (*bool*) `was_list`: was this value a list in the data pull from klaviyo? If yes, we'll need to make sure its a list when we send again
        :param (*str*) `key`: the property's id in klaviyo
        :param  `db_value`: value from db that we will be sending to klaviyo
        :param  `old_value`: value changing from. Only used for logging output and tracking
        
        Returns
        ---
        :return `variablename` (dict): `payload` with added key and value
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform._compare_attr_prop_`
        '''
        self.logger.info(f'{self.current_prefix}{key}: Updating from {old_value if old_value and old_value != '' else 'blank'} to {db_value}')
        if isinstance(db_value, Decimal):
            db_value = float(db_value)
        self._updated.append({f'{attr_or_prop}.{key}': {'old': old_value, 'new': db_value}})
        if attr_or_prop == 'properties':
            payload['data']['attributes']['properties'][key] = [db_value] if was_list else db_value
        else:
            payload['data']['attributes'][key] = [db_value] if was_list else db_value
        return payload

        



    #MARK: __format_create_payload__
    def _format_create_payload_(self, payload: dict, customer: dict, action: Literal['Create', 'Update'], update_customer_record: dict) -> dict:
        ''':class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform._format_create_payload_`
        ---
        
        Formats portion of payload to send to klaviyo that fills in values from the database that aren't captured at Klaviyo
        If updating, this is only some or no fields, if creating, all the data we send will be added from here
        
        Parameters
        ---
        :param (*dict*) `customer`: A particular customer's data that was extracted from the db
        :param (*dict*) `payload`: The payload to be sent to klaviyo containing that customer's profile data
        :param (*Literal[`attributes`, `properties`]*) `attr_or_prop`: Which part of klaviyo's profile payload are we comparing
        :param (*dict*) `update_customer_record`: _description_
        
        Returns
        ---
        :return `customer_record` (dict): dict of customer data. Contains **`action`**, **`payload`**, **`db`** and **`fields_added`**
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform.__format_payload__`
        
          - Called regardless of action
        
        ## Downstream Calls (Methods/Functions called)
        
         ### :class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform._match_payload_values_`
        
          - Called if there's a match in any of the klaviyo mapping dictionaries
        '''
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
        ''':class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform._match_payload_values_`
        ---
        
        Checks to see if a value already exists in the klaviyo payload, if not, add it.
        
        Parameters
        ---
        :param (*dict*) `payload_section`: section of klaviyo payload value is from
        :param (*str*) `match_key`: the key to lookup in klaviyo mapping dicts
        :param (*_type_*) `value`: value to check for
        :param (*list*) `matched`: list of matched keys that had values added to payload
        :param (*str*) `list_prepend`: what part of klaviyo payload the value is from
        
        Returns
        ---
        :return `payload_section` (dict): updated part of payload which key/value originate from
        :return `matched` (list): updated (or not) list of matched keys/values
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.transform.klaviyo_data_push.Transform`.:meth:`~integration_platform.transform.klaviyo_data_push.Transform._format_create_payload_`
        '''        
        klaviyo_value = payload_section.get(match_key)
        if isinstance(klaviyo_value, str) and isinstance(value, str):
            klaviyo_value = klaviyo_value.lower()
            value = value.lower()
        if isinstance(value, (date, datetime)):
            bp = 'here'
            format = '%Y-%m-%d' if isinstance(value, date) else '%Y-%m-%dT%H:%M:%S.%fZ'
            value = value.strftime(format)
        if klaviyo_value != value:
            if match_key == 'phone_number':
                if klaviyo_value and value in klaviyo_value: #If the db's TFN value is within klaviyo's TFN value. (db doesn't have +1 and klaviyo does)
                    return payload_section, matched
            elif 'zip' in match_key.lower():
                v = value[:5]
                k = klaviyo_value[:5] if isinstance(klaviyo_value, str) else None
                if v == k:
                    return payload_section, matched
            elif match_key == 'country' and value == 'united states' and klaviyo_value == 'us':
                return payload_section, matched
            payload_section[match_key] = value
            self.logger.info(f'{self.current_prefix}{match_key}, {klaviyo_value} to {value}')
            matched.append({f'{list_prepend}{match_key}': {'old': klaviyo_value, 'new': value}})
        return payload_section, matched
            

    #MARK: _check_consent_
    def _check_consent_(self, customer_records: list[dict]):
        db_consent = []
        consent_columns = {
            'Mkt_Email_CanReceiveEmail_phone': None,
            'Mkt_Email_CanReceiveEmail_email': None,
            'Mkt_SMS_CanReceiveSMS_phone': None,
            'Mkt_SMS_CanReceiveSMS_email': None,
            'Consent_email': None,
            'Consent_phone': None,
            'Mkt_Email_Consent_email': None,
            'Mkt_Email_Consent_phone': None,
            'Mkt_SMS_Consent_email': None,
            'Mkt_SMS_Consent_phone': None,
            'EmailOption': None,
            'AcceptsMarketing': None,
            'AcceptsMarketing_email': None,
            'AcceptsMarketing_phone': None,
            'EmailLastUpdatedDatetime': None,
            'EmailLastUpdatedBy': None,
            'EmailCollection': None,
            'PhoneOption': None,
            'Mkt_Email_ConsentTimestamp_phone': None,
            'Mkt_Email_ConsentTimestamp_email': None,
            'Mkt_SMS_ConsentTimestamp_phone': None,
            'Mkt_SMS_ConsentTimestamp_email': None,
        }
        for customer in customer_records:
            customer['db_consent'] = dict(consent_columns)
            for key, value in customer['db'].items():
                if key in list(consent_columns.keys()):
                    customer['db_consent'][key] = value
        return customer_records


    #MARK: _compare_consent_
    def _compare_consent_(self, customer_records: list[dict]):
        bp = 'here'
        update_klaviyo = []
        update_klaviyo_call_center_consent = []
        total = len(customer_records)
        call_center_consent = False
        for i, customer in enumerate(customer_records):
            customer['ConsentUpdate'] = None
            entries = 0
            self.current_customer_email = customer['db']['Email']
            self.current_prefix = f'{i+1}/{total}, {self.current_customer_email}: '
            if not customer.get('klaviyo_response'):
                continue
            klaviyo = customer['klaviyo_response']['data']['attributes']['subscriptions']
            db = customer['db_consent']

            k_email_consent = klaviyo['email']['marketing']['can_receive_email_marketing'] == True and klaviyo['email']['marketing']['consent'] == 'SUBSCRIBED'
            db_email_consent = (
                (db['Mkt_Email_Consent_phone'] == 'SUBSCRIBED' and db['Mkt_Email_CanReceiveEmail_phone'] == True)
                or
                (db['Mkt_Email_Consent_email'] == 'SUBSCRIBED' and db['Mkt_Email_CanReceiveEmail_email'] == True)
            )

            k_sms_consent = klaviyo['sms']['marketing']['can_receive_sms_marketing'] == True and klaviyo['sms']['marketing']['consent'] == 'SUBSCRIBED'
            
            db_sms_consent = (
                (db['Mkt_SMS_CanReceiveSMS_phone'] == True and db['Mkt_SMS_Consent_phone'] == 'SUBSCRIBED')
                or
                (db['Mkt_SMS_CanReceiveSMS_email'] == True and db['Mkt_SMS_Consent_email'] == 'SUBSCRIBED')
            )


            consent_header = self._format_consent_header_(customer=customer)
            if k_email_consent != db_email_consent:
                customer['ConsentUpdate'] = 'Email'
                self.logger.info(f'{self.current_prefix}Email consent will be updated')
                consent_payload = self._format_consent_(consent_header=consent_header, email_sms='email')
                entries+=1
            if k_sms_consent != db_sms_consent and not k_sms_consent:
                customer['ConsentUpdate'] = 'SMS' if not customer['ConsentUpdate'] else 'Email & SMS'
                self.logger.info(f'{self.current_prefix}SMS consent will be updated')
                consent_payload = self._format_consent_(consent_header=consent_header, email_sms='sms')
                bp = 'here'
                entries+=1
            db_email_consent_from_call_center = db['EmailOption']
            if entries >= 1:
                update_klaviyo.append(consent_payload)

            if db_email_consent_from_call_center and not k_email_consent:
                db_consent_timestamp = db['Mkt_Email_ConsentTimestamp_email'] or db['Mkt_Email_ConsentTimestamp_phone'] 
                if db['EmailLastUpdatedDatetime'] == None and db_consent_timestamp != None:
                    continue
                elif db['EmailLastUpdatedDatetime'] and db_consent_timestamp and db['EmailLastUpdatedDatetime'] <= db_consent_timestamp:
                    continue
                elif not db['EmailLastUpdatedDatetime'] and not db_consent_timestamp:
                    consented_at = datetime.strftime(datetime.now(ZoneInfo('America/New_York')), '%Y-%m-%dT%H:%M:%SZ')
                else:
                    consented_at = datetime.strftime(db['EmailLastUpdatedDatetime'] , '%Y-%m-%dT%H:%M:%SZ')
                call_center_consent_payload = self._format_consent_(consent_header=consent_header, email_sms='email')
                call_center_consent_payload['attributes']['subscriptions']['email']['marketing']['consented_at'] = consented_at
                update_klaviyo_call_center_consent.append(call_center_consent_payload)
                bp = 'here'

        consent_updates = {'profiles': {'data': update_klaviyo}}
        historic_consent_updates = {'profiles': {'data': update_klaviyo_call_center_consent}} 
        return consent_updates, historic_consent_updates, customer_records


    #MARK: _format_consent_header_
    def _format_consent_header_(self, customer: dict):
        new_payload = {
            'type': 'profile',
            'id': customer['payload']['data']['id'],
            'attributes':{
                'email': customer['klaviyo_response']['data']['attributes']['email'],
                'phone_number': customer['klaviyo_response']['data']['attributes']['phone_number'],
                'subscriptions': {}
            }
        }
        
        return new_payload


    #MARK: _format_consent_
    def _format_consent_(self, consent_header: dict, email_sms: Literal['email', 'sms']):
        
        consent_header['attributes']['subscriptions'][email_sms] = {
            'marketing': {
                'consent': 'SUBSCRIBED'
            }
        }
        return consent_header
