

import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Any
class DefaultLoader:
    def __init__(self, pipeline):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.DefaultLoader')
        pass



    def add_InsertedDT_to_list(self, ldata: list):
        for row in ldata:
            row['InsertedDT'] = datetime.now(ZoneInfo('America/New_York'))
        return ldata

    
    def add_to_list(self, ldata: list, additions: dict[str, Any]):
        for row in ldata:
            for key, value in additions.items():
                row[key] = value
                bp = 'here'
        return ldata