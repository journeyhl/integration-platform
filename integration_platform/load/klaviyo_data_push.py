from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.klaviyo_data_push import KlaviyoDataPush
import logging
import time
import polars as pl
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import json

class Load:
    def __init__(self, pipeline: KlaviyoDataPush):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.Load')
        bp = 'here'


    #MARK: landing_loader
    def landing_loader(self, data_transformed: dict) -> list[dict]:
        ''':class:`~integration_platform.load.klaviyo_data_push.Load`.:meth:`~integration_platform.load.klaviyo_data_push.Load.landing_loader`
        ---
        
        Landing method for Load class of :class:`~integration_platform.pipelines.klaviyo_data_push.KlaviyoDataPush`
        
        Parameters
        ---
        :param (*dict*) `data_transformed`: transformed data from pipeline. Contains `customer_records` and `consent_updates`
        
        Returns
        ---
        :return `db_logs` (list[dict]): List of customer_records to load to db with the last checked date and the data that was changed/added to load to db
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.pipelines.klaviyo_data_push.KlaviyoDataPush`.:meth:`~integration_platform.pipelines.klaviyo_data_push.KlaviyoDataPush.load`
        
        ## Downstream Calls (Methods/Functions called)
        
         ### :class:`~integration_platform.load.klaviyo_data_push.Load`.:meth:`~integration_platform.load.klaviyo_data_push.Load._load_customer_records_`
        
          - For each customer that needs to be updated in Klaviyo or have a profile created sends profile payload for each one at a time 
        
         ### :class:`~integration_platform.load.klaviyo_data_push.Load`.:meth:`~integration_platform.load.klaviyo_data_push.Load._load_consent_updates_`
           
          - Sends consent/subscription updates to Klaviyo in bulk. If no updates to be made, doesn't send anything
        '''        
        bp = 'here'
        updated_or_created = self._load_customer_records_(customer_records=data_transformed['customer_records'])
        self._load_consent_updates_(consent_updates=data_transformed['consent_updates'])
        self._load_consent_updates_(consent_updates=data_transformed['historic_consent_updates'], historical_import=True)
        db_logs = self._log_loaded_records_(customer_records=data_transformed['customer_records'])
        return db_logs

    def _log_loaded_records_(self, customer_records: list):
        db_logs = []
        for record in customer_records:
            bp = 'here'
            fields_added = self.pipeline.default_transformer.clean_string(','.join(list(k for field in record['fields_added'] for k in field.keys()))) if record['fields_added'] else None
            log_entry = {
                'Email': record['db']['Email'],
                'KlaviyoID': record['payload']['data'].get('id'),
                'Action': record['action'],
                'FieldsAdded': fields_added,
                'FieldsChanged': None if not record['fields_changed'] else json.dumps(record['fields_changed']),
                'SentUpdate': True if record['klaviyo_response'] in [200, 202] or record['ConsentUpdate'] != None else False,
                'ConsentUpdate': record['ConsentUpdate'],
                'LastChecked': datetime.now(ZoneInfo('America/New_York'))
            }
            bp = 'here'
            db_logs.append(log_entry)
        return db_logs

    #MARK: _load_customer_records_
    def _load_customer_records_(self, customer_records: list):
        ''':class:`~integration_platform.load.klaviyo_data_push.Load`.:meth:`~integration_platform.load.klaviyo_data_push.Load._load_customer_records_`
        ---
        
        Given the full list of customer records, filter down to only those proviles needing to be updated or created, then send each payload to Klaviyo individually
        
        Parameters
        ---
        :param (*list*) `customer_records`: list of customer dicts containing payloads to send to klaviyo among additional details
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.load.klaviyo_data_push.Load`.:meth:`~integration_platform.load.klaviyo_data_push.Load.landing_loader`
        
        ## Downstream Calls (Methods/Functions called)
        
         ### :class:`~integration_platform.connectors.klaviyo.KlaviyoAPI`.:meth:`~integration_platform.connectors.klaviyo.KlaviyoAPI.create_or_update_profile`
        
          - Called for each profile that needs to be updated or created
        '''        
        created = 0
        updated = 0
        updated_or_created = [customer for customer in customer_records if customer['fields_added'] or customer['fields_changed']]
        self.logger.info(f'{len(customer_records) - len(updated_or_created)} records will be skipped as no updates were found to be needed')
        total = len(updated_or_created)
        for i, customer_record in enumerate(updated_or_created):
            prepend = f'{customer_record['action'][:-1]}ing'
            self.logger.info(f'{prepend} profile {i+1}/{total}... {customer_record['db']['Email']}{f' (https://www.klaviyo.com/profile/{customer_record['payload']['data']['id']})' if customer_record['action'] == 'Update' else ''}')
            response = self.pipeline.klaviyo.create_or_update_profile(payload=customer_record['payload'])
            if response.status_code == 201:
                created += 1
                self.logger.info(f'{customer_record['db']['Email']} created successfully')
            elif response.status_code == 200:
                updated += 1
                self.logger.info(f'{customer_record['db']['Email']} updated successfully')
            else:
                self.logger.error(f'Error {response.status_code}! {response.text}')
            bp = 'here'
            customer_record['klaviyo_response'] = response.status_code
        self.logger.info(f'Profiles created: {created}/{len(customer_records)}')
        self.logger.info(f'Profiles updated: {updated}/{len(customer_records)}')
        self.logger.info(f'Profiles skipped: {len(customer_records)-len(updated_or_created)}/{len(customer_records)}')
        return updated_or_created

    #MARK: _load_consent_updates_
    def _load_consent_updates_(self, consent_updates: dict, historical_import: bool = False):
        ''':class:`~integration_platform.load.klaviyo_data_push.Load`.:meth:`~integration_platform.load.klaviyo_data_push.Load._load_consent_updates_`
        ---
        
        Given a section of the payload to send to Klaviyo to update consent in bulk for a group of profiles, verify that we have profiles in our payload. If so, format the rest of the payload, and send to Klaviyo to bulk update consent for the whole group in one go
        
        Parameters
        ---
        :param (*dict*) `consent_updates`: main section of payload to be sent to Klaviyo
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.load.klaviyo_data_push.Load`.:meth:`~integration_platform.load.klaviyo_data_push.Load.landing_loader`
        
        ## Downstream Calls (Methods/Functions called)
        
         ### :class:`~integration_platform.connectors.klaviyo.KlaviyoAPI`.:meth:`~integration_platform.connectors.klaviyo.KlaviyoAPI.subscribe_profiles`
        
          - Hit Klaviyo api with payload of profiles to update consent for
        
         ### :class:`~integration_platform.helpers.klaviyo_api_helper.KlaviyoAPIHelper`.:meth:`~integration_platform.helpers.klaviyo_api_helper.KlaviyoAPIHelper.parse_errors`
           
          - If error, generate logs here
        '''        
        if historical_import:
            self.logger.info(f'Executing historic consent update (EmailOption = `Opt-In` in ucmiraw.HubspotCustomers)')
        total = len(consent_updates['profiles']['data'])
        if total == 0:
            self.logger.warning(f'No profiles need consent updates, skipping...')
            return
        self.logger.info(f'Updating consent to subscribed for {len(consent_updates['profiles']['data'])} profiles')
        payload = {
            'data':{
                'type': 'profile-subscription-bulk-create-job',
                'attributes': consent_updates,
            }
        }
        if historical_import:
            payload['data']['attributes']['historical_import'] = True
        response = self.pipeline.klaviyo.subscribe_profiles(payload=payload)
        if response.status_code == 200:
            self.logger.info(f'{response.status_code} {response.text}')
        elif response.status_code == 202:
            self.logger.info(f'{response.status_code} {response.reason}')
        else:
            self.pipeline.klaviyo.helper.parse_errors(response=response)
        bp = 'here'