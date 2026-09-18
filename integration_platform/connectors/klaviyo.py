from __future__ import annotations
from typing import TYPE_CHECKING,  Any, Iterator
if TYPE_CHECKING:
    from integration_platform.pipelines.klaviyo_newsletter import KlaviyoNewsletter
import logging
from integration_platform.config.settings import KLAYVIO
from integration_platform.helpers.klaviyo_api_helper import KlaviyoAPIHelper
import requests

class KlaviyoAPI:
    ''':class:`~integration_platform.connectors.klaviyo.KlaviyoAPI`
    ---
    
    KlaviyoAPI connector
    
    <hr>
    
    Methods
    ---
    - ## :meth:`~integration_platform.connectors.klaviyo.KlaviyoAPI._set_urls_`
    - ## :meth:`~integration_platform.connectors.klaviyo.KlaviyoAPI.get_profiles`
    - ## :meth:`~integration_platform.connectors.klaviyo.KlaviyoAPI.get_list`
    - ## :meth:`~integration_platform.connectors.klaviyo.KlaviyoAPI.get_list_profiles`
    - ## :meth:`~integration_platform.connectors.klaviyo.KlaviyoAPI._get_data_`
    - ## :meth:`~integration_platform.connectors.klaviyo.KlaviyoAPI.__page__`
    - ## :meth:`~integration_platform.connectors.klaviyo.KlaviyoAPI._set_fields_`
    '''
    def __init__(self, pipeline: KlaviyoNewsletter) -> None:
        self.pipeline = pipeline
        if type(pipeline) == str:
            self.logger = logging.getLogger(f'{pipeline}.KlaviyoAPI')
        else:
            self.logger = logging.getLogger(f'{pipeline.pipeline_name}.KlaviyoAPI')
        self.helper = KlaviyoAPIHelper(self)
        self.headers = self.helper.format_headers(api_key=KLAYVIO['api_key'] or '')
        self.base_url = 'https://a.klaviyo.com/api'
        self._set_urls_()
        self._set_fields_()
        pass

    #MARK: _set_urls_
    def _set_urls_(self):
        self.url_lists = f'{self.base_url}/lists'
        self.url_profiles = f'{self.base_url}/profiles'



    #MARK: get_profiles
    def get_profiles(self, url: str = 'https://a.klaviyo.com/api/profiles', params: str = 'page[size]=100'):
        ''':class:`~integration_platform.connectors.klaviyo.KlaviyoAPI`.:meth:`~integration_platform.connectors.klaviyo.KlaviyoAPI.get_profiles`
        ---
        
        Gets profiles from Klaviyo and handles paging. Default url will return all profiles, pass a url value to return values from a list
        
        Returns
        ---
        :return `profiles` (list): list of profiles from Klaviyo
            
        <hr>
        
        ## Downstream Calls (Methods/Functions called)
        
         ### :class:`~integration_platform.connectors.klaviyo.KlaviyoAPI`.:meth:`~integration_platform.connectors.klaviyo.KlaviyoAPI._get_data_`
        
          - Method that hits the Klaviyo api at the url passed
        
         ### :class:`~integration_platform.connectors.klaviyo.KlaviyoAPI`.:meth:`~integration_platform.connectors.klaviyo.KlaviyoAPI.__page__`
            
          - Method to determine if there are more records to be parsed/if we should turn top the next page of results
        '''        
        profiles = []
        paged = False
        bp = 'here'
        while True:
            parsed_response = self._get_data_(url=url, params=params) if not paged else self._get_data_(url=url)
            profiles.extend(parsed_response['data'])
            self.logger.info(f'{len(profiles)} Profiles parsed successfully')
            keep_going, next_page = self.__page__(parsed_response=parsed_response)
            if not keep_going:
                break
            url = next_page
            paged = True
        return profiles


    #MARK: get_list
    def get_list(self, list_id: str, profile_filter: str = ''):
        ''':class:`~integration_platform.connectors.klaviyo.KlaviyoAPI`.:meth:`~integration_platform.connectors.klaviyo.KlaviyoAPI.get_list`
        ---
        
        Given the ID of a Klaviyo list, hit API for its details, then retrieve the profiles within that list
        
        Parameters
        ---
        :param (*str*) `list_id`: Klaviyo ID of list to retrieve details and profiles for

        Returns
        ---
        :return `parsed_response` (dict): dict containing `data`,  `links`
        
        <hr>
        
        ## Downstream Calls (Methods/Functions called)
        
         ### :class:`~integration_platform.connectors.klaviyo.KlaviyoAPI`.:meth:`~integration_platform.connectors.klaviyo.KlaviyoAPI._get_data_`
        
         ### :class:`~integration_platform.connectors.klaviyo.KlaviyoAPI`.:meth:`~integration_platform.connectors.klaviyo.KlaviyoAPI.get_list_profiles`
           
         
          - Retrieves all profiles belonging to the list with the passed list_id value
        '''        
        url = f'{self.url_lists}/{list_id}'
        parsed_response = self._get_data_(url=url, params='?additional-fields[list]=profile_count')
        try:
            self.logger.info(f'{parsed_response['data']['attributes']['profile_count']} profiles belong to {parsed_response['data']['attributes']['name']} list')
        except Exception as e:
            self.logger.warning(f"Couldn't parse list record count from response! {e}")
        profiles = self.get_list_profiles(url=url, profile_filter=profile_filter)
        bp = 'here'
        parsed_response['profiles'] = profiles
        self.logger.info(f'List parsed in full...Extract complete.')
        return parsed_response


    #MARK: get_list_profiles
    def get_list_profiles(self, url: str, profile_filter: str = ''):
        ''':class:`~integration_platform.connectors.klaviyo.KlaviyoAPI`.:meth:`~integration_platform.connectors.klaviyo.KlaviyoAPI.get_list_profiles`
        ---
        
        Given the URL of a list, retrieve all profiles belonging to it
        
        Parameters
        ---
        :param (*str*) `url`: Url to hit klayvio at. It should be the url that we retrieved the list data at, with `/profiles` appended
        
        Returns
        ---
        :return `parsed_profiles` (list[dict]): list of dictionaries containing profile data
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.connectors.klaviyo.KlaviyoAPI`.:meth:`~integration_platform.connectors.klaviyo.KlaviyoAPI.get_list`
        
        ## Downstream Calls (Methods/Functions called)
        
         ### :class:`~integration_platform.connectors.klaviyo.KlaviyoAPI`.:meth:`~integration_platform.connectors.klaviyo.KlaviyoAPI.get_profiles`
         ### :class:`~integration_platform.connectors.klaviyo.KlaviyoAPI`.:class:`~integration_platform.helpers.klaviyo_api_helper.KlaviyoAPIHelper`.:meth:`~integration_platform.helpers.klaviyo_api_helper.KlaviyoAPIHelper.consolidate_profiles`
        '''        
        url = f'{url}/profiles'
        filter = f'?{profile_filter}&' if profile_filter != '' else '?'
        params = f'{filter}additional-fields[profile]={','.join([s for s in self.fields_add_profile])}&fields[profile]={','.join([s for s in self.fields_profile])}&page[size]=100'
        profiles = self.get_profiles(url=url, params=params)
        parsed_profiles = self.helper.consolidate_profiles(profiles=profiles)
        bp = 'here'
        return parsed_profiles



    #MARK: _get_data_
    def _get_data_(self, url: str, params: str = ''):
        ''':class:`~integration_platform.connectors.klaviyo.KlaviyoAPI`.:meth:`~integration_platform.connectors.klaviyo.KlaviyoAPI._get_data_`
        ---
        
        Given a URL and parameters, sends request to Klaviyo API
        
        Parameters
        ---
        :param (*str*) `url`: _description_
        
                
           ### ***Optional***
        :param (*str = ''*) `log_prefix`: String to prepend to any logger outputs. Usually used when iterating, like `'keyvalue1, 1/150: '`, `'keyvalue2, 2/150: '` and so on 
        
        Returns
        ---
        :return `parsed_response` (dict): dict of data from Klaviyo API
        
        <hr>

        ## Downstream Calls (Methods/Functions called)
        
         ### :class:`~integration_platform.helpers.klaviyo_api_helper.KlaviyoAPIHelper`.:meth:`~integration_platform.helpers.klaviyo_api_helper.KlaviyoAPIHelper.parse_response`
        
          - Returns json formatted response
        '''        
        full_url = f'{url}{params}'
        response = requests.get(url=full_url, headers=self.headers)
        parsed_response = self.helper.parse_response(response=response, url=url)
        return parsed_response



    #MARK: __page__
    def __page__(self, parsed_response: dict):
        paging_links = parsed_response.get('links')
        if paging_links == None or paging_links['next'] == None:
            self.logger.info(f'No more pages found')
            return False, ''
        return True, parsed_response['links']['next']

        #fill rate for

    
    #MARK: _set_fields_
    def _set_fields_(self):
        # self.fields_profile = ['anonymous_id', 'created', 'email', 'external_id', 'first_name', 'id', 'image', 'joined_group_at', 'last_event_date', 'last_name', 'locale', 'location', 'organization', 'phone_number', 'predictive_analytics', 'properties', 'subscriptions', 'title', 'updated', 'whatsapp_bsuid']
        self.fields_profile = ['created','email','external_id','first_name','id','image','joined_group_at','last_event_date','last_name','locale','location','location.address1','location.address2','location.city','location.country','location.ip','location.latitude','location.longitude','location.region','location.timezone','location.zip','organization','phone_number','predictive_analytics','predictive_analytics.average_days_between_orders','predictive_analytics.average_order_value','predictive_analytics.churn_probability','predictive_analytics.expected_date_of_next_order','predictive_analytics.historic_clv','predictive_analytics.historic_number_of_orders','predictive_analytics.predicted_clv','predictive_analytics.predicted_number_of_orders','predictive_analytics.ranked_channel_affinity','predictive_analytics.total_clv','properties','subscriptions','subscriptions.email','subscriptions.email.click_tracking','subscriptions.email.click_tracking.can_receive','subscriptions.email.click_tracking.consent','subscriptions.email.click_tracking.consent_timestamp','subscriptions.email.click_tracking.created_timestamp','subscriptions.email.click_tracking.last_updated','subscriptions.email.click_tracking.metadata','subscriptions.email.click_tracking.valid_until','subscriptions.email.marketing','subscriptions.email.marketing.can_receive_email_marketing','subscriptions.email.marketing.consent','subscriptions.email.marketing.consent_timestamp','subscriptions.email.marketing.custom_method_detail','subscriptions.email.marketing.double_optin','subscriptions.email.marketing.last_updated','subscriptions.email.marketing.list_suppressions','subscriptions.email.marketing.method','subscriptions.email.marketing.method_detail','subscriptions.email.marketing.suppression','subscriptions.email.open_tracking','subscriptions.email.open_tracking.can_receive','subscriptions.email.open_tracking.consent','subscriptions.email.open_tracking.consent_timestamp','subscriptions.email.open_tracking.created_timestamp','subscriptions.email.open_tracking.last_updated','subscriptions.email.open_tracking.metadata','subscriptions.email.open_tracking.valid_until','subscriptions.mobile_push','subscriptions.mobile_push.marketing','subscriptions.mobile_push.marketing.can_receive_push_marketing','subscriptions.mobile_push.marketing.consent','subscriptions.mobile_push.marketing.consent_timestamp','subscriptions.sms','subscriptions.sms.marketing','subscriptions.sms.marketing.can_receive_sms_marketing','subscriptions.sms.marketing.consent','subscriptions.sms.marketing.consent_timestamp','subscriptions.sms.marketing.last_updated','subscriptions.sms.marketing.method','subscriptions.sms.marketing.method_detail','subscriptions.sms.transactional','subscriptions.sms.transactional.can_receive_sms_transactional','subscriptions.sms.transactional.consent','subscriptions.sms.transactional.consent_timestamp','subscriptions.sms.transactional.last_updated','subscriptions.sms.transactional.method','subscriptions.sms.transactional.method_detail','subscriptions.whatsapp','subscriptions.whatsapp.conversational','subscriptions.whatsapp.conversational.can_receive','subscriptions.whatsapp.conversational.consent','subscriptions.whatsapp.conversational.consent_timestamp','subscriptions.whatsapp.conversational.created_timestamp','subscriptions.whatsapp.conversational.last_updated','subscriptions.whatsapp.conversational.metadata','subscriptions.whatsapp.conversational.phone_number','subscriptions.whatsapp.conversational.valid_until','subscriptions.whatsapp.marketing','subscriptions.whatsapp.marketing.can_receive','subscriptions.whatsapp.marketing.consent','subscriptions.whatsapp.marketing.consent_timestamp','subscriptions.whatsapp.marketing.created_timestamp','subscriptions.whatsapp.marketing.last_updated','subscriptions.whatsapp.marketing.metadata','subscriptions.whatsapp.marketing.phone_number','subscriptions.whatsapp.marketing.valid_until','subscriptions.whatsapp.transactional','subscriptions.whatsapp.transactional.can_receive','subscriptions.whatsapp.transactional.consent','subscriptions.whatsapp.transactional.consent_timestamp','subscriptions.whatsapp.transactional.created_timestamp','subscriptions.whatsapp.transactional.last_updated','subscriptions.whatsapp.transactional.metadata','subscriptions.whatsapp.transactional.phone_number','subscriptions.whatsapp.transactional.valid_until','title','updated',]
        self.fields_add_profile = ['subscriptions', 'predictive_analytics']