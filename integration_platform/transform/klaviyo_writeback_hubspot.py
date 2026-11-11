from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.klaviyo_writeback_hubspot import KlaviyoWritebackHubspot
import logging
import polars as pl
class Transform:
    def __init__(self, pipeline: KlaviyoWritebackHubspot):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.Transform')
        pass

    def landing(self, data_extract):
        self._parse_merged_contacts_(merged_contacts=data_extract['merged_contacts'])
        contact_profiles = self._get_profiles_(extract=data_extract['contacts'])
        self.pipeline.comparer.landing(contact_profiles=contact_profiles)
        bp = 'here'



    
    def _parse_merged_contacts_(self, merged_contacts: list[dict]):
        self.merged_contacts = {contact['RecordID']: contact['MergedContactIDs'].split(';') for contact in merged_contacts}
        self.reverse_merged_contacts = {merged_contact: contact['RecordID'] for contact in merged_contacts for merged_contact in contact['MergedContactIDs'].split(';')}


        
    def _get_profiles_(self, extract):
        ''':class:`~integration_platform.transform.klaviyo_writeback_hubspot.Transform`.:meth:`~integration_platform.transform.klaviyo_writeback_hubspot.Transform._get_profiles_`
        ---
        
        Gets Klaviyo and HubSpot profiles for each contact in `extract`
        
        Parameters
        ---
        :param (*_type_*) `extract`: _description_
        
                
           ### ***Optional***
        :param (*str = ''*) `log_prefix`: String to prepend to any logger outputs. Usually used when iterating, like `'keyvalue1, 1/150: '`, `'keyvalue2, 2/150: '` and so on 
        
        Returns
        ---
        :return `variablename` (_type_): _description_
        
        <hr>
        
        Sets
        ---
        - #### ____replace_with_class_level_variable_pls____
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### _______replace_me_______
        
          - Description
        
         ### _______replace_me_______
           
          - Description
        
        ## Downstream Calls (Methods/Functions called)
        
         ### :class:`~integration_platform.transform.klaviyo_writeback_hubspot.Transform`.:meth:`~integration_platform.transform.klaviyo_writeback_hubspot.Transform._get_hubspot_profile_`
        
          - Called for each contact, retrieves hubspot profile (if found), then trims to only the data we need
        
         ### :class:`~integration_platform.connectors.klaviyo.KlaviyoAPI`.:meth:`~integration_platform.connectors.klaviyo.KlaviyoAPI.get_profiles`
           
          - Called for each contact, retrieves klaviyo profile
         
         ### :class:`~integration_platform.transform.klaviyo_writeback_hubspot.Transform`.:meth:`~integration_platform.transform.klaviyo_writeback_hubspot.Transform._condense_klaviyo_response_`
           
          - After retrieving a klaviyo profile, trim it down to only what we need
        '''        
        bp = 'here'
        total = len(extract)
        contacts = []
        for i, contact in enumerate(extract):
            self.pipeline.hubspot.prefix = f'{i+1}/{total}: ' 
            bp = 'here'
            hubspot_profile = self._get_hubspot_profile_(contact=contact)
            klaviyo_profile = self._condense_klaviyo_response_(klaviyo_profile=self.pipeline.klaviyo.get_profiles(filter=f"filter=equals(id,'{contact['ID']}')"))
            contact_record = {
                'hubspot': hubspot_profile,
                'klaviyo': klaviyo_profile,
                'db': contact
            }
            contacts.append(contact_record)
        return contacts



    def _get_hubspot_profile_(self, contact: dict):
        if not contact['HubspotRecordID']:
            filter = [{"filters": [{"propertyName": "email", "operator": "eq", "value": contact['Email']}]}]
            profile = self.pipeline.hubspot.search_contacts(filter_groups=filter, properties=self.pipeline.hubspot.contact_properties_v2.split(','))
            bp = 'here'
        else:
            profile = self.pipeline.hubspot.get_object_by_id(object_id=contact['HubspotRecordID'],object_type='contact', props=self.pipeline.hubspot.contact_properties_v2)
            hubspot_profile = self._condense_hubspot_response_(hubspot_profile=profile)
        if profile in [[], {}]:
            if contact['RawPhoneNumber']:
                filter = [{"filters": [{"propertyName": "phone", "operator": "eq", "value": contact['Email']}]}]
                hubspot_profile = self.pipeline.hubspot.search_by_phone(phone_value=contact['RawPhoneNumber'], properties=self.pipeline.hubspot.contact_properties_v2.split(','))
            else:
                hubspot_profile = {}
        hubspot_profile = {} if profile == [] else hubspot_profile
        return hubspot_profile


    def _condense_hubspot_response_(self, hubspot_profile):
        if hubspot_profile == {}:
            return {}
        hubspot_profile = {
            'id': hubspot_profile['id'],
            'createdAt': hubspot_profile['createdAt'],
            'updatedAt': hubspot_profile['updatedAt'],
            'url': hubspot_profile['url'],
            **hubspot_profile['properties'],   
        }
        return hubspot_profile

    def _condense_klaviyo_response_(self, klaviyo_profile):
        def get_rid_of_dicts(parent: dict):
            trimmed_parent = {k: v for k, v in parent.items() if not isinstance(v, dict)}
            return trimmed_parent
        if klaviyo_profile == []:
            return {}
        klaviyo_profile = klaviyo_profile[0]
        profile = {
            'id': klaviyo_profile['id'],
            'attributes': get_rid_of_dicts(parent=klaviyo_profile['attributes']),
            'location': get_rid_of_dicts(parent=klaviyo_profile['attributes']['location']),
            'properties': get_rid_of_dicts(parent=klaviyo_profile['attributes']['properties']),
            'subscriptions': klaviyo_profile['attributes']['subscriptions']
        }
        return profile
