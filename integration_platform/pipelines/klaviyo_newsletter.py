from integration_platform.pipelines.base import Pipeline
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from integration_platform.connectors.klaviyo import KlaviyoAPI
from integration_platform.transform.klaviyo_newsletter import Transform
import polars as pl
class KlaviyoNewsletter(Pipeline):
    def __init__(self, function: str, is_newsletter: bool = True, filter_if_not_newsletter: str = ''):
        ''':class:`~integration_platform.pipelines.klaviyo_newsletter.KlaviyoNewsletter`
        ---

        Loads Klaviyo profile data to db_CentralStore
        
        ## Initialization

        :param (*str*) `function`: name of Azure Function        
                
           ### ***Optional***
        :param (*bool = True*) `is_newsletter`: Pull records only from Newsletter list?

        :param (*str = ''*) `filter_if_not_newsletter`: If pulling all profiles, filter that should be applied


        ### Sets

         - #### self.:attr:`~integration_platform.pipelines.klaviyo_newsletter.KlaviyoNewsletter.klaviyo`:  :class:`~integration_platform.connectors.klaviyo.KlaviyoAPI`
         - #### self.:attr:`~integration_platform.pipelines.klaviyo_newsletter.KlaviyoNewsletter.transformer`: :class:`~integration_platform.transform.klaviyo_newsletter.Transform`
         - #### self.:attr:`~integration_platform.pipelines.klaviyo_newsletter.KlaviyoNewsletter.cutoff`: datetime.now() - 7 days
         - #### self.:attr:`~integration_platform.pipelines.klaviyo_newsletter.KlaviyoNewsletter.cutoff_str`: self.cutoff as a string

        <hr>

        ## Extraction
        
        Pulls profiles and details from Klaviyo. Depending on if is_newsletter is True or False, it'll look at only the members of the Newsletter list, or all profiles.

        <hr>

        ## Transformation

        Splits up each profile from Klaviyo into three dicts, one for header level data, one for properties and one for subscriptions. Adds each profile's dicts to lists

        <hr>

        ## Load

        Loads to db_CentralStore via merge
        - klaviyo.ProfileHeader
        - klaviyo.ProfileProperties
        - klaviyo.ProfileSubscriptions
        '''
        super().__init__('KlaviyoNewsletter', function)
        self.klaviyo = KlaviyoAPI(self)
        self.transformer = Transform(self)
        self.is_newsletter = is_newsletter
        self.filter_if_not_newsletter = filter_if_not_newsletter
        self.cutoff = datetime.now(ZoneInfo('America/New_York')) - timedelta(days=7)
        self.cutoff_str = self.cutoff.strftime('%Y-%m-%dT%H:%M:%SZ')

    def extract(self):
        last_checked = datetime.now(ZoneInfo('America/New_York'))
        if not self.is_newsletter:
            data_extract = self.klaviyo.get_profiles() if self.filter_if_not_newsletter == '' else self.klaviyo.get_profiles(filter=self.filter_if_not_newsletter)
            data_extract = {
                'profiles': data_extract,
                'LastChecked': last_checked
            }
        else:
            data_extract = self.klaviyo.get_list(list_id='Rz3G6F', profile_filter=f"filter=greater-than(joined_group_at,{self.cutoff_str})")
            # data_extract = self.klaviyo.get_list(list_id='Rz3G6F')
            data_extract['LastChecked'] = last_checked

        data_extract['is_newsletter'] = self.is_newsletter
        self.df_newsletter = self.centralstore.query_db('Select ID, IsNewsletter from klaviyo.ProfileHeader where IsNewsletter = 1')
        return data_extract

    def transform(self, data_extract):
        data_transformed = self.transformer.landing(data_extract=data_extract)

        return data_transformed

    def load(self, data_transformed):
        self.centralstore.reconnect()
        for i, (table, rows) in enumerate(data_transformed.items()):
            bp = 'here'
            self.centralstore.merge_table_paginated(table_name=table, data=rows, page_size=100)
        return data_transformed

    def log_results(self, data_loaded):
        pass
