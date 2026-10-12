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
        # creates = data_transformed['create']
        # for i, payload in enumerate(creates):
        #     response = self.klaviyo.create_or_update_profile(payload=payload)
        #     bp = 'here'
        creates = data_transformed['create']
        updates = data_transformed['update']

        for i, customer_record in enumerate(updates):
            bp = 'here'



        bp = 'here'
        updates = [customer_record['payload'] for action, customer_records in data_transformed.items() for customer_record in customer_records if customer_record['updated'] != []]
        for i, payload in enumerate(updates):
            response = self.klaviyo.create_or_update_profile(payload=payload)
            #TODO: left off here 10/9 5pm
            bp = 'here'
        return data_transformed

    def log_results(self, data_loaded):
        pass
