
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.connectors.acu_api import AcumaticaAPI
import logging
import requests
import time
from datetime import datetime, timedelta
import polars as pl

class AcumaticaAPIHelper:
    def __init__(self, acu_api: AcumaticaAPI) -> None:
        self.acu = acu_api
        if type(acu_api.pipeline) == str:
            self.logger = logging.getLogger(f'{acu_api.pipeline}.AcumaticaAPIHelper')
        else:
            self.logger = logging.getLogger(f'{acu_api.pipeline.pipeline_name}.AcumaticaAPIHelper')
        
        pass