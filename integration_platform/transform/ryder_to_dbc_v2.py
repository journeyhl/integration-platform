from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.ryder_to_dbc import RyderToDbc
import logging
import polars as pl
from datetime import datetime

class Transform:
    def __init__(self, pipeline: RyderToDbc):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.Transform')
        pass


    def landing(self, data_extract):
        bp = 'here'
        self.orders = []
        self._parse_milestones_()
        


    def _parse_milestones_(self):
        bp = 'here'