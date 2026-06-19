from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines import RedStagOrderSearch
import logging
class Transform:
    def __init__(self, pipeline: RedStagOrderSearch):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.transform')
        pass
    
    def transform(self, data_extract):
        base_extract = data_extract['base_extract']
        distinct_extract = data_extract['distinct_extract']
        data_transformed = []
        bp = 'here'
        for shipment in distinct_extract:
            shipment_response = self.pipeline.transformer2.transform_lookup_payload(shipment['ShipmentNbr'])
            try:
                response = shipment_response['results'][0]
                if len(response['tracking_numbers']) == 0:
                    self.pipeline.logger.warning(f'{shipment['ShipmentNbr']}: No TrackingNbrs found, skipping...')
                    continue
                shipment['response'] = response
                data_transformed.append(shipment)
                bp = 'here'
            except Exception as e:
                self.logger.error(f'Could not parse RedStag response!')
            bp = 'here'
        data_transformed = self.transform_to_redstagevents(data_transformed)
        # test = self.match_base_to_response(data_transformed, base_extract)
        return data_transformed
    

    def transform_to_redstagevents(self, data_transformed):
        formatted_shipments = []
        for shipment in data_transformed:
            new_shipment = {
                'Topic': 'shipment:packed',
                'ShipmentNbr_3pl': shipment['ShipmentNbr'],
                'Packages': shipment['response']['packages'],
                'Trackers': shipment['response']['packages'],
                'Items': shipment['response']['items'],
                'TrackingNumbers': shipment['response']['tracking_numbers'],
                'msg': shipment['response']
            }
            formatted_shipments.append(new_shipment)
            bp = 'here'
        bp = 'here'
        return formatted_shipments


    def match_base_to_response(self, data_transformed: list, base_extract: list):
        base = [b for b in base_extract if b['ShipmentNbr'] in [d['ShipmentNbr'] for d in data_transformed]]
        for shipment in data_transformed:
            shipment['acu_matches'] = [sh for sh in base if shipment['ShipmentNbr'] == sh['ShipmentNbr']]
            shipment['rs_packages'] = self.parse_packages(shipment)
            shipment['rs_item_summary'] = [item for item in shipment['response']['items']]
            self.match(shipment)
            bp = 'here'

        bp = 'here'
    
    def parse_packages(self, shipment: dict):
        packages = []
        tracking_nbrs = shipment['response']['tracking_numbers']
        for i, package in enumerate(shipment['response']['packages']):
            if len(package['tracking']) == 0: 
                continue
            tracking = package['tracking'][0]['number'] if len(package['tracking']) == 1 else package['tracking'][i]['number'] if i < len(package['tracking']) else package['tracking'][1]['number']
            items = [item for item in package['package_items']]
            item_detail = self.parse_package_items(shipment, package, items, tracking)
            package['item_detail'] = item_detail
            package['manifest_courier'] = package['manifest_courier_code']
            packages.append(package)
            bp = 'here'
        return packages


    def parse_package_items(self, shipment, package, items, tracking):
        item_detail = {}
        for item in items:
            if item_detail.get(item['sku']) == None:
                
                item_detail[item['sku']] = {
                    'InventoryCD': item['sku'],
                    'Qty': item['quantity'],
                    'TrackingNbr': tracking
                }            
            elif item_detail.get(item['sku']) != None:
                item_detail[item['sku']]['Qty'] +=  item['quantity']
        return item_detail
    


    def match(self, shipment):
        for line in shipment['acu_matches']:
            line_match = [ship for ship in shipment['rs_packages'] if ship['InventoryCD'] == line['InventoryCD']]
            bp = 'here'
        bp = 'here'