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
        bp = 'here'

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