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
                data = self.__update_ship_sep_or_wh__(data=data, status=status)
                put_on_hold.append(data)
                
                bp = 'here'
            bp = 'here'




    def __update_ship_sep_or_wh__(self, data: dict, status: str):
        for i, order in enumerate(data['Orders']):
            prefix = f'{i+1}/{data['OrderCount']}: '
            self.logger.info(f'{prefix}{order['OrderNbr']}')
            if order['ChairRemovalWH'] != order['OrderLineWH']:
                order['acu_response'] = self.pipeline.acu_api.get_order_details(order_data=order, additional_details='?$expand=Details')
                order['acu_details'] = order['acu_response']['Details']
                update_wh_payload = self.__update_wh_payload__(order=order)
                response = self.pipeline.acu_api.target_api(endpoint='/SalesOrder', payload_data={'target_api_update_payload': update_wh_payload}, operation='put', descr='Update Warehouse')
                bp = 'here'
            bp = 'here'
            if status != 'On Hold':
                self.pipeline.acu_api.order_do_action(order_data=order, payload=hold_payload, action='PutOrderOnHold')
            time.sleep(5)
            if order['ShipSeparately']:
                hold_payload, ship_sep_payload = self.__ship_sep_format_payload__(order=order)
                self.pipeline.acu_api.target_api(endpoint='/SalesOrder?$expand=ShippingSettings', payload_data={'target_api_update_payload': ship_sep_payload}, operation='put', descr='Ship Separately')


            
            time.sleep(5)
            self.pipeline.acu_api.order_remove_hold(order)
            bp = 'here'
        return data



    def __update_wh_payload__(self, order):
        lines = order['acu_details']
        chair = [line for line in lines if line['InventoryID']['value'] != '27222'][0] or {}
        chair_removal = [line for line in lines if line['InventoryID']['value'] == '27222'][0] or {}
        if chair == {} or chair_removal == {}:
            self.logger.error(f'{'Chair not found! ' if chair == {} else ''}{'Chair Removal not found!' if chair_removal == {} else ''}')
            return {}
        update_wh_payload = {
            "CustomerID": {
                "value": order['AcctCD']
            },
            "OrderType": {
                "value": order['OrderType']
            },
            "OrderNbr": {
                "value": order['OrderNbr']
            },
            "Details": [
                {
                    "id": chair_removal['id'],
                    "WarehouseID": {
                        "value": order['OrderLineWH']
                    },
                    # 'UOM': {
                    #     "value": "EA"
                    # },
                    # "IsSpecialOrder": {
                    #     "value": False
                    # },
                    # "SalesAcctID":{
                    #     "value": chair['Account']['value']
                    # }
                }
            ]      
        }
        return update_wh_payload


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
