from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.ucmi_hubspot import UCMI_HubspotCustomers
import logging
import polars as pl
from datetime import datetime

class TransformPhase2:
    def __init__(self, pipeline: UCMI_HubspotCustomers):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.TransformPhase2')
        pass


    def phase2_landing(self, data_transformed: list[dict]):
        bp = 'here'
        