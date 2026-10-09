from integration_platform.pipelines.base import Pipeline
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from integration_platform.connectors.klaviyo import KlaviyoAPI
from integration_platform.transform.klaviyo_newsletter import Transform

class KlaviyoNewsletter(Pipeline):
    def __init__(self, function: str, is_newsletter: bool = True):
        super().__init__('KlaviyoNewsletter', function)
        self.klaviyo = KlaviyoAPI(self)
        self.transformer = Transform(self)
        self.is_newsletter = is_newsletter

    def extract(self):
        cutoff = datetime.now(ZoneInfo('America/New_York')) - timedelta(days=3)
        cut_str = cutoff.strftime('%Y-%m-%dT%H:%M:%SZ')
        if not self.is_newsletter:
            data_extract = self.klaviyo.get_profiles()
            data_extract = {
                'profiles': data_extract,
                'LastChecked': datetime.now(ZoneInfo('America/New_York'))
            }
        else:
            data_extract = self.klaviyo.get_list(list_id='Rz3G6F')
        data_extract['is_newsletter'] = self.is_newsletter
        # data_extract = self.klaviyo.get_list(list_id='Rz3G6F', profile_filter=f"filter=greater-than(joined_group_at,{cut_str})")
        # 
        return data_extract

    def transform(self, data_extract):
        data_transformed = self.transformer.landing(data_extract=data_extract)
        return data_transformed

    def load(self, data_transformed):
        self.centralstore.reconnect()
        for i, (table, rows) in enumerate(data_transformed.items()):
            bp = 'here'
            self.centralstore.merge_table_paginated(table_name=table, data=rows, page_size=500)
        return data_transformed

    def log_results(self, data_loaded):
        pass
