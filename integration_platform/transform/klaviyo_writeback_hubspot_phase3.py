from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.klaviyo_writeback_hubspot import KlaviyoWritebackHubspot
import logging
import polars as pl

class TransformPhase3:
    def __init__(self, pipeline: KlaviyoWritebackHubspot):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.TransformPhase3')
        pass

    #MARK: landing
    def landing(self, data_transformed: dict[str, list[dict]]):
        bp = 'here'
        contact_payloads = []
        for id, properties in data_transformed.items():
            contact = {
                'object_type': 'contacts',
                'object_id': id,
                'payload': {
                    'properties':{
                        prop['hubspot_key'].lower(): prop['klaviyo']
                        for prop in properties
                    }                    
                }
            }
            contact_payloads.append(contact)
        return contact_payloads

       