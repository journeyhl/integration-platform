from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.klaviyo_writeback_hubspot import KlaviyoWritebackHubspot
import logging
import polars as pl
from datetime import datetime

class TransformPhase2:
    def __init__(self, pipeline: KlaviyoWritebackHubspot):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.TransformPhase2')
        pass

    #MARK: landing
    def landing(self, data_transformed: list):
        no_update = []
        self.prelim_contacts_needing_update = {}
        total = len(data_transformed)
        for i, contact in enumerate(data_transformed):
            self.prefix = f'{i+1}/{total} ({contact['db']['Email']}): '
            self._filter_no_updates_(contact)
        total = len(self.prelim_contacts_needing_update)
        bp = 'here'
        final_contacts_needing_update = {}
        for i, (hubspot_id, change_list) in enumerate(self.prelim_contacts_needing_update.items()):
            self.prefix = f'{i+1}/{total}, {hubspot_id}: '
            change_list = self.comparer(values=change_list)
            change_list = self._split_dual_keys_(values=change_list)
            change_list = self._format_for_hubspot_(values=change_list)
            if change_list != []:
                final_contacts_needing_update[hubspot_id] = change_list
            else: 
                no_update.append({'RecordID': hubspot_id, 'Payload': None})
            bp = 'here'
        bp = 'here'
        return final_contacts_needing_update, no_update

    #MARK: _filter_no_updates_
    def _filter_no_updates_(self, contact: dict):
        ''':class:`~integration_platform.transform.klaviyo_writeback_hubspot_phase2.TransformPhase2`.:meth:`~integration_platform.transform.klaviyo_writeback_hubspot_phase2.TransformPhase2._filter_no_updates_`
        ---
        
        Filters out any properties that we can immediately determine to not need an update
        
        Parameters
        ---
        :param (*dict*) `contact`: contact dict containing data from hubspot, klaviyo, database and the values that are differing

        <hr>
        
        Sets
        ---
        :attr:`~integration_platform.transform.klaviyo_writeback_hubspot_phase2.TransformPhase2.prelim_contacts_needing_update`
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.transform.klaviyo_writeback_hubspot_phase2.TransformPhase2`.:meth:`~integration_platform.transform.klaviyo_writeback_hubspot_phase2.TransformPhase2.landing`
        '''        
        updates = []
        if contact['hubspot'] == {} or not contact.get('diffs'):
            return
        for key, properties in contact['diffs'].items():
            bp = 'here'
            for prop_key, update_status in properties.items():
                bp = 'here'
                if update_status == {}:
                    continue
                if update_status['update_hubspot'] == False:
                    self.logger.info(f'{self.prefix}{key}.{prop_key}, No update needed')
                    continue
                if update_status['hubspot_key'] in self.pipeline.read_only:
                    self.logger.info(f'{update_status['hubspot_key']} is read only, skipping')
                    continue
                updates.append(update_status)
                bp ='here'
        self.prelim_contacts_needing_update[contact['hubspot']['id']] = updates

    #MARK: comparer
    def comparer(self, values):
        total_vals = len(values)
        record_prefix = self.prefix
        no_key = []
        for i, value in enumerate(values):
            self.prefix = f'{record_prefix}, ({i+1}/{total_vals} props): '
            self.current_value = value
            bp = 'here'
            v_hubspot = value['hubspot']
            v_klaviyo = value['klaviyo'] if 'date' not in value['klaviyo_key'].lower() else self.pipeline.klaviyo.helper.__parse_and_compare_dates__(klaviyo_date=value['klaviyo'])
            if not value['hubspot_key']:
                value['update_hubspot'] = False
                no_key.append(value)
                bp = 'here'
            elif value['klaviyo_key'] == 'zip' and value['hubspot_key'] == 'shipping_zip//billing_zip':
                value['update_hubspot'] = self._compare_zip_codes(zip_hs=v_hubspot, zip_klaviyo=v_klaviyo)
            elif isinstance(v_klaviyo, str) and isinstance(v_hubspot, str):
                value['update_hubspot'] = self._compare_strings_(v_hubspot=v_hubspot, v_klaviyo=v_klaviyo)
                bp = 'here'
            elif not v_hubspot:
                self.logger.warning(f'{self.prefix}No value found in Hubspot {value['hubspot_key']} property, updating to {v_klaviyo}')
            bp = 'here'
            value['klaviyo'] = v_klaviyo
        values_to_update = [val for val in values if val['update_hubspot']]
        self.logger.info(f'{total_vals} -> {len(values_to_update)} values to update. Any trimmed did not have a hubspot key or were equal, but as different data types (str & date, etc)')
        bp = 'here'
        return values_to_update


    #MARK: _compare_strings_
    def _compare_strings_(self, v_hubspot: str, v_klaviyo: str):
        self.logger.info(f'{self.prefix}Comparing Klaviyo {self.current_value['klaviyo_key']} to Hubspot {self.current_value['hubspot']}')
        hs = self.pipeline.default_transformer.clean_string(string=v_hubspot) or ''
        k = self.pipeline.default_transformer.clean_string(v_klaviyo) or ''
        if hs.lower() == k.lower():
            self.logger.info(f'{self.prefix}No {self.current_value['hubspot_key']} update needed')
            return False
        self.logger.warning(f'{self.prefix}Updating Hubspot {self.current_value['hubspot']} from {hs} to {k}')
        return True


    #MARK: _compare_zip_codes
    def _compare_zip_codes(self, zip_hs, zip_klaviyo):
        self.logger.info(f'{self.prefix}Comparing zipcodes...')
        bp = 'here'
        if zip_hs == None:
            self.logger.warning(f'{self.prefix}Updating Hubspot zipcode from {zip_hs} to {zip_klaviyo}')
            return True
        if zip_klaviyo == None:
            return False
        if len(zip_hs) != len(zip_klaviyo):
            if zip_hs[:5] != zip_klaviyo[:5]:
                self.logger.warning(f'{self.prefix}Updating Hubspot zipcode from {zip_hs} to {zip_klaviyo}')
                return True
            self.logger.info(f'{self.prefix}No zipcode update needed')
            return False 
        hs = self.pipeline.default_transformer.clean_string(string=zip_hs) or ''
        k = self.pipeline.default_transformer.clean_string(zip_klaviyo) or ''
        if hs == k:
            self.logger.info(f'{self.prefix}No zipcode update needed')
            return False
        self.logger.warning(f'{self.prefix}Updating hubspot zipcode from {zip_hs} to {zip_klaviyo}')
        return True


    def _split_dual_keys_(self, values):
        new_values = []
        for value in values:
            if value['hubspot_key'] and '//' in value['hubspot_key']:
                local_splits = [
                    {
                        **value,
                        'hubspot_key': key
                    }
                    for key in value['hubspot_key'].split('//')
                ]
                self.logger.warning(f'Split {value['hubspot_key']} to two entries: {', '.join(value['hubspot_key'].split('//'))}')
                new_values.extend(local_splits)
            else:
                new_values.append(value)
        bp = 'here'
        return new_values

    def _format_for_hubspot_(self, values):
        for value in values:
            k = value['klaviyo']
            if isinstance(k, datetime):
                value['klaviyo'] = k.strftime('%Y-%m-%d') if value['hubspot_key'].lower() in self.pipeline.date_types else str(int(k.timestamp()))
            elif isinstance(k, bool):
                value['klaviyo'] = 'true' if k else 'false'
            elif isinstance(k, (int, float)):
                value['klaviyo'] = str(k)
            elif isinstance(k, str):
                continue
            elif isinstance(k, list):
                value['klaviyo'] = ','.join(k)
            else:
                bp = 'here'
        return values

