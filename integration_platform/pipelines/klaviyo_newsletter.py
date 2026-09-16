from integration_platform.pipelines.base import Pipeline
from datetime import datetime
from zoneinfo import ZoneInfo
from integration_platform.connectors.klaviyo import KlaviyoAPI
from integration_platform.transform.klaviyo_newsletter import Transform

class KlaviyoNewsletter(Pipeline):
    def __init__(self, function: str):
        super().__init__('klaviyo-newsletter', function)
        self.klaviyo = KlaviyoAPI(self)
        self.transformer = Transform(self)

    def extract(self):
        data_extract = self.klaviyo.get_list(list_id='Rz3G6F')
        return data_extract

    def transform(self, data_extract):
        data_transformed = self.transformer.landing(data_extract=data_extract)
        return data_transformed

    def load(self, data_transformed):

        return

    def log_results(self, data_loaded):
        pass
