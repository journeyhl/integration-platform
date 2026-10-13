from integration_platform.pipelines.base import Pipeline
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from integration_platform.connectors.klaviyo import KlaviyoAPI
from integration_platform.transform.klaviyo_data_push import Transform
from integration_platform.load.klaviyo_data_push import Load
class KlaviyoDataPush(Pipeline):
    '''
    ## Situation
        Using the broadened marketing data I've made available from the Newsletter pipeline, we want to now make sure we are creating profiles and updating data where available within klaviyo
    
    <hr>

    ## Task
        Design a process to create and update profiles in klaviyo.
        We have a limit of profiles before we incur increased costs, must stay within threshold.
    
    <hr>
    
    ## Action
        Wrote query pulling all data from the table populated via :class:`~integration_platform.pipelines.ucmi_hubspot.UCMI_HubspotCustomers` using custom built :class:`~integration_platform.connectors.sql.SQLConnector`, 
        For each row or customer, lookup klaviyo profile by email. If email is found update, if not, create.
        For updates, compare the existing values in klaviyo with what we have in db. If differenct, update. If there are any db values popualted but not in klaviyo that we can fill, send them
        For creations, send all non-null db values in klaviyo payload
    <hr>
    
    ## Result
        
    '''
    def __init__(self, function: str):
        super().__init__('KlaviyoNewsletter', function)
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




