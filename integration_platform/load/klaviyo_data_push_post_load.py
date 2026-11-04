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

class PostLoad:
    def __init__(self, pipeline: KlaviyoDataPush):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.Load')
        bp = 'here'

