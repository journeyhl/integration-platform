from integration_platform.pipelines.base import Pipeline
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from integration_platform.connectors.klaviyo import KlaviyoAPI
from integration_platform.transform.klaviyo_data_push import Transform

class KlaviyoDataPush(Pipeline):
    def __init__(self, function: str):
        super().__init__('KlaviyoNewsletter', function)
        self.klaviyo = KlaviyoAPI(self)
        self.transformer = Transform(self)

    def extract(self):
        self.ts_extract_s = datetime.now(ZoneInfo('America/New_York'))
        data_extract = self.centralstore.query_to_dataframe(query=self.centralstore.queries.Klaviyo_GroHaus_DataPush)
        self.ts_extract_f = datetime.now(ZoneInfo('America/New_York'))
        return data_extract

    def transform(self, data_extract):
        data_transformed = self.transformer.landing(data_extract=data_extract)
        return data_transformed

    def load(self, data_transformed):
        creates = data_transformed['create']
        for i, payload in enumerate(creates):
            response = self.klaviyo.create_or_update_profile(payload=payload)
            bp = 'here'
        for i, (table, rows) in enumerate(data_transformed.items()):
            bp = 'here'
            self.centralstore.merge_table_paginated(table_name=table, data=rows, page_size=500)
        return data_transformed

    def log_results(self, data_loaded):
        pass
