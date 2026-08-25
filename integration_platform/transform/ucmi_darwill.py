from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.ucmi_darwill import UCMI_DarwillCustomers
import logging
import polars as pl
from datetime import datetime

class Transform:
    def __init__(self, pipeline: UCMI_DarwillCustomers):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.Transform')
        pass

    def landing(self, data_extract):
        bp = 'here'