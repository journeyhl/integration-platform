

import logging
from datetime import datetime
from zoneinfo import ZoneInfo
class DefaultLoader:
    def __init__(self, pipeline):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.DefaultLoader')
        pass



    def add_InsertedDT_to_list(self, ldata: list):
        for row in ldata:
            row['InsertedDT'] = datetime.now(ZoneInfo('America/New_York'))
        return ldata