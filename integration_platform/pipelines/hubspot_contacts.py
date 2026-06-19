
from typing import Any

from integration_platform.pipelines.base import Pipeline
from integration_platform.connectors import HubSpotAPI



class HubSpotContacts(Pipeline):
    def __init__(self, function: str):
        super().__init__(pipeline_name='hubspot-properties', function=function)
        self.hubapi = HubSpotAPI(self)


    def extract(self):
        properties = [prop['name'] for prop in self.hubapi.get_properties('contacts')]
        data_extract = self.hubapi.search_contacts(properties = properties)
        return data_extract
    
    def transform(self, data_extract):
        property_list = [de['properties'] for de in data_extract]
        prop_usage = {}
        for dict in property_list:
            for key, value in dict.items():
                if value == None:
                    continue
                if prop_usage.get(key):
                    prop_usage[key] += 1
                else:
                    prop_usage[key] = 1

        prop_usage = [{"property": k, "count": v} for k, v in sorted(prop_usage.items(), key=lambda x: x[1], reverse=True)]

        data_transformed = data_extract
        return prop_usage
    
    def load(self, data_transformed):
        data_loaded = data_transformed
        bp = 'here'
        return data_loaded
    
    def log_results(self, data_loaded) -> Any:
        pass