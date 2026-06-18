from integration_platform.pipelines import Pipeline
from integration_platform.connectors import HubSpotAPI
import polars as pl


class HubspotPropertyUpdate(Pipeline):
    def __init__(self, function: str, env: str='prod'):
        # function = 'hubspot_property_update'
        super().__init__(pipeline_name='hubspot-property-update', function=function, env=env)
        self.hubspot = HubSpotAPI(self)

    def extract(self):
        property_extract = self.hubspot.get_properties(object_type='contacts', property_name='acumatica_product_list')
        acu_item_extract = self.acudb.query_db('select distinct Descr label from InventoryItem i where i.CompanyID = 2')
        data_extract = {
            'property_extract': property_extract[0],
            'acu_item_extract': acu_item_extract
        }
        return data_extract

    def transform(self, data_extract):
        property = data_extract['property_extract']
        proptions = property['options']
        df_proptions = pl.DataFrame(proptions)
        option_count = df_proptions.height
        acu_items: pl.DataFrame = data_extract['acu_item_extract']
        new_options = acu_items.join(df_proptions, on='label', how='anti').to_dicts()
        self.logger.info(f'Current stats:\nHubspot options: {option_count} options\nAcu items: {acu_items.height}\nItems to add: {len(new_options)}')
        for i, item in enumerate(new_options):
            option = {
                'label': item['label'],
                'value': item['label'],
                'description': '',
                'displayOrder': option_count + i,
                'hidden': False
            }
            property['options'].append(option)
        self.logger.info(f'{property['name']} now has {option_count + len(new_options)} options')
        return property
    
    def load(self, transformed_property):
        self.hubspot.update_property_options(property=transformed_property)
        return transformed_property
    
    def log_results(self, data_loaded):
        pass