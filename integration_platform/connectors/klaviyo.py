from __future__ import annotations
from typing import TYPE_CHECKING,  Any, Iterator
if TYPE_CHECKING:
    from integration_platform.pipelines.klaviyo_newsletter import KlaviyoNewsletter
    from integration_platform.pipelines.klaviyo_data_push import KlaviyoDataPush
import logging
from integration_platform.config.settings import KLAYVIO
from integration_platform.helpers.klaviyo_api_helper import KlaviyoAPIHelper
import requests
import json

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
    def __init__(self, pipeline: KlaviyoNewsletter | KlaviyoDataPush) -> None:
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
        self._set_mappings_()
        pass

    #MARK: _set_urls_
    def _set_urls_(self):
        self.url_lists = f'{self.base_url}/lists'
        self.url_profiles = f'{self.base_url}/profiles'



    #MARK: get_profiles
    def get_profiles(self, url: str = 'https://a.klaviyo.com/api/profiles', filter: str = '', params: str = 'page[size]=100'):
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
        filter = f'?filter={filter}&' if filter != '' else '?'
        params = f'{filter}additional-fields[profile]={','.join([s for s in self.fields_add_profile])}&fields[profile]={','.join([s for s in self.fields_profile])}&page[size]=100'
        while True:
            parsed_response = self._get_data_(url=url, params=params) if not paged else self._get_data_(url=url)
            profiles.extend(parsed_response.get('data') or [])
            self.logger.info(f'{len(profiles)} Profiles parsed successfully')
            keep_going, next_page = self.__page__(parsed_response=parsed_response)
            if not keep_going:# or len(profiles) > 1000:
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
        params = f'{filter}additional-fields[profile]={','.join([s for s in self.fields_add_profile])}&fields[profile]={','.join([s for s in self.list_fields_profile])}&page[size]=100'
        profiles = self.get_profiles(url=url, params=params)
        parsed_profiles = self.helper.consolidate_profiles(profiles=profiles)
        bp = 'here'
        return parsed_profiles

    def create_or_update_profile(self, payload: dict):
        url = 'https://a.klaviyo.com/api/profile-import'
        response = self._post_data_(url=url, payload=payload)
        return response

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

    def _post_data_(self, url: str, payload: dict):
        pl = json.dumps(payload)
        response = requests.post(url=url, headers=self.headers, data=pl)
        t_response = response.text
        return response


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
        self.fields_profile = ['anonymous_id', 'created', 'email', 'external_id', 'first_name', 'id', 'image', 'last_event_date', 'last_name', 'locale', 'location', 'organization', 'phone_number', 'predictive_analytics', 'properties', 'subscriptions', 'title', 'updated', 'whatsapp_bsuid']
        self.list_fields_profile = ['created','email','external_id','first_name','id','image','joined_group_at','last_event_date','last_name','locale','location','location.address1','location.address2','location.city','location.country','location.ip','location.latitude','location.longitude','location.region','location.timezone','location.zip','organization','phone_number','predictive_analytics','predictive_analytics.average_days_between_orders','predictive_analytics.average_order_value','predictive_analytics.churn_probability','predictive_analytics.expected_date_of_next_order','predictive_analytics.historic_clv','predictive_analytics.historic_number_of_orders','predictive_analytics.predicted_clv','predictive_analytics.predicted_number_of_orders','predictive_analytics.ranked_channel_affinity','predictive_analytics.total_clv','properties','subscriptions','subscriptions.email','subscriptions.email.click_tracking','subscriptions.email.click_tracking.can_receive','subscriptions.email.click_tracking.consent','subscriptions.email.click_tracking.consent_timestamp','subscriptions.email.click_tracking.created_timestamp','subscriptions.email.click_tracking.last_updated','subscriptions.email.click_tracking.metadata','subscriptions.email.click_tracking.valid_until','subscriptions.email.marketing','subscriptions.email.marketing.can_receive_email_marketing','subscriptions.email.marketing.consent','subscriptions.email.marketing.consent_timestamp','subscriptions.email.marketing.custom_method_detail','subscriptions.email.marketing.double_optin','subscriptions.email.marketing.last_updated','subscriptions.email.marketing.list_suppressions','subscriptions.email.marketing.method','subscriptions.email.marketing.method_detail','subscriptions.email.marketing.suppression','subscriptions.email.open_tracking','subscriptions.email.open_tracking.can_receive','subscriptions.email.open_tracking.consent','subscriptions.email.open_tracking.consent_timestamp','subscriptions.email.open_tracking.created_timestamp','subscriptions.email.open_tracking.last_updated','subscriptions.email.open_tracking.metadata','subscriptions.email.open_tracking.valid_until','subscriptions.mobile_push','subscriptions.mobile_push.marketing','subscriptions.mobile_push.marketing.can_receive_push_marketing','subscriptions.mobile_push.marketing.consent','subscriptions.mobile_push.marketing.consent_timestamp','subscriptions.sms','subscriptions.sms.marketing','subscriptions.sms.marketing.can_receive_sms_marketing','subscriptions.sms.marketing.consent','subscriptions.sms.marketing.consent_timestamp','subscriptions.sms.marketing.last_updated','subscriptions.sms.marketing.method','subscriptions.sms.marketing.method_detail','subscriptions.sms.transactional','subscriptions.sms.transactional.can_receive_sms_transactional','subscriptions.sms.transactional.consent','subscriptions.sms.transactional.consent_timestamp','subscriptions.sms.transactional.last_updated','subscriptions.sms.transactional.method','subscriptions.sms.transactional.method_detail','subscriptions.whatsapp','subscriptions.whatsapp.conversational','subscriptions.whatsapp.conversational.can_receive','subscriptions.whatsapp.conversational.consent','subscriptions.whatsapp.conversational.consent_timestamp','subscriptions.whatsapp.conversational.created_timestamp','subscriptions.whatsapp.conversational.last_updated','subscriptions.whatsapp.conversational.metadata','subscriptions.whatsapp.conversational.phone_number','subscriptions.whatsapp.conversational.valid_until','subscriptions.whatsapp.marketing','subscriptions.whatsapp.marketing.can_receive','subscriptions.whatsapp.marketing.consent','subscriptions.whatsapp.marketing.consent_timestamp','subscriptions.whatsapp.marketing.created_timestamp','subscriptions.whatsapp.marketing.last_updated','subscriptions.whatsapp.marketing.metadata','subscriptions.whatsapp.marketing.phone_number','subscriptions.whatsapp.marketing.valid_until','subscriptions.whatsapp.transactional','subscriptions.whatsapp.transactional.can_receive','subscriptions.whatsapp.transactional.consent','subscriptions.whatsapp.transactional.consent_timestamp','subscriptions.whatsapp.transactional.created_timestamp','subscriptions.whatsapp.transactional.last_updated','subscriptions.whatsapp.transactional.metadata','subscriptions.whatsapp.transactional.phone_number','subscriptions.whatsapp.transactional.valid_until','title','updated',]
        self.fields_add_profile = ['subscriptions', 'predictive_analytics']
        self.payload_profile = {
            'data': {
                'type': 'profile',
                'attributes': {
                    'email': None,
                    'phone_number': None,
                    'location': {},
                    'properties': {}
                }
            }
        }


    #MARK: _set_mappings_
    def _set_mappings_(self):
        self.map_attributes_update = {
            'id': 'ID',
            'phone_number': 'PhoneNumber',     # parsed via parse_phone
            'email': 'Email',
            'first_name': 'FirstName',         # pascal-cased, truncated to 55 chars
            'last_name': 'LastName',           # pascal-cased, truncated to 55 chars
            # 'Name' is derived: f'{FirstName} {LastName}' from first_name + last_name
            'organization': 'Organization',
            'title': 'Title',
            'external_id': 'ExternalID',
            'locale': 'Locale',
            # 'phone_number': 'RawPhoneNumber',  # same source as PhoneNumber, unparsed
            'phone_number': 'PhoneNumberFmt',  # same source as PhoneNumber, unparsed
            'created': 'Created',
            'updated': 'Updated',
            'joined_group_at': 'JoinedGroupAt',
            'last_event_date': 'LastEventDate',
        }
        self.map_attributes_create = {
            'ID': 'id',
            'PhoneNumber': 'phone_number',
            'Email': 'email',
            'FirstName': 'first_name',
            'LastName': 'last_name',
            'Organization': 'organization',
            'Title': 'title',
            'ExternalID': 'external_id',
            'Locale': 'locale',
            # 'PhoneNumberFmt': 'phone_number',  # same target as PhoneNumber, would overwrite
            'Created': 'created',
            'Updated': 'updated',
            'JoinedGroupAt': 'joined_group_at',
            'LastEventDate': 'last_event_date',
        }

        self.map_subscriptions_update = {
            'email': {
                'marketing': {
                    'can_receive_email_marketing': 'Mkt_Email_CanReceiveEmail',
                    'consent': 'Mkt_Email_Consent',
                    'consent_timestamp': 'Mkt_Email_ConsentTimestamp',
                    'last_updated': 'Mkt_Email_LastUpdated',
                    'method': 'Mkt_Email_Method',
                    'method_detail': 'Mkt_Email_MethodDetail',
                    'custom_method_detail': 'Mkt_Email_CustomMethodDetail',
                    'double_optin': 'Mkt_Email_DoubleOptin',
                    # 'suppression': 'Mkt_Email_Suppression',
                    # 'list_suppressions': 'Mkt_Email_ListSuppressions',
                },
                'open_tracking': {
                    'consent': 'OpenTrk_Email_Consent',
                    'consent_timestamp': 'OpenTrk_Email_ConsentTimestamp',
                    'last_updated': 'OpenTrk_Email_LastUpdated',
                    'created_timestamp': 'OpenTrk_Email_CreatedTimestamp',
                    'metadata': 'OpenTrk_Email_Metadata',
                    'can_receive': 'OpenTrk_Email_CanReceive',
                    'valid_until': 'OpenTrk_Email_ValidUntil',
                },
                'click_tracking': {
                    'consent': 'ClickTrk_Email_Consent',
                    'consent_timestamp': 'ClickTrk_Email_ConsentTimestamp',
                    'last_updated': 'ClickTrk_Email_LastUpdated',
                    'created_timestamp': 'ClickTrk_Email_CreatedTimestamp',
                    'metadata': 'ClickTrk_Email_Metadata',
                    'can_receive': 'ClickTrk_Email_CanReceive',
                    'valid_until': 'ClickTrk_Email_ValidUntil',
                },
            },
            'sms': {
                'marketing': {
                    'can_receive_sms_marketing': 'Mkt_SMS_CanReceiveSMS',
                    'consent': 'Mkt_SMS_Consent',
                    'consent_timestamp': 'Mkt_SMS_ConsentTimestamp',
                    'method': 'Mkt_SMS_Method',
                    'method_detail': 'Mkt_SMS_MethodDetail',
                    'last_updated': 'Mkt_SMS_LastUpdated',
                },
                'transactional': {
                    'can_receive_sms_transactional': 'Txn_SMS_CanReceiveSMS',
                    'consent': 'Txn_SMS_Consent',
                    'consent_timestamp': 'Txn_SMS_ConsentTimestamp',
                    'method': 'Txn_SMS_Method',
                    'method_detail': 'Txn_SMS_MethodDetail',
                    'last_updated': 'Txn_SMS_LastUpdated',
                },
            },
            'mobile_push': {
                'marketing': {
                    'can_receive_push_marketing': 'Mkt_Push_CanReceivePush',
                    'consent': 'Mkt_Push_Consent',
                    'consent_timestamp': 'Mkt_Push_ConsentTimestamp',
                },
            },
        }

        self.map_location_create = {
            'Address1': 'address1',
            'Address2': 'address2',
            'City': 'city',
            'Country': 'country',
            'State': 'region',
            'Zip': 'zip',
            
        }
        self.map_location_update = {
            'address1': 'Address1',
            'address2': 'Address2',
            'city': 'City',
            'country': 'Country',
            'region': 'State',
            'zip': 'Zip',
        }
        
        self.map_properties_update = {
            'Accepts Marketing': 'AcceptsMarketing',
            'Shopify Tags': 'ShopifyTags',
            'Date Created': 'DateCreated',
            'Last Mailed Date': 'LastMailedDate',
            'Last Opened Date': 'LastOpenedDate',
            '$consent': 'Consent',
            '$consent_timestamp': 'ConsentTimestamp',
            '$source': 'Source',
            '$phone_number_region': 'PhoneNumberRegion',
            'Hubspot Record ID': 'HubspotRecordID',
            'Lead Status - Phone': 'LeadStatusPhone',
            'Contact Owner - Phone': 'ContactOwnerPhone',
            'timeStamp': 'Timestamp',
            'creative_id': 'CreativeID',
            'sms_attentive_signup': 'SMSAttentiveSignup',
            '$sms_consent_method': 'SMSConsentMethod',
            '$consent_method': 'ConsentMethod',
            '$consent_form_id': 'ConsentFormID',
            '$consent_form_version': 'ConsentFormVersion',
            'Expected Date Of Next Order': 'ExpectedDateOfNextOrder',
            'Shopping For': 'ShoppingFor',
            'Mobility Issues?': 'MobilityIssues',
            'Features': 'Features',
            'Brand': 'Brand',
            'Veteran_Status': 'VeteranStatus',
            'Birthday': 'Birthday',
            'clicks': 'Clicks',
            'Opens': 'Opens',
            'Full Name': 'FullName',
            'Customer ID': 'CustomerID',
            'mothers_day_opt_out': 'MothersDayOptOut',
            'Number of Orders': 'NumberOfOrders',
            '$latitude': 'Latitude',
            '$longitude': 'Longitude',
            'Initial Source': 'InitialSource',
            'Last Source': 'LastSource',
            'Store Interest': 'StoreInterest',
            'coupon': 'Coupon',
            'Okendo Family Name': 'OkendoFamilyName',
            'Okendo Given Name': 'OkendoGivenName',
            'Product': 'Product',
            'source': 'Source',
            'company': 'Company',
            'hubspot_original_source': 'HubspotOriginalSource',
            'hubspot_original_source_drill_down_1': 'HubspotOriginalSourceDrillDown1',
            'hubspot_original_source_drill_down_2': 'HubspotOriginalSourceDrillDown2',
            'product': 'Product',
            'product_for_you_or_someone_else': 'ProductForYouOrSomeoneElse',
            'primary_product_user': 'PrimaryProductUser',
            'type_of_first_engagement': 'TypeOfFirstEngagement',
            'lead_source': 'LeadSource',
            'bread_finance_outcome': 'BreadFinanceOutcome',
            'shipping_state': 'ShippingState',
            'shipping_zip': 'ShippingZip',
            'text_opt_in': 'TextOptIn',
            'email_option': 'EmailOption',
            'member_has_accessed_private_content': 'MemberHasAccessedPrivateContent',
            'legal_basis': 'LegalBasis',
            'Okendo Number of Survey Responses': 'OkendoNumberOfSurveyResponses',
            'Amazon_Interest': 'AmazonInterest',
            'Last Referring Domain': 'LastReferringDomain',
            'Interested in Category': 'InterestedInCategory',
            'Has received digital catalog': 'HasReceivedDigitalCatalog',
            'Amazon_or_Store': 'AmazonOrStore',
            'fathers_day_opt_out': 'FathersDayOptOut',
            'Initial Referring Domain': 'InitialReferringDomain',
            'Last Contacted on Phone': 'LastContactedOnPhone',
            'last_event_date': 'LastEventDate',
            'Okendo Average Review Rating': 'OkendoAverageReviewRating',
            'Okendo Has Submitted Media': 'OkendoHasSubmittedMedia',
            'Okendo Latest Review Rating': 'OkendoLatestReviewRating',
            'Okendo Number of Reviews': 'OkendoNumberOfReviews',
            'Okendo Average Review Sentiment': 'OkendoAverageReviewSentiment',
            'Okendo Latest Review Sentiment': 'OkendoLatestReviewSentiment',
            'User_Status': 'UserStatus',
            'Additional Email': 'AdditionalEmail',
            'Call Disposition': 'CallDisposition',
            'Date Order Placed': 'DateOrderPlaced',
            'Rep Email': 'RepEmail',
            'Unengaged': 'Unengaged',
            'Okendo Latest NPS Category': 'OkendoLatestNPSCategory',
            'Okendo Latest NPS': 'OkendoLatestNPS',
            'Okendo Latest NPS Date': 'OkendoLatestNPSDate',
            'Type of First Engagement (hubspot)': 'TypeOfFirstEngagementHubspot',
            'Item Description': 'ItemDescription',
            'undefined': 'Undefined',
            'UGC Free Item': 'UgcFreeItem',
            'company_id': 'CompanyID',
            'Email Content Preference': 'EmailContentPreference',
            'Primary Product User': 'PrimaryProductUser',
            'UTM Content': 'UTMContent',
            # set in __do_utms__, each merges two source keys
            'utm_source': 'UTMSource',   'UTM Source': 'UTMSource',
            'utm_medium': 'UTMMedium',   'UTM Medium': 'UTMMedium',
            'utm_campaign': 'UTMCampaign', 'UTM Campaign': 'UTMCampaign',
            'utm_term': 'UTMTerm',       'UTM Term': 'UTMTerm',
        }
        self.map_properties_create = {
            'AcceptsMarketing': 'Accepts Marketing',
            'ShopifyTags': 'Shopify Tags',
            'DateCreated': 'Date Created',
            'LastMailedDate': 'Last Mailed Date',
            'LastOpenedDate': 'Last Opened Date',
            'Consent': '$consent',
            'ConsentTimestamp': '$consent_timestamp',
            'Source': '$source',               # update also maps 'source' -> 'Source'
            'PhoneNumberRegion': '$phone_number_region',
            'HubspotRecordID': 'Hubspot Record ID',
            'RecordID': 'Hubspot Record ID',
            'LeadStatusPhone': 'Lead Status - Phone',
            'LeadStatus': 'Lead Status - Phone',
            'ContactOwnerPhone': 'Contact Owner - Phone',
            'Timestamp': 'timeStamp',
            'CreativeID': 'creative_id',
            'SMSAttentiveSignup': 'sms_attentive_signup',
            'SMSConsentMethod': '$sms_consent_method',
            'ConsentMethod': '$consent_method',
            'ConsentFormID': '$consent_form_id',
            'ConsentFormVersion': '$consent_form_version',
            'ExpectedDateOfNextOrder': 'Expected Date Of Next Order',
            'ShoppingFor': 'Shopping For',
            'MobilityIssues': 'Mobility Issues?',
            'Features': 'Features',
            'Brand': 'Brand',
            'VeteranStatus': 'Veteran_Status',
            'Birthday': 'Birthday',
            'Clicks': 'clicks',
            'Opens': 'Opens',
            'FullName': 'Full Name',
            'CustomerID': 'Customer ID',
            'MothersDayOptOut': 'mothers_day_opt_out',
            'NumberOfOrders': 'Number of Orders',
            'Latitude': '$latitude',
            'Longitude': '$longitude',
            'InitialSource': 'Initial Source',
            'LastSource': 'Last Source',
            'StoreInterest': 'Store Interest',
            'Coupon': 'coupon',
            'OkendoFamilyName': 'Okendo Family Name',
            'OkendoGivenName': 'Okendo Given Name',
            'Product': 'Product',              # update also maps 'product' -> 'Product'
            'Company': 'company',
            'HubspotOriginalSource': 'hubspot_original_source',
            'HubspotOriginalSourceDrillDown1': 'hubspot_original_source_drill_down_1',
            'HubspotOriginalSourceDrillDown2': 'hubspot_original_source_drill_down_2',
            'ProductForYouOrSomeoneElse': 'product_for_you_or_someone_else',
            'PrimaryProductUser': 'primary_product_user',  # update also maps 'Primary Product User'
            'TypeOfFirstEngagement': 'type_of_first_engagement',
            'LeadSource': 'lead_source',
            'BreadFinanceOutcome': 'bread_finance_outcome',
            'ShippingState': 'shipping_state',
            'ShippingZip': 'shipping_zip',
            'TextOptIn': 'text_opt_in',
            'EmailOption': 'email_option',
            'MemberHasAccessedPrivateContent': 'member_has_accessed_private_content',
            'LegalBasis': 'legal_basis',
            'OkendoNumberOfSurveyResponses': 'Okendo Number of Survey Responses',
            'AmazonInterest': 'Amazon_Interest',
            'LastReferringDomain': 'Last Referring Domain',
            'InterestedInCategory': 'Interested in Category',
            'HasReceivedDigitalCatalog': 'Has received digital catalog',
            'AmazonOrStore': 'Amazon_or_Store',
            'FathersDayOptOut': 'fathers_day_opt_out',
            'InitialReferringDomain': 'Initial Referring Domain',
            'LastContactedOnPhone': 'Last Contacted on Phone',
            'LastEventDate': 'last_event_date',
            'OkendoAverageReviewRating': 'Okendo Average Review Rating',
            'OkendoHasSubmittedMedia': 'Okendo Has Submitted Media',
            'OkendoLatestReviewRating': 'Okendo Latest Review Rating',
            'OkendoNumberOfReviews': 'Okendo Number of Reviews',
            'OkendoAverageReviewSentiment': 'Okendo Average Review Sentiment',
            'OkendoLatestReviewSentiment': 'Okendo Latest Review Sentiment',
            'UserStatus': 'User_Status',
            'AdditionalEmail': 'Additional Email',
            'CallDisposition': 'Call Disposition',
            'DateOrderPlaced': 'Date Order Placed',
            'RepEmail': 'Rep Email',
            'Unengaged': 'Unengaged',
            'OkendoLatestNPSCategory': 'Okendo Latest NPS Category',
            'OkendoLatestNPS': 'Okendo Latest NPS',
            'OkendoLatestNPSDate': 'Okendo Latest NPS Date',
            'TypeOfFirstEngagementHubspot': 'Type of First Engagement (hubspot)',
            'ItemDescription': 'Item Description',
            'Undefined': 'undefined',
            'UgcFreeItem': 'UGC Free Item',
            'CompanyID': 'company_id',
            'EmailContentPreference': 'Email Content Preference',
            'UTMContent': 'UTM Content',
            # update merges two source keys each; create writes back to the snake_case key
            'UTMSource': 'utm_source',     # or 'UTM Source'
            'UTMMedium': 'utm_medium',     # or 'UTM Medium'
            'UTMCampaign': 'utm_campaign', # or 'UTM Campaign'
            'UTMTerm': 'utm_term',         # or 'UTM Term'
        }
