from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.create_acu_receipt import CreateAcuReceipt
    from integration_platform.pipelines.pack_shipments import PackShipments
    from integration_platform.pipelines.redstag_send_shipments import SendRedStagShipments
    from integration_platform.pipelines.ship_chair_removal_separate import ShipChairRemovalSeparate
import logging
import time





class AcuAPILoader:
    def __init__(self, pipeline: CreateAcuReceipt | PackShipments | SendRedStagShipments | ShipChairRemovalSeparate):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.load')
        pass



    def landing_ship_chair_removal_separate(self, data_transformed: dict):
        bp = 'here'
        put_on_hold = []
        on_hold = []
        orders = [order for status, data in data_transformed.items() for order in data['Orders']]
        self.logger.info(f'{len(orders)} total orders across {len(data_transformed.keys())} different statuses')
        for status, data in data_transformed.items():
            self.logger.info(f'{data['OrderCount']} order(s) in {status} status')
            if status in('Risk Hold', 'Open', 'Awaiting Payment', 'On Hold'):
                data = self.__update_ship_sep_or_wh__(data=data, status=status)
                put_on_hold.append(data)
                
                bp = 'here'
            bp = 'here'




    def __update_ship_sep_or_wh__(self, data: dict, status: str):
        for i, order in enumerate(data['Orders']):
            prefix = f'{i+1}/{data['OrderCount']} {status} orders: '
            self.logger.info(f'{prefix}{order['OrderNbr']}')
            if status != 'On Hold':
                hold_payload = self.pipeline.acu_api.helper.format_put_on_hold(order=order)
                self.pipeline.acu_api.order_do_action(order_data=order, payload=hold_payload, action='PutOrderOnHold')
            time.sleep(5)
            if order['ChairRemovalWH'] != order['OrderLineWH']:
                self.logger.warning(f'Warehouse mismatch! {order['InventoryCD']}: {order['OrderLineWH']}, Chair Removal: {order['ChairRemovalWH']}')
                order['acu_response'] = self.pipeline.acu_api.get_order_details(order_data=order, additional_details='?$expand=Details')
                order['acu_details'] = order['acu_response']['Details']
                update_wh_payload = self.pipeline.acu_api.helper.format_soline_wh_update(order=order)
                response = self.pipeline.acu_api.target_api(endpoint='/SalesOrder', payload_data={'target_api_update_payload': update_wh_payload}, operation='put', descr='Update Warehouse')
                status = response['Status']['value'] if isinstance(response, dict) else status
            if order['ShipSeparately']:
                ship_sep_payload = self.pipeline.acu_api.helper.format_ship_separately(order=order)
                self.pipeline.acu_api.target_api(endpoint='/SalesOrder?$expand=ShippingSettings', payload_data={'target_api_update_payload': ship_sep_payload}, operation='put', descr='Ship Separately')
            time.sleep(5)
            self.pipeline.acu_api.order_remove_hold(order)
            bp = 'here'
        return data





