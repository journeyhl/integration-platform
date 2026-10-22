from integration_platform.pipelines.base import Pipeline
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from integration_platform.connectors.klaviyo import KlaviyoAPI
from integration_platform.transform.klaviyo_data_push import Transform
from integration_platform.load.klaviyo_data_push import Load
class KlaviyoDataPush(Pipeline):
    ''':class:`~integration_platform.pipelines.klaviyo_data_push.KlaviyoDataPush`
    ---
    
    ## Initialization

    Sets up KlavioAPI, transformer and loader

    <hr>

    ## Extraction
    
    Queries db_CentralStore for all HubspotCustomers with a populated email value and joins to klavio schema tables twice, once on phone and email

    <hr>

    ## Transformation

    For each customer, looks up Klavio profile using :class:`~integration_platform.connectors.klaviyo.KlaviyoAPI`.

    If profile is returned, we'll update, if not, we create.

    For each updated customer, we compare all the `attributes` & `properties` values from Klaviyo against what we have in our db

    If there's a difference, determine if it's significant enough to warrant change. Do so for full response from klavio

    Next, for all customers, check if there's any data in the database that we don't have in klavio. If there is, add it to the payload. If a value already exists, make sure it differs, then add

    Finally, check the subscription/consent values from Klaviyo and the database. If the database has it that the customer has consented for SMS or email marketing, add to payload to send to Klaviyo for consent update

    <hr>

    ## Load

    Filter out those customers who already existed, but don't have any fields to be updated.

    For each customer to be created or updated, do so via :class:`~integration_platform.connectors.klaviyo.KlaviyoAPI`.:meth:`~integration_platform.connectors.klaviyo.KlaviyoAPI.create_or_update_profile`

    If any customers need their consent updated, send bulk consent update via :class:`~integration_platform.connectors.klaviyo.KlaviyoAPI`.:meth:`~integration_platform.connectors.klaviyo.KlaviyoAPI.subscribe_profiles`
    '''
    
    def __init__(self, function: str):
        super().__init__('KlaviyoDataPush', function)
        self.klaviyo = KlaviyoAPI(self)
        self.transformer = Transform(self)
        self.loader = Load(self)

    def extract(self):
        self.ts_extract_s = datetime.now(ZoneInfo('America/New_York'))
        data_extract = self.centralstore.query_to_dataframe(query=self.centralstore.queries.Klaviyo_GroHaus_DataPush)
        self.ts_extract_f = datetime.now(ZoneInfo('America/New_York'))
        return data_extract

    def transform(self, data_extract):
        data_transformed = self.transformer.landing(data_extract=data_extract)
        return data_transformed

    def load(self, data_transformed):
        data_loaded = self.loader.landing_loader(data_transformed=data_transformed)
        return data_transformed

    def log_results(self, data_loaded):
        pass




