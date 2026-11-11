
from __future__ import annotations
from typing import TYPE_CHECKING, Literal
if TYPE_CHECKING:
    from integration_platform.pipelines.klaviyo_writeback_hubspot import KlaviyoWritebackHubspot
import logging
import requests
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from requests import Response
import polars as pl



class KlaviyoHubspotComparer:
    def __init__(self, pipeline: KlaviyoWritebackHubspot) -> None:
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.KlaviyoHubspotComparer')        


    def landing(self, contact_profiles: list):
        bp = 'here'
        for profile in contact_profiles:
            bp = 'here'

