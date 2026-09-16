from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.klaviyo_newsletter import KlaviyoNewsletter
import logging
import polars as pl
from datetime import datetime

class Transform:
    def __init__(self, pipeline: KlaviyoNewsletter):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.Transform')
        pass

    def landing(self, data_extract):
        parsed_profiles = self.profiles_landing(data_extract['profiles'])
        return parsed_profiles


    def _distinct_properties_(self, profiles):
        props = {}
        prop_list = [p['properties'] for p in profiles]
        for profiles_props in prop_list:
            for k, v in profiles_props.items():
                if props.get(k) == None:
                    props[k] = [v]
                else:
                    props[k].append([v])
        self.pipeline.default_transformer.rename_columns(data=props, output_format='dict', strategy='.get', dict_name='props')
        bp = 'here'

    def profiles_landing(self, profiles: list[dict]):
        bp = 'here'
        self._distinct_properties_(profiles=profiles)
        total = len(profiles)
        for i, p in enumerate(profiles):
            self.log_prefix = f'{i+1}/{total}: ' 
            bp = 'here'
            props = self._parse_properties_(profile=p)
            subs = self._parse_subscriptions_(profile=p)
            relations = self._parse_relationships_(profile=p)
        bp = 'here'


    def _parse_properties_(self, profile: dict):
        self.logger.info(f'{self.log_prefix}Parsing properties...')
        props = profile['properties']
        parsed_props = {            
            'AcceptsMarketing': props.get('Accepts Marketing'),
            'ShopifyTags': props['Shopify Tags'] if len(props['Shopify Tags'])<= 1 else ','.join(props['Shopify Tags']),
            'DateCreated': props.get('Date Created'),
            'LastMailedDate': props.get('Last Mailed Date'),
            'LastOpenedDate': props.get('Last Opened Date'),
            'Consent': props['$consent'] if len(props['$consent'])<= 1 else ','.join(props['$consent']),
            'ConsentTimestamp': props.get('$consent_timestamp'),
            'Source': props.get('$source'),
            'PhoneNumberRegion': props.get('$phone_number_region'),
            'HubspotRecordID': props.get('Hubspot Record ID'),
            'LeadStatusPhone': props.get('Lead Status - Phone'),
            'ContactOwnerPhone': props.get('Contact Owner - Phone'),
            'Timestamp': props.get('timeStamp'),
            'CreativeId': props.get('creative_id'),
            'SmsAttentiveSignup': props.get('sms_attentive_signup'),
            'SmsConsentMethod': props.get('$sms_consent_method'),
            'ConsentMethod': props.get('$consent_method'),
            'ConsentFormId': props.get('$consent_form_id'),
            'ConsentFormVersion': props.get('$consent_form_version'),
            'ExpectedDateOfNextOrder': props.get('Expected Date Of Next Order'),
            'UtmSource': props.get('utm_source'),
            'UtmMedium': props.get('utm_medium'),
            'UtmCampaign': props.get('utm_campaign'),
            'ShoppingFor': props.get('Shopping For'),
            'MobilityIssues?': props.get('Mobility Issues?'),
            'Features': props.get('Features'),
            'Brand': props.get('Brand'),
            'VeteranStatus': props.get('Veteran_Status'),
            'Birthday': props.get('Birthday'),
            'Clicks': props.get('clicks'),
            'Opens': props.get('Opens'),
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
            'UtmContent': props.get('utm_content'),
            'UtmTerm': props.get('utm_term'),
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
            'AmazonOrStore': props.get('Amazon_or_Store'),
            'FathersDayOptOut': props.get('fathers_day_opt_out'),
            'InitialReferringDomain': props.get('Initial Referring Domain'),
            'UtmCampaign': props.get('UTM Campaign'),
            'UtmMedium': props.get('UTM Medium'),
            'UtmSource': props.get('UTM Source'),
            'UtmTerm': props.get('UTM Term'),
            'LastContactedOnPhone': props.get('Last Contacted on Phone'),
            'LastEventDate': props.get('last_event_date'),
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
            'UtmContent': props.get('UTM Content'),
            'TypeOfFirstEngagementHubspot': props.get('Type of First Engagement (hubspot)'),
            'ItemDescription': props.get('Item Description'),
            'Undefined': props.get('undefined'),
            'UgcFreeItem': props.get('UGC Free Item'),
            'CompanyId': props.get('company_id'),
            'EmailContentPreference': props.get('Email Content Preference'),
            'PrimaryProductUser': props.get('Primary Product User'),
        }
        self.logger.info(f'{self.log_prefix}Parsed properties!')
        return parsed_props

    
    def _parse_subscriptions_(self, profile: dict):
        self.logger.info(f'{self.log_prefix}Parsing subscriptions...')
        subs = profile['subscriptions']

        emails = subs['email']
        sms = subs['sms']
        mobile = subs['mobile_push']
        whatsapp = subs['whatsapp']

        email_subs = self.__parse_subs_email__(emails=emails)
        sms_subs = self.__parse_subs_sms__(sms=sms)
        mobile_subs = self.__parse_subs_mobile__(mobile=mobile)
        bp = 'here'
        parsed_subs = {**email_subs, **sms_subs, **mobile_subs}
        self.logger.info(f'{self.log_prefix}Parsed subscriptions!')
        return parsed_subs



    def __parse_subs_email__(self, emails: dict):
        email_subs = {
            'Mkt_Email_CanReceiveEmail': emails['marketing']['can_receive_email_marketing'],
            'Mkt_Email_Consent': emails['marketing']['consent'],
            'Mkt_Email_ConsentTimestamp': emails['marketing']['consent_timestamp'],
            'Mkt_Email_LastUpdated': emails['marketing']['last_updated'],
            'Mkt_Email_Method': emails['marketing']['method'],
            'Mkt_Email_MethodDetail': emails['marketing']['method_detail'],
            'Mkt_Email_CustomMethodDetail': emails['marketing']['custom_method_detail'],
            'Mkt_Email_DoubleOptin': emails['marketing']['double_optin'],
            'Mkt_Email_Suppression': emails['marketing']['suppression'],
            'Mkt_Email_ListSuppressions': emails['marketing']['list_suppressions'],            
            'OpenTrk_Email_Consent': emails['open_tracking']['consent'],
            'OpenTrk_Email_ConsentTimestamp': emails['open_tracking']['consent_timestamp'],
            'OpenTrk_Email_LastUpdated': emails['open_tracking']['last_updated'],
            'OpenTrk_Email_CreatedTimestamp': emails['open_tracking']['created_timestamp'],
            'OpenTrk_Email_Metadata': emails['open_tracking']['metadata'],
            'OpenTrk_Email_CanReceive': emails['open_tracking']['can_receive'],
            'OpenTrk_Email_ValidUntil': emails['open_tracking']['valid_until'],
            'ClickTrk_Email_Consent': emails['click_tracking']['consent'],
            'ClickTrk_Email_ConsentTimestamp': emails['click_tracking']['consent_timestamp'],
            'ClickTrk_Email_LastUpdated': emails['click_tracking']['last_updated'],
            'ClickTrk_Email_CreatedTimestamp': emails['click_tracking']['created_timestamp'],
            'ClickTrk_Email_Metadata': emails['click_tracking']['metadata'],
            'ClickTrk_Email_CanReceive': emails['click_tracking']['can_receive'],
            'ClickTrk_Email_ValidUntil': emails['click_tracking']['valid_until'],
        }
        return email_subs

    def __parse_subs_sms__(self, sms: dict):        
        sms_subs = {
            'Mkt_SMS_CanReceiveSMS': sms['marketing']['can_receive_sms_marketing'],
            'Mkt_SMS_Consent': sms['marketing']['consent'],
            'Mkt_SMS_ConsentTimestamp': sms['marketing']['consent_timestamp'],
            'Mkt_SMS_Method': sms['marketing']['method'],
            'Mkt_SMS_MethodDetail': sms['marketing']['method_detail'],
            'Mkt_SMS_LastUpdated': sms['marketing']['last_updated'],
            'Txn_SMS_CanReceiveSMS': sms['transactional']['can_receive_sms_transactional'],
            'Txn_SMS_Consent': sms['transactional']['consent'],
            'Txn_SMS_ConsentTimestamp': sms['transactional']['consent_timestamp'],
            'Txn_SMS_Method': sms['transactional']['method'],
            'Txn_SMS_MethodDetail': sms['transactional']['method_detail'],
            'Txn_SMS_LastUpdated': sms['transactional']['last_updated'],
        }
        return sms_subs

    def __parse_subs_mobile__(self, mobile: dict):
        mobile_subs = {
            'Mkt_Push_CanReceivePush': mobile['marketing']['can_receive_push_marketing'],
            'Mkt_Push_Consent': mobile['marketing']['consent'],
            'Mkt_Push_ConsentTimestamp': mobile['marketing']['consent_timestamp'],

        }
        return mobile_subs

        

    def _parse_relationships_(self, profile: dict):
        self.logger.info(f'{self.log_prefix}Parsing relationships...')
        relations = profile['relationships']
        parsed_relations = {

        }
        bp = 'here'

        self.logger.info(f'{self.log_prefix}Parsed relationships!')
        return parsed_relations