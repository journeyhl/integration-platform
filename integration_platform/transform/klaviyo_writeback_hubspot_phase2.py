from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.klaviyo_writeback_hubspot import KlaviyoWritebackHubspot
import logging
import polars as pl
class TransformPhase2:
    def __init__(self, pipeline: KlaviyoWritebackHubspot):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.TransformPhase2')
        pass

    #MARK: landing
    def landing(self, data_transformed: list):
        bp = 'here'
        self.contacts_needing_update = {}
        total = len(data_transformed)
        for i, contact in enumerate(data_transformed):
            self.prefix = f'{i+1}/{total} ({contact['db']['Email']}): '
            self._filter_no_updates_(contact)
        total = len(self.contacts_needing_update)
        bp = 'here'
        for i, (hubspot_id, change_list) in enumerate(self.contacts_needing_update.items()):
            self.prefix = f'{i+1}/{total}, {hubspot_id}: '
            change_list = self.comparer(values=change_list)
            bp = 'here'

    #MARK: _filter_no_updates_
    def _filter_no_updates_(self, contact: dict):
        updates = []
        if contact['hubspot'] == {}:
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
                if update_status['hubspot_key'] == 'createdate':
                    continue
                updates.append(update_status)
                bp ='here'
        self.contacts_needing_update[contact['hubspot']['id']] = updates


    def comparer(self, values):
        total_vals = len(values)
        record_prefix = self.prefix
        for i, value in enumerate(values):
            self.prefix = f'{record_prefix}, ({i+1}/{total_vals} props): '
            self.current_value = value
            bp = 'here'
            v_hubspot = value['hubspot']
            v_klaviyo = value['klaviyo'] if 'date' not in value['klaviyo_key'].lower() else self.pipeline.klaviyo.helper.__parse_and_compare_dates__(klaviyo_date=value['klaviyo'])
            
            if value['klaviyo_key'] == 'zip' and value['hubspot_key'] == 'shipping_zip//billing_zip':
                value['update_hubspot'] = self._compare_zip_codes(zip_hs=v_hubspot, zip_klaviyo=v_klaviyo)
            elif isinstance(v_klaviyo, str) and isinstance(v_hubspot, str):
                value['update_hubspot'] = self._compare_strings_(v_hubspot=v_hubspot, v_klaviyo=v_klaviyo)
                bp = 'here'
            elif not v_hubspot:
                self.logger.info(f'{self.prefix}No value found in Hubspot {value['hubspot_key']} property, updating to {v_klaviyo}')
            bp = 'here'


    def _compare_strings_(self, v_hubspot: str, v_klaviyo: str):
        self.logger.info(f'{self.prefix}Comparing Klaviyo {self.current_value['klaviyo_key']} to Hubspot {self.current_value['hubspot']}')
        hs = self.pipeline.default_transformer.clean_string(string=v_hubspot) or ''
        k = self.pipeline.default_transformer.clean_string(v_klaviyo) or ''
        if hs.lower() == k.lower():
            self.logger.info(f'{self.prefix}No {self.current_value['hubspot_key']} update needed')
            return False
        self.logger.info(f'{self.prefix}Updating Hubspot {self.current_value['hubspot']} from {hs} to {k}')
        return True


    def _compare_zip_codes(self, zip_hs, zip_klaviyo):
        self.logger.info(f'{self.prefix}Comparing zipcodes...')
        bp = 'here'
        test = zip_hs[:5]
        if len(zip_hs) != len(zip_klaviyo):
            if zip_hs[:5] != zip_klaviyo[:5]:
                self.logger.info(f'{self.prefix}Updating Hubspot zipcode from {zip_hs} to {zip_klaviyo}')
                return True
            self.logger.info(f'{self.prefix}No zipcode update needed')
            return False 
        hs = self.pipeline.default_transformer.clean_string(string=zip_hs) or ''
        k = self.pipeline.default_transformer.clean_string(zip_klaviyo) or ''
        if hs == k:
            self.logger.info(f'{self.prefix}No zipcode update needed')
            return False
        self.logger.info(f'{self.prefix}Updating hubspot zipcode from {zip_hs} to {zip_klaviyo}')
        return True