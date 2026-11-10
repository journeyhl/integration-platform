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
        extract_w_profiles = self._get_profiles_(extract=data_extract['contacts'])
        bp = 'here'
    
    def _parse_merged_contacts_(self, merged_contacts: list[dict]):
        self.merged_contacts = {contact['RecordID']: contact['MergedContactIDs'].split(';') for contact in merged_contacts}
        self.reverse_merged_contacts = {merged_contact: contact['RecordID'] for contact in merged_contacts for merged_contact in contact['MergedContactIDs'].split(';')}


        
    def _get_profiles_(self, extract):
        bp = 'here'
        total = len(extract)
        customers = []
        for i, customer in enumerate(extract):
            self.pipeline.hubspot.prefix = f'{i+1}/{total}: ' 
            bp = 'here'
            if not customer['HubspotRecordID']:
                customer['hubspot_profile'] = {}
                continue
            hubspot_profile = self._get_hubspot_profile_(customer=customer)
            klaviyo_profile = self._condense_klaviyo_response_(klaviyo_profile=self.pipeline.klaviyo.get_profiles(filter=f"filter=equals(id,'{customer['ID']}')"))
            customer_record = {
                'hubspot': hubspot_profile,
                'klaviyo': klaviyo_profile,
                'db': customer
            }
            customers.append(customer_record)
        return customers



    def _get_hubspot_profile_(self, customer: dict):
        hubspot_profile = self._condense_hubspot_response_(hubspot_profile=self.pipeline.hubspot.get_contact_by_id(contact_id=customer['HubspotRecordID'], properties=self.pipeline.hubspot.contact_properties_v2))
        if hubspot_profile == {}:
            try1 = self.merged_contacts.get(customer['HubspotRecordID'])
            try2 = self.reverse_merged_contacts.get(customer['HubspotRecordID'])
            filter = [{"filters": [{"propertyName": "email", "operator": "eq", "value": customer['Email']}]}]
            # hubspot_profile = self.pipeline.hubspot.search_contacts(filter_groups=filter, properties=self.pipeline.hubspot.contact_properties_v2.split(','))
            bp = 'here'
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
