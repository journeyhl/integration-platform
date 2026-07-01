from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.address_validator import AddressValidator
import logging
import time
import polars as pl

class Load:
    '''Load
    ===
    <hr>    

    Class for smart handling of Acumatica API interactions 
    
    '''
    def __init__(self, pipeline: AddressValidator):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.load')

    def landing(self, data_transformed: list):
        for order_avs in data_transformed:
            if order_avs.get('update_order_address_payload') == None:
                self.logger.warning(f'{order_avs['OrderNbr']}: No response from AVS, skipping...')
                continue
            self.logger.info(f'{order_avs['OrderNbr']}: Beginning target run')
            light_payload = {
                'key': f'{order_avs['OrderNbr']}',
                'target_api_update_payload': order_avs['update_order_address_payload'],
                'log_error': f"Issue overriding & updating {order_avs['OrderNbr']}'s addresses!",
                'log_success': f"{order_avs['OrderNbr']}'s addresses were overriden & updated successfully!",
                'log_validation_error': f"Issue validating {order_avs['OrderNbr']}'s addresses",
                'log_validation_success': f"{order_avs['OrderNbr']}'s addresses were validated successfully!",
                'acu_api_data_log': order_avs['acu_api_log_update_override'],
            }
            order_avs['validate_address'] = self.pipeline.acu_api.target_api(endpoint='/SalesOrder', payload_data=light_payload, operation='put', descr='Override & Update')
            bp = 'here'
            # order_avs['validate_address'] = self.pipeline.acu_api.update_customer_address(order_avs['update_address_payload'])
            if order_avs['validate_address']:
                self.validate_remove_hold_create(order_avs)
                bp = 'here'


    def validate_remove_hold_create(self, order_avs):
        iterations = 0
        order_avs = self.pipeline.acu_api.get_order_details(order_avs)
        bp = 'here'
        while (order_avs['ShippingValidated'] != True or order_avs['BillingValidated'] != True) and iterations < 5:
            self.pipeline.acu_api.validate_order_address(order_avs)
            time.sleep(1)
            order_avs = self.pipeline.acu_api.get_order_details(order_avs)
            time.sleep(1)
            iterations += 1
        if iterations == 5:
            self.logger.warning(f"Couldn't validate address for {order_avs['OrderNbr']}")
            bp = 'here'
        else:
            self.pipeline.acu_api.order_remove_hold(order_avs)
            time.sleep(1)
            self.pipeline.acu_api.order_create_shipment(order_avs)
            bp = 'here'
        bp = 'here'
        
        