from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.redstag_send_shipments import SendRedStagShipments
import logging
import time

class Load:
    '''Load
    ===
    <hr>

    Class for smart handling of Acumatica API interactions 
    
    '''
    def __init__(self, pipeline: SendRedStagShipments):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.Load')

    def send_shipments(self, data_transformed):
        '''`send_shipments`(self, data_transformed)
        ---
        <hr>

        Once we have the order_id (*rsOrderID*) from RedStag, we can mark the shipment as Sent to WH.


        Parameters
        ===
        <hr>

        :param **data_transformed**: Transformed dictionary of RedStag Shipments to send
        :type **data_transformed**: _dict_
        '''
        data_transformed_copy = data_transformed
        data_loaded = []
        total = len(data_transformed)
        self.logger.info(f'Now sending {total} shipments...')
        for i, (shipment, data) in enumerate(data_transformed.items()):
            self.log_prefix = f'{shipment}, {i+1}/{total}: '
            self.logger.info(f'{self.log_prefix}Sending execution payload for {shipment} to RedStag')
            self.create_response = self.pipeline.redstag.target_api(payload_target=data['execution_payload'], operation=data['execution_operation'], log_prefix=self.log_prefix)
            if self.create_response.get('results'):
                self.create_response = self.create_response['results'][0]
            elif self.create_response.get('error'):
                self.logger.error(f'{self.log_prefix}Error {self.create_response['error']['code']}! {self.create_response['error']['message']}')
                self.logger.warning(f'{self.log_prefix}Skipping {shipment}...')
                continue
            if i % 10 == 0 and i != 0:
                self.logger.info(f'{self.log_prefix}Sleeping 3 seconds...')
                time.sleep(3)
            if self.create_response['status'] == 'unable_to_process':
                self.logger.warning(f'{self.create_response['status']} {shipment}!')                
            if self.create_response['status'] == 'new' or self.create_response['status'] == 'unable_to_process':
                self.logger.info(f'{self.log_prefix}Shipment {shipment} created at RedStag successfully!')
            if data['note'] == 'Already at RedStag':
                self.logger.info(f'{self.log_prefix}Shipment had already been sent to RedStag, marking SentToWH as true in Acumatica')
            
            data['data_3pl'] = self.create_response
            data['attribute_payload'] = self.pipeline.transformer.transform_acu_attribute_payload(data, log_prefix=self.log_prefix)
            self.pipeline.acu_api.send_to_wh_v2(ShipmentNbr=shipment, CustomerID=data['CustomerID'], attribute_payload=data['attribute_payload'], log_prefix=self.log_prefix)
            bp = 'here'

        data_loaded = data_transformed
        return data_loaded