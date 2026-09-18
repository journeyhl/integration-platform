from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.klaviyo_newsletter import KlaviyoNewsletter
import logging
import polars as pl
from datetime import datetime
from zoneinfo import ZoneInfo
import json
from typing import Literal
class Transform:
    def __init__(self, pipeline: KlaviyoNewsletter):
        self.pipeline = pipeline
        self.default_transformer = pipeline.default_transformer
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.Transform')
        self.date_formats = {}
        pass

    #MARK: landing
    def landing(self, data_extract):
        data_transformed = self.profiles_landing(data_extract['profiles'])
        now = datetime.now(tz=ZoneInfo('America/New_York'))
        self.pipeline.default_loader.add_to_list(ldata=data_transformed['klaviyo.ProfileHeader'], additions={'InsertedDT': now, 'LastChecked': data_extract['LastChecked']})
        self.pipeline.default_loader.add_to_list(ldata=data_transformed['klaviyo.ProfileProperties'], additions={'InsertedDT': now, 'LastChecked': data_extract['LastChecked']})
        self.pipeline.default_loader.add_to_list(ldata=data_transformed['klaviyo.ProfileSubscriptions'], additions={'InsertedDT': now, 'LastChecked': data_extract['LastChecked']})
        for row in data_transformed['klaviyo.ProfileProperties']:
            for k, v in row.items():
                if  isinstance(v, str) and '%' in v:
                    v = v.replace('%', 'pct')
                    bp = 'here'
        return data_transformed

    #MARK: profiles_landing
    def profiles_landing(self, profiles: list[dict]):
        ''':class:`~integration_platform.transform.klaviyo_newsletter.Transform`.:meth:`~integration_platform.transform.klaviyo_newsletter.Transform.profiles_landing`
        ---
        
        Method that drivers the transformation of the *profiles* piece of data_extract
        
        Parameters
        ---
        :param (*list[dict]*) `profiles`: Profiles retrieved from Klaviyo API
        
        Returns
        ---
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.transform.klaviyo_newsletter.Transform`.:meth:`~integration_platform.transform.klaviyo_newsletter.Transform.landing`
        
        ## Downstream Calls (Methods/Functions called)
        
         ### :class:`~integration_platform.transform.klaviyo_newsletter.Transform`.:meth:`~integration_platform.transform.klaviyo_newsletter.Transform._parse_properties_`
        
          - Parses a given profile's properties
        
         ### :class:`~integration_platform.transform.klaviyo_newsletter.Transform`.:meth:`~integration_platform.transform.klaviyo_newsletter.Transform._parse_subscriptions_`
        
          - Parses a given profile's subscription data
        '''        
        bp = 'here'
        self._distinct_properties_(profiles=profiles)
        total = len(profiles)
        headers = []
        parsed_properties = []
        parsed_subscriptions = []
        for i, p in enumerate(profiles):
            self.log_prefix = f'{i+1}/{total}: ' 
            bp = 'here'
            profile_header = self._profile_header_(profile=p)
            props = self._parse_properties_(profile=p)
            subs = self._parse_subscriptions_(profile=p)
            parsed_props = {'ID': profile_header['ID'], **props}
            parsed_subs = {'ID': profile_header['ID'], **subs}

            headers.append(profile_header)
            parsed_properties.append(parsed_props)
            parsed_subscriptions.append(parsed_subs)
            bp = 'here'
        data_transformed = {
            'klaviyo.ProfileHeader': headers,
            'klaviyo.ProfileProperties': parsed_properties,
            'klaviyo.ProfileSubscriptions': parsed_subscriptions
        }
        return data_transformed

    #MARK: _profile_header_
    def _profile_header_(self, profile: dict):
        p = {k: v for k, v in profile.items() if not isinstance(v, dict)}
        fname, lname, name = self.__do_header_names__(profile=p)
        header = {            
            'ID': p['id'],
            'PhoneNumber': self.default_transformer.parse_phone(phone_str=p['phone_number']),
            'Email': self.default_transformer.clean_string(string=p['email']),
            'FirstName': fname,
            'LastName': lname,
            'Name': self.default_transformer.clean_string(string=name),
            'Organization': self.default_transformer.string_case_pascal(string=p['organization']),
            'Title': self.default_transformer.string_case_pascal(string=p['title']),
            'ExternalID': self.default_transformer.clean_string(string=p['external_id']),
            'Locale': self.default_transformer.clean_string(string=p['locale']),
            'RawPhoneNumber': p['phone_number'],
            'Created': self.default_transformer.parse_date_str(date_str=p['created'], tries=0, format='%Y-%m-%dT%H:%M:%S', offset=True),
            'Updated': self.default_transformer.parse_date_str(date_str=p['updated'], tries=0, format='%Y-%m-%dT%H:%M:%S', offset=True),
            'JoinedGroupAt': self.default_transformer.parse_date_str(date_str=p['joined_group_at'], tries=0, format='%Y-%m-%dT%H:%M:%S', offset=True),
            'LastEventDate': self.default_transformer.parse_date_str(date_str=p['last_event_date'], tries=0, format='%Y-%m-%dT%H:%M:%S', offset=True),
        }
        return header

    def __do_header_names__(self, profile):
        def do_name(name: Literal['first_name', 'last_name']):
            parsed_name = profile[name] or ''
            if len(parsed_name) > 55:
                parsed_name = profile[name][:55]
            return parsed_name
        fname = self.default_transformer.string_case_pascal(string=do_name(name='first_name'))
        lname = self.default_transformer.string_case_pascal(string=do_name(name='last_name'))
        name = f'{f'{fname} ' if fname != None else ''}{lname if lname != None else ''}'
        return fname, lname, name

    #MARK: _parse_properties_
    def _parse_properties_(self, profile: dict) -> dict:
        ''':class:`~integration_platform.transform.klaviyo_newsletter.Transform`.:meth:`~integration_platform.transform.klaviyo_newsletter.Transform._parse_properties_`
        ---
        
        Given data for a particular Klaviyo profile, transform the properties returned
        
        Parameters
        ---
        :param (*dict*) `profile`: dict containing profile data from Klaviyo
        
        Returns
        ---
        :return `parsed_props` (dict): Transformed property data for a given profile
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.transform.klaviyo_newsletter.Transform`.:meth:`~integration_platform.transform.klaviyo_newsletter.Transform.profiles_landing`
        '''        
        self.logger.info(f'{self.log_prefix}Parsing properties...')
        props = profile['properties']
        shop_tags = self._list_props_(props=props, key='ShopifyTags')
        consent = self._list_props_(props=props, key='$consent')
        if props.get('Accepts Marketing') == None:
            accepts = False
        elif isinstance(props['Accepts Marketing'], str):
            accepts = True if props['Accepts Marketing'].lower() == 'true' else False
        elif isinstance(props['Accepts Marketing'], int):
            accepts = True if props['Accepts Marketing'] == 1 else False
        else:
            accepts = props['Accepts Marketings']
            
        parsed_props = {            
            'AcceptsMarketing': accepts,
            'ShopifyTags': shop_tags,
            'DateCreated': self._date_formatter_(date_str=props.get('Date Created'), key='Date Created'),
            'LastMailedDate': self._date_formatter_(date_str=props.get('Last Mailed Date'), key='Last Mailed Date'),
            'LastOpenedDate': self._date_formatter_(date_str=props.get('Last Opened Date'), key='Last Opened Date'),
            'Consent': consent,
            'ConsentTimestamp': self.default_transformer.parse_date_str(date_str=props.get('$consent_timestamp'), tries=0),
            'Source': props.get('$source'),
            'PhoneNumberRegion': props.get('$phone_number_region'),
            'HubspotRecordID': props.get('Hubspot Record ID'),
            'LeadStatusPhone': props.get('Lead Status - Phone'),
            'ContactOwnerPhone': props.get('Contact Owner - Phone'),
            'Timestamp': self.default_transformer.parse_date_str(date_str=props.get('timeStamp'), tries=0, offset=True if props.get('timeStamp') != None and '+' in props.get('timeStamp') else False),
            'CreativeID': props.get('creative_id'),
            'SMSAttentiveSignup': props.get('sms_attentive_signup'),
            'SMSConsentMethod': props.get('$sms_consent_method'),
            'ConsentMethod': props.get('$consent_method'),
            'ConsentFormID': props.get('$consent_form_id'),
            'ConsentFormVersion': props.get('$consent_form_version'),
            'ExpectedDateOfNextOrder': self._date_formatter_(date_str=props.get('Expected Date Of Next Order')),
            'ShoppingFor': self._list_props_(props=props, key='Shopping For'),
            'MobilityIssues': props.get('Mobility Issues?'),
            'Features': self._list_props_(props=props, key='Features'),
            'Brand': props.get('Brand'),
            'VeteranStatus': props.get('Veteran_Status'),
            'Birthday': self._date_formatter_(date_str=props.get('Birthday'), key='Birthday'),
            'Clicks': self.default_transformer.string_to_int(int_str=props.get('clicks')),
            'Opens': self.default_transformer.string_to_int(int_str=props.get('Opens')),
            'FullName': props.get('Full Name'),
            'CustomerID': props.get('Customer ID'),
            'MothersDayOptOut': props.get('mothers_day_opt_out'),
            'NumberOfOrders': props.get('Number of Orders'),
            'Latitude': props.get('$latitude'),
            'Longitude': props.get('$longitude'),
            'InitialSource': props.get('Initial Source'),
            'LastSource': props.get('Last Source'),
            'StoreInterest': props.get('Store Interest'),
            'Coupon': props.get('coupon'),
            'OkendoFamilyName': props.get('Okendo Family Name'),
            'OkendoGivenName': props.get('Okendo Given Name'),
            'Product': props.get('Product'),

            'Source': props.get('source'),
            'Company': props.get('company'),
            'HubspotOriginalSource': props.get('hubspot_original_source'),
            'HubspotOriginalSourceDrillDown1': props.get('hubspot_original_source_drill_down_1'),
            'HubspotOriginalSourceDrillDown2': props.get('hubspot_original_source_drill_down_2'),
            'Product': props.get('product'),
            'ProductForYouOrSomeoneElse': props.get('product_for_you_or_someone_else'),
            'PrimaryProductUser': props.get('primary_product_user'),
            'TypeOfFirstEngagement': props.get('type_of_first_engagement'),
            'LeadSource': props.get('lead_source'),
            'BreadFinanceOutcome': props.get('bread_finance_outcome'),
            'ShippingState': props.get('shipping_state'),
            'ShippingZip': props.get('shipping_zip'),
            'TextOptIn': props.get('text_opt_in'),
            'EmailOption': props.get('email_option'),
            'MemberHasAccessedPrivateContent': props.get('member_has_accessed_private_content'),
            'LegalBasis': props.get('legal_basis'),
            'OkendoNumberOfSurveyResponses': props.get('Okendo Number of Survey Responses'),
            'AmazonInterest': props.get('Amazon_Interest'),
            'LastReferringDomain': props.get('Last Referring Domain'),
            'InterestedInCategory': props.get('Interested in Category'),
            'HasReceivedDigitalCatalog': props.get('Has received digital catalog'),
            'AmazonOrStore': self._list_props_(props=props, key='Amazon_or_Store'),
            'FathersDayOptOut': props.get('fathers_day_opt_out'),
            'InitialReferringDomain': props.get('Initial Referring Domain'),
            'LastContactedOnPhone': props.get('Last Contacted on Phone'),
            'LastEventDate': self._date_formatter_(date_str=props.get('last_event_date')),
            'OkendoAverageReviewRating': props.get('Okendo Average Review Rating'),
            'OkendoHasSubmittedMedia': props.get('Okendo Has Submitted Media'),
            'OkendoLatestReviewRating': props.get('Okendo Latest Review Rating'),
            'OkendoNumberOfReviews': props.get('Okendo Number of Reviews'),
            'OkendoAverageReviewSentiment': props.get('Okendo Average Review Sentiment'),
            'OkendoLatestReviewSentiment': props.get('Okendo Latest Review Sentiment'),
            'UserStatus': props.get('User_Status'),
            'AdditionalEmail': props.get('Additional Email'),
            'CallDisposition': props.get('Call Disposition'),
            'DateOrderPlaced': props.get('Date Order Placed'),
            'RepEmail': props.get('Rep Email'),
            'Unengaged': props.get('Unengaged'),
            'OkendoLatestNPSCategory': props.get('Okendo Latest NPS Category'),
            'OkendoLatestNPS': props.get('Okendo Latest NPS'),
            'OkendoLatestNPSDate': props.get('Okendo Latest NPS Date'),
            'TypeOfFirstEngagementHubspot': props.get('Type of First Engagement (hubspot)'),
            'ItemDescription': props.get('Item Description'),
            'Undefined': props.get('undefined'),
            'UgcFreeItem': props.get('UGC Free Item'),
            'CompanyID': props.get('company_id'),
            'EmailContentPreference': self._list_props_(props=props, key='Email Content Preference'),
            'PrimaryProductUser': props.get('Primary Product User'),
            'UTMContent': props['UTM Content'].replace('%', 'pct') if props.get('UTM Content') != None else None,
        }
        parsed_props = self.__do_utms__(props=props, parsed_props=parsed_props)
        return parsed_props


    #MARK: __do_utms__
    def __do_utms__(self, props, parsed_props):
        def utms(key1, key2):
            v1 = props.get(key1)
            v2 = props.get(key2)
            v = v1 if v2 == None else f'{v1},{v2}'.replace('%', 'pct') if v1 != v2 and v2 != None else v2
            return v
        utm_source = utms(key1=props.get('utm_source'), key2=props.get('UTM Source'))
        utm_medium = utms(key1=props.get('utm_medium'), key2=props.get('UTM Medium'))
        utm_campaign = utms(key1=props.get('utm_campaign'), key2=props.get('UTM Campaign'))
        utm_term = utms(key1=props.get('utm_term'), key2=props.get('UTM Term'))
        parsed_props['UTMSource'] = utm_source
        parsed_props['UTMMedium'] = utm_medium
        parsed_props['UTMCampaign'] = utm_campaign
        parsed_props['UTMTerm'] = utm_term
        self.logger.info(f'{self.log_prefix}Parsed properties!')
        return parsed_props


    #MARK: _parse_subscriptions_
    def _parse_subscriptions_(self, profile: dict) -> dict:
        '''_replace_me_with_full_sphinx_docstring_
        ---
        
        put_summary_here
        
        Parameters
        ---
        :param (*dict*) `profile`: Data for a particular profile from Klaviyo
        
        Returns
        ---
        :return `parsed_subs` (dict): Dict containing consolidated subscription data for a given profile
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.transform.klaviyo_newsletter.Transform`.:meth:`~integration_platform.transform.klaviyo_newsletter.Transform.profiles_landing`
        
        ## Downstream Calls (Methods/Functions called)
        
         ### :class:`~integration_platform.transform.klaviyo_newsletter.Transform`.:meth:`~integration_platform.transform.klaviyo_newsletter.Transform.__parse_subs_email__`
        
          - Transforms email subscription data
        
         ### :class:`~integration_platform.transform.klaviyo_newsletter.Transform`.:meth:`~integration_platform.transform.klaviyo_newsletter.Transform.__parse_subs_sms__`
        
          - Transforms sms subscription data
        
         ### :class:`~integration_platform.transform.klaviyo_newsletter.Transform`.:meth:`~integration_platform.transform.klaviyo_newsletter.Transform.__parse_subs_mobile__`
        
          - Transforms mobile push notification subscription data
        '''        
        self.logger.info(f'{self.log_prefix}Parsing subscriptions...')
        subs = profile['subscriptions']

        emails = subs['email']
        sms = subs['sms']
        mobile = subs['mobile_push']
        whatsapp = subs['whatsapp']

        email_subs = self.__parse_subs_email__(emails=emails)
        sms_subs = self.__parse_subs_sms__(sms=sms)
        mobile_subs = self.__parse_subs_mobile__(mobile=mobile)
        parsed_subs = {**email_subs, **sms_subs, **mobile_subs}
        self.logger.info(f'{self.log_prefix}Parsed subscriptions!')
        return parsed_subs



    #MARK: __parse_subs_email__
    def __parse_subs_email__(self, emails: dict) -> dict:
        ''':class:`~integration_platform.transform.klaviyo_newsletter.Transform`.:meth:`~integration_platform.transform.klaviyo_newsletter.Transform.__parse_subs_email__`
        ---
        
        Transforms a given profile's email subscription data
        
        Parameters
        ---
        :param (*dict*) `emails`: Email subscription data for a particular profile
        
        Returns
        ---
        :return `email_subs` (dict): Formatted dict of email subscription data
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.transform.klaviyo_newsletter.Transform`.:meth:`~integration_platform.transform.klaviyo_newsletter.Transform._parse_subscriptions_`
        '''    
        if len(emails['marketing']['suppression']) > 1:
            bp = 'here'
        if len(emails['marketing']['list_suppressions']) > 1:
            bp = 'here'
        email_subs = {
            'Mkt_Email_CanReceiveEmail': emails['marketing']['can_receive_email_marketing'],
            'Mkt_Email_Consent': emails['marketing']['consent'],
            'Mkt_Email_ConsentTimestamp':self.default_transformer.parse_date_str(date_str=emails['marketing']['consent_timestamp'], tries=0, format='%Y-%m-%dT%H:%M:%S.%f', offset=True),
            'Mkt_Email_LastUpdated': self.default_transformer.parse_date_str(date_str=emails['marketing']['last_updated'], tries=0, format='%Y-%m-%dT%H:%M:%S.%f', offset=True),
            'Mkt_Email_Method': emails['marketing']['method'],
            'Mkt_Email_MethodDetail': emails['marketing']['method_detail'],
            'Mkt_Email_CustomMethodDetail': emails['marketing']['custom_method_detail'],
            'Mkt_Email_DoubleOptin': emails['marketing']['double_optin'],
            # 'Mkt_Email_Suppression': emails['marketing']['suppression'],
            # 'Mkt_Email_ListSuppressions': emails['marketing']['list_suppressions'],            
            'OpenTrk_Email_Consent': emails['open_tracking']['consent'],
            'OpenTrk_Email_ConsentTimestamp': self.default_transformer.parse_date_str(date_str=emails['open_tracking']['consent_timestamp'], tries=0, format='%Y-%m-%dT%H:%M:%S.%f', offset=True),
            'OpenTrk_Email_LastUpdated': self.default_transformer.parse_date_str(date_str=emails['open_tracking']['last_updated'], tries=0, format='%Y-%m-%dT%H:%M:%S.%f', offset=True),
            'OpenTrk_Email_CreatedTimestamp': self.default_transformer.parse_date_str(date_str=emails['open_tracking']['created_timestamp'], tries=0, format='%Y-%m-%dT%H:%M:%S.%f', offset=True),
            'OpenTrk_Email_Metadata': emails['open_tracking']['metadata'],
            'OpenTrk_Email_CanReceive': emails['open_tracking']['can_receive'],
            'OpenTrk_Email_ValidUntil': self.default_transformer.parse_date_str(date_str=emails['open_tracking']['valid_until'], tries=0, format='%Y-%m-%dT%H:%M:%S.%f', offset=True),
            'ClickTrk_Email_Consent': emails['click_tracking']['consent'],
            'ClickTrk_Email_ConsentTimestamp': self.default_transformer.parse_date_str(date_str=emails['click_tracking']['created_timestamp'], tries=0, format='%Y-%m-%dT%H:%M:%S.%f', offset=True),
            'ClickTrk_Email_LastUpdated': self.default_transformer.parse_date_str(date_str=emails['click_tracking']['last_updated'], tries=0, format='%Y-%m-%dT%H:%M:%S.%f', offset=True),
            'ClickTrk_Email_CreatedTimestamp': self.default_transformer.parse_date_str(date_str=emails['click_tracking']['created_timestamp'], tries=0, format='%Y-%m-%dT%H:%M:%S.%f', offset=True),
            'ClickTrk_Email_Metadata': emails['click_tracking']['metadata'],
            'ClickTrk_Email_CanReceive': emails['click_tracking']['can_receive'],
            'ClickTrk_Email_ValidUntil': self.default_transformer.parse_date_str(date_str=emails['click_tracking']['valid_until'], tries=0, format='%Y-%m-%dT%H:%M:%S.%f', offset=True),
        }
        return email_subs

    #MARK: __parse_subs_sms__
    def __parse_subs_sms__(self, sms: dict) -> dict:
        ''':class:`~integration_platform.transform.klaviyo_newsletter.Transform`.:meth:`~integration_platform.transform.klaviyo_newsletter.Transform.__parse_subs_sms__`
        ---
        
        Transforms a given profile's sms subscription data
        
        Parameters
        ---
        :param (*dict*) `sms`: SMS subscription data for a particular profile
        
        Returns
        ---
        :return `sms_subs` (dict): Formatted dict of SMS subscription data
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.transform.klaviyo_newsletter.Transform`.:meth:`~integration_platform.transform.klaviyo_newsletter.Transform._parse_subscriptions_`
        '''        
        sms_subs = {
            'Mkt_SMS_CanReceiveSMS': sms['marketing']['can_receive_sms_marketing'],
            'Mkt_SMS_Consent': sms['marketing']['consent'],
            'Mkt_SMS_ConsentTimestamp': self.default_transformer.parse_date_str(date_str=sms['marketing']['consent_timestamp'], tries=0, format='%Y-%m-%dT%H:%M:%S.%f', offset=True),
            'Mkt_SMS_Method': sms['marketing']['method'],
            'Mkt_SMS_MethodDetail': sms['marketing']['method_detail'],
            'Mkt_SMS_LastUpdated': self.default_transformer.parse_date_str(date_str=sms['marketing']['last_updated'], tries=0, format='%Y-%m-%dT%H:%M:%S.%f', offset=True),
            'Txn_SMS_CanReceiveSMS': sms['transactional']['can_receive_sms_transactional'],
            'Txn_SMS_Consent': sms['transactional']['consent'],
            'Txn_SMS_ConsentTimestamp': self.default_transformer.parse_date_str(date_str=sms['transactional']['consent_timestamp'], tries=0, format='%Y-%m-%dT%H:%M:%S.%f', offset=True),
            'Txn_SMS_Method': sms['transactional']['method'],
            'Txn_SMS_MethodDetail': sms['transactional']['method_detail'],
            'Txn_SMS_LastUpdated': self.default_transformer.parse_date_str(date_str=sms['transactional']['last_updated'], tries=0, format='%Y-%m-%dT%H:%M:%S.%f', offset=True),
        }
        
        
        return sms_subs

    #MARK: __parse_subs_mobile__
    def __parse_subs_mobile__(self, mobile: dict) -> dict:
        ''':class:`~integration_platform.transform.klaviyo_newsletter.Transform`.:meth:`~integration_platform.transform.klaviyo_newsletter.Transform.__parse_subs_mobile__`
        ---
        
        Transforms a given profile's mobile push notification subscription data
        
        Parameters
        ---
        :param (*dict*) `mobile`: Mobile push notification subscription data for a particular profile
        
        Returns
        ---
        :return `mobile_subs` (dict): Formatted dict of Mobile push notification subscription data
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.transform.klaviyo_newsletter.Transform`.:meth:`~integration_platform.transform.klaviyo_newsletter.Transform._parse_subscriptions_`
        '''       
        mobile_subs = {
            'Mkt_Push_CanReceivePush': mobile['marketing']['can_receive_push_marketing'],
            'Mkt_Push_Consent': mobile['marketing']['consent'],
            'Mkt_Push_ConsentTimestamp': self.default_transformer.parse_date_str(date_str=mobile['marketing']['consent_timestamp'], tries=0, format='%Y-%m-%dT%H:%M:%S.%f', offset=True),
        }
        

        return mobile_subs

    #MARK: _date_formatter_
    def _date_formatter_(self, date_str: str | None, key: str = ''):
        ''':class:`~integration_platform.transform.klaviyo_newsletter.Transform`.:meth:`~integration_platform.transform.klaviyo_newsletter.Transform._date_formatter_`
        ---
        
        Since klaviyo has a bunch of different formats it stores its dates in, handle them all here
        
        Parameters
        ---
        :param (*str | None*) `date_str`: _description_
        
                
           ### ***Optional***
        :param (*str = ''*) `log_prefix`: String to prepend to any logger outputs. Usually used when iterating, like `'keyvalue1, 1/150: '`, `'keyvalue2, 2/150: '` and so on 
        
        Returns
        ---
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### _______replace_me_______
        
          - Description
        
         ### _______replace_me_______
           
          - Description
        
        ## Downstream Calls (Methods/Functions called)
        
         ### _______replace_me_______
        
          - Description
        
         ### _______replace_me_______
           
          - Description
        '''        
        def do_datetime(date_str, sep, seconds: str = ''):
            try:
                dt = datetime.strptime(date_str, f'%Y{sep}%m{sep}%d %H:%M{seconds}')
            except:
                dt = datetime.strptime(date_str, f'%m{sep}%d{sep}%Y %H:%M{seconds}')
            return dt
        if date_str == None:
            return None
        sep = '/' if '/' in date_str else '-' if '-' in date_str else '.'
        if len(date_str) <= 10:
            loc = date_str.find(sep)
            if loc > 3:
                date_str = '2024-02-29' if date_str == '2026-02-29' else date_str
                dt = datetime.strptime(date_str, f'%Y{sep}%m{sep}%d')
            else:
                dt = datetime.strptime(date_str, f'%m{sep}%d{sep}%Y')
            return dt

        if ' ' in date_str:
            spl = date_str.split(' ')
            if 'am' in date_str.lower():
                l = len(date_str)
                if l  == 18:
                    date_str = f'{spl[0]} 0{spl[1]}'
                    bp = 'here'
                if l == 19:
                    date_str = date_str[:16]
                    bp = 'here'
                dt = do_datetime(date_str, sep)
                bp = 'here'
            elif 'pm' in date_str.lower():
                t = spl[1]
                hour = t.split(':')
                time = int(hour[0]) + 12 if hour[0] != '12' else int(hour[0])
                new_date_str = f'{spl[0]} {time}:{hour[1]}'
                dt = do_datetime(new_date_str, sep)
                bp = 'here'
            else:
                seconds = '' if len(spl[1]) < 6 else ':%S' if len(spl[1]) < 9 else ':%S.%f'
                dt = do_datetime(date_str, sep, seconds=seconds)
                bp = 'here'
        else:
            if 'z' in date_str.lower():
                dt = self.default_transformer.parse_date_str(date_str=date_str, tries=0, format='%Y-%m-%dT%H:%M:%SZ')
            bp = 'here'
        return dt




#region Helpers
    def _list_props_(self, props, key: str):
        if isinstance(props.get(key), list):
            prop_value = None if props.get(key) == None or len(props[key]) == 0 else props[key][0] if len(props[key]) == 1  else ','.join(props[key])
        elif isinstance(props.get(key), str):
            prop_value = props.get(key)
        else:
            prop_value = None
        return prop_value

    #MARK: _distinct_properties_
    def _distinct_properties_(self, profiles):
        ''':class:`~integration_platform.transform.klaviyo_newsletter.Transform`.:meth:`~integration_platform.transform.klaviyo_newsletter.Transform._distinct_properties_`
        ---
        
        helper method.

        Returns all of a profile's properties that were returned from Klaviyo

        SInce Klaviyo operates in the style of not returning fields if a profile doesn't have a value for it (or another reason), we don't receive the same list of properties for each profile.


        '''        
        props = {}
        prop_list = [p['properties'] for p in profiles]
        for profiles_props in prop_list:
            for k, v in profiles_props.items():
                if props.get(k) == None:
                    props[k] = [v]
                else:
                    props[k].append([v])
        self.default_transformer.rename_columns(data=props, output_format='dict', strategy='.get', dict_name='props')
        bp = 'here'
    

#endregion




#region not in use
    def _parse_relationships_(self, profile: dict):
        self.logger.info(f'{self.log_prefix}Parsing relationships...')
        relations = profile['relationships']
        parsed_relations = {
        }
        bp = 'here'

        self.logger.info(f'{self.log_prefix}Parsed relationships!')
        return parsed_relations

#endregion

