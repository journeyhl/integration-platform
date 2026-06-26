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
        for status, data in data_transformed.items():
            self.logger.info(f'{data['OrderCount']} order(s) in {status} status')
            if status in('Risk Hold', 'Open', 'Awaiting Payment', 'On Hold'):
                data = self.__update_ship_sep__(data=data, status=status)
                put_on_hold.append(data)
            elif status == 'On Hold':
                self.__ship_sep_on_hold__(data)
            elif status == '':
                bp = 'here'
            bp = 'here'




    def __update_ship_sep__(self, data: dict, status: str):
        for i, order in enumerate(data['Orders']):
            prefix = f'{i+1}/{data['OrderCount']}: '
            self.logger.info(f'{prefix}{order['OrderNbr']}')
            hold_payload, ship_sep_payload = self.__ship_sep_format_payload__(order=order)
            if status != 'On Hold':
                self.pipeline.acu_api.order_do_action(order_data=order, payload=hold_payload, action='PutOrderOnHold')
            time.sleep(5)
            self.pipeline.acu_api.target_api(endpoint='/SalesOrder?$expand=ShippingSettings', payload_data={'target_api_update_payload': ship_sep_payload}, operation='put', descr='Ship Separately')
            time.sleep(5)
            self.pipeline.acu_api.order_remove_hold(order)
            bp = 'here'
        return data



    def __ship_sep_on_hold__(self, data: dict):
        for i, order in enumerate(data['Orders']):
            prefix = f'{i+1}/{data['OrderCount']}: '
            self.logger.info(f'{prefix}{order['OrderNbr']}')
            bp = 'here'




    def __ship_sep_format_payload__(self, order: dict):

        hold_payload = {
            "entity": {
                "Type": {
                    "value": "SalesOrder"
                },
                "OrderType": {
                    "value": order['OrderType']
                },
                "OrderNbr": {
                    "value": order['OrderNbr']
                }
            }
        }
        ship_sep_payload = {
            "OrderType": 
            {
                "value": order['OrderType']
            },
            "OrderNbr": 
            {
                "value": order['OrderNbr']
            },
            "CustomerID": 
            {
                "value": order['AcctCD']
            },
            'ShippingSettings':{
                "ShipSeparately":{
                    "value": False
                }                
            }

        }
        return hold_payload, ship_sep_payload
