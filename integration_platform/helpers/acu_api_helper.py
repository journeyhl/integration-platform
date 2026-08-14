
from __future__ import annotations
from typing import TYPE_CHECKING, Literal
if TYPE_CHECKING:
    from integration_platform.connectors.acu_api import AcumaticaAPI
import logging
import requests
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import polars as pl

class AcumaticaAPIHelper:
    def __init__(self, acu_api: AcumaticaAPI) -> None:
        self.acu = acu_api
        if type(acu_api.pipeline) == str:
            self.logger = logging.getLogger(f'{acu_api.pipeline}.AcumaticaAPIHelper')
        else:
            self.logger = logging.getLogger(f'{acu_api.pipeline.pipeline_name}.AcumaticaAPIHelper')
        
        pass
    
    #region format_data_log_entry
    def format_data_log_entry(self, entity: str, key_value: str, operation: str, payload: dict, response: str, tstamp: datetime, options: Literal['append', 'return']):
        self.acu.calls += 1
        entry = {            
            'Entity': entity,
            'KeyValue': key_value,
            'Operation': operation,
            'Payload': payload,
            'Response': response,
            'Timestamp': tstamp,
        }
        if options == 'append':
            self.acu.data_log.append(entry)
            return
        elif options == 'return':
            return entry
        else:
            self.acu.data_log.append(entry)
            return entry
    #endregion

    #region format_manage_sales_allocations
    def format_manage_sales_allocations(self, order_data: dict) -> dict:
        ''':class:`~AcumaticaAPIHelper`.:meth:`~format_manage_sales_allocations` (self, order_data: *dict*):
        ---
        <hr>
        
        Formats payload to pass to :class:`~integration_platform.connectors.acu_api.AcumaticaAPI`.:meth:`~integration_platform.connectors.acu_api.AcumaticaAPI.target_api` for managing sales allocations
        
        ### Upstream Calls 
         #### :class:`~integration_platform.connectors.acu_api.AcumaticaAPI`.:meth:`~integration_platform.connectors.acu_api.AcumaticaAPI.manage_sales_allocations`
            
        <hr>
        
        Parameters
        ---
        :param (*dict*) `order_data`: dictionary of order data. Must contain ***`SiteCD`***, ***`OrderType`***, ***`OrderNbr`***, and ***`param_Action`***
        
        <hr>
        
        Returns
        ---
        :return `full_payload` (dict): payload to be sent to :class:`~integration_platform.connectors.acu_api.AcumaticaAPI`.:meth:`~integration_platform.connectors.acu_api.AcumaticaAPI.target_api`
        '''
        order_nbr = order_data['OrderNbr']
        end_date = datetime.now().strftime('%m/%d/%Y')
        payload = {
            "entity": {
                "Warehouse":{
                    "value": order_data['SiteCD']
                },
                "EndDate":{
                    "value": end_date
                },
                "OrderType":{
                    "value": order_data['OrderType']
                },
                "OrderNbr":{
                    "value": order_data['OrderNbr']
                }
            },
            "parameters": {
                "param_Action": {
                    "value": order_data['param_Action']
                },
                "param_SelectBy":{
                    "value": "Line Ship On"
                },
                "param_Warehouse":{
                    "value": order_data['SiteCD']
                },
                "param_EndDate":{
                    "value": end_date
                },
                "param_OrderType":{
                    "value": order_data['OrderType']
                },
                "param_OrderNbr":{
                    "value": order_data['OrderNbr']
                }
            }            
        }
        acu_data_log_entry = {            
            'Entity': 'ManageSalesAllocations',
            'KeyValue': order_nbr,
            'Operation': f'POST - {order_data['param_Action']}',
            'Payload': payload,
        }
        short_action = f'{order_data['param_Action'].split(' ')[0]}'
        success_str = f'{order_nbr} {short_action}d!'
        error_str = f'Could not {short_action} {order_nbr}!'
        full_payload = {
            'target_api_update_payload': payload,
            'log_success': success_str,
            'log_error': error_str,
            'acu_api_data_log': acu_data_log_entry,
        }
        return full_payload
    #endregion

    #region format_reclassify_transaction
    def format_reclassify_transaction(self, cogs_entry: dict) -> dict:
        ''':class:`~AcumaticaAPIHelper`.:meth:`~format_reclassify_transaction` (self, cogs_entry: *dict*):
        ---
        <hr>
        
        Formats payload to pass to :class:`~integration_platform.connectors.acu_api.AcumaticaAPI`.:meth:`~integration_platform.connectors.acu_api.AcumaticaAPI.target_api` for reclassifying a transaction
        
        ### Upstream Calls 
         #### :class:`~integration_platform.connectors.acu_api.AcumaticaAPI`.:meth:`~integration_platform.connectors.acu_api.AcumaticaAPI.reclassify_transaction`
            
        <hr>
        
        Parameters
        ---
        :param (*dict*) `cogs_entry`: dict of data regarding Cost of Good Sold entry. Must contain ***`BatchNbr`*** and ***`Module`***
        
        <hr>
        
        Returns
        ---
        :return `full_payload` (dict): payload to be sent to :class:`~integration_platform.connectors.acu_api.AcumaticaAPI`.:meth:`~integration_platform.connectors.acu_api.AcumaticaAPI.target_api`
        '''
        batch_nbr = cogs_entry['BatchNbr']
        payload = {
            "entity": {
                "BatchNbr": {
                    "value": batch_nbr
                },
                "Module": {
                    "value": cogs_entry['Module']
                },
                "parameters": {
                    "NewAccountID": {
                        "value": "5090"
                    }
                }
            }
        }        
        acu_data_log_entry = {            
            'Entity': 'JournalTransaction',
            'KeyValue': batch_nbr,
            'Operation': f'POST - Reclassify Journal Transaction',
            'Payload': payload,
        }
        success_str = f'{batch_nbr} reclassified to 5090 successfully!'
        error_str = f'Could not reclassify {batch_nbr}!'
        full_payload = {
            'target_api_update_payload': payload,
            'log_success': success_str,
            'log_error': error_str,
            'acu_api_data_log': acu_data_log_entry,
        }
        return full_payload
    #endregion

    #region format_prepare_shopify
    def format_prepare_shopify(self, entity: str = 'Product Availability') -> dict:     
        ''':class:`~AcumaticaAPIHelper`.:meth:`~format_prepare_shopify` (self, entity: *str = 'Product Availability'*):
        ---
        <hr>
        
        Formats payload to pass to :class:`~integration_platform.connectors.acu_api.AcumaticaAPI`.:meth:`~integration_platform.connectors.acu_api.AcumaticaAPI.target_api` when ***preparing*** shopify sync records for a given Entity
        
        ### Upstream Calls 
         #### :class:`~integration_platform.connectors.acu_api.AcumaticaAPI`.:meth:`~integration_platform.connectors.acu_api.AcumaticaAPI.prepare_shopify`
            
        <hr>
        
        Parameters
        ---
        :param (*str*) `entity`: Entity to prepare. Defaults to *`Product Availability`*
        
        <hr>
        
        Returns
        ---
        :return `full_payload` (dict): payload to be sent to :class:`~integration_platform.connectors.acu_api.AcumaticaAPI`.:meth:`~integration_platform.connectors.acu_api.AcumaticaAPI.target_api`
        '''           
        payload = {
            "entity": {
                "Store":{
                    "value": "ShopJourneyProductio"
                },
                "EntityName":{
                    "value": entity
                },
                "Selected":{
                    "value": True
                }
            },
            "parameters": {
                "param_Store": {
                    "value": "ShopJourneyProductio"
                },
                "param_Entity":{
                    "value": entity
                },
                "param_PrepareMode":{
                    "value": "Incremental"
                }
            }
        }
        acu_data_log_entry = {            
            'Entity': 'PrepareShopify',
            'KeyValue': entity,
            'Operation': f'POST - Prepare {entity}',
            'Payload': payload,
        }
        success_str = f'{entity} prepared successfully!'
        error_str = f'Could not prepare {entity}!'
        full_payload = {
            'target_api_update_payload': payload,
            'log_success': success_str,
            'log_error': error_str,
            'acu_api_data_log': acu_data_log_entry,
        }
        return full_payload
    #endregion

    #region format_process_shopify
    def format_process_shopify(self, entity_data: dict, entity: str = 'Product Availability') -> dict:
        ''':class:`~AcumaticaAPIHelper`.:meth:`~format_process_shopify` (entity_data: *dict*, entity: *str = 'Product Availability'*):
        ---
        <hr>
        
        Formats payload to pass to :class:`~integration_platform.connectors.acu_api.AcumaticaAPI`.:meth:`~integration_platform.connectors.acu_api.AcumaticaAPI.target_api` when ***processing*** shopify sync records for a given Entity

        ### Upstream Calls 
         #### :class:`~integration_platform.connectors.acu_api.AcumaticaAPI`.:meth:`~integration_platform.connectors.acu_api.AcumaticaAPI.process_shopify`
            
        <hr>
        
        Parameters
        ---
        :param (*dict*) `entity_data`: dictionary of data for Entity. Must contain ***`SyncID`***
        :param (*str*) `entity`: Entity to prepare. Defaults to *`Product Availability`*
        
        <hr>
        
        Returns
        ---
        :return `full_payload` (dict): payload to be sent to :class:`~integration_platform.connectors.acu_api.AcumaticaAPI`.:meth:`~integration_platform.connectors.acu_api.AcumaticaAPI.target_api`
        '''        
        sync_id = entity_data['SyncID']
        payload = {
            "entity": {
                "Store":{
                    "value": "ShopJourneyProductio"
                },
                "EntityName":{
                    "value": entity
                },
                "Selected":{
                    "value": True
                }
            },
            "parameters": {
                "param_Store": {
                    "value": "ShopJourneyProductio"
                },
                "param_Entity":{
                    "value": entity
                },
                "param_SyncID":{
                    "value": sync_id
                }
            }
        }
        acu_data_log_entry = {            
            'Entity': 'ProcessShopify',
            'KeyValue': f'{entity}, SyncID: {sync_id}',
            'Operation': f'POST - Process {entity}',
            'Payload': payload,
        }
        success_str = f'{entity} processed successfully!'
        error_str = f'Could not process {entity}!'
        full_payload = {
            'target_api_update_payload': payload,
            'log_success': success_str,
            'log_error': error_str,
            'acu_api_data_log': acu_data_log_entry,
        }
        return full_payload
    #endregion


    #region format_put_on_hold
    def format_put_on_hold(self, order: dict) -> dict:
        ''':class:`~AcumaticaAPIHelper`.:meth:`~format_put_on_hold` (self, order: *dict*):
        ---
        <hr>
        
        Given a dict of order data, formats payload to be sent to Acumatica API in order to place the specified order on hold

        ### Upstream Calls 
         #### :class:`~integration_platform.load.acu_api_loader.AcuAPILoader`.:meth:`~integration_platform.load.acu_api_loader.AcuAPILoader.__update_ship_sep_or_wh__`
            - If an order's status doesn't equal On Hold, then this method is called to format payload to send to Acu api so that we may put it on hold
            
        <hr>
        
        Parameters
        ---
        :param (*dict*) `order`: dict of order data. Must contain ***`OrderType`*** and ***`OrderNbr`***
        
        <hr>
        
        Returns
        ---
        :return `hold_payload` (dict): payload to be sent to Acumatica API
        '''
        self.logger.info(f'Placing {order['OrderNbr']} On Hold!')
        hold_payload = self._format_sales_order_entity_payload_(order=order)
        return hold_payload
    #endregion
    
    #region format_order_remove_hold
    def format_order_remove_hold(self, order: dict) -> dict:
        ''':class:`~AcumaticaAPIHelper`.:meth:`~format_order_remove_hold` (self, order: *dict*, ):
        ---
        <hr>
        
        Given a dict of order data, pass it to :class:`~integration_platform.helpers.acu_api_helper.AcumaticaAPIHelper`.:meth:`~integration_platform.helpers.acu_api_helper.AcumaticaAPIHelper._format_sales_order_entity_payload_` to format standard Sales Order entity payload
        
        ### Downstream Calls 
         #### :class:`~integration_platform.helpers.acu_api_helper.AcumaticaAPIHelper`.:meth:`~integration_platform.helpers.acu_api_helper.AcumaticaAPIHelper._format_sales_order_entity_payload_`
        
        ### Upstream Calls 
         #### :class:`~integration_platform.connectors.acu_api.AcumaticaAPI`.:meth:`~integration_platform.connectors.acu_api.AcumaticaAPI.order_remove_hold`
            
        <hr>
        
        Parameters
        ---
        :param (*dict*) `order`: dict of order data. Must contain ***`OrderType`*** and ***`OrderNbr`***
        
        <hr>
        
        Returns
        ---
        :return `payload` (dict): payload to send to remove order from hold
        '''
        payload = self._format_sales_order_entity_payload_(order)
        return payload
    #endregion

    #region format_soline_wh_update
    def format_soline_wh_update(self, order: dict):
        ''':class:`~AcumaticaAPIHelper`.:meth:`~format_soline_wh_update` (self, order: *dict*):
        ---
        <hr>
        
        Given a dict of order data, formats payload to be sent to Acumatica API to update the warehouse on a given order line
        
        ### Upstream Calls 
         #### :class:`~integration_platform.load.acu_api_loader.AcuAPILoader`.:meth:`~integration_platform.load.acu_api_loader.AcuAPILoader.__update_ship_sep_or_wh__`
            - If the warehouse of the Sleepchair doesn't equal the warehouse of the Chair Removal, this method is called so that we can change the Chair Removal line's warehouse to that of the PSChair.
            
        <hr>
        
        Parameters
        ---
        :param (*dict*) `order`: dict of order data. Must contain ***`acu_details`***, ***`OrderType`*** and ***`OrderNbr`***
        
        <hr>
        
        Returns
        ---
        :return `update_soline_wh_payload` (dict): payload to be sent to Acumatica api to update the warehouse on a given order line
        :return `dl_entry` (dict): data log entry. The "pre-response" data_log entry. Once we hit the api, we add the response details, then the dict is loaded to central store for logging
        '''
        self.logger.info(f"Updating Chair Removal's warehouse to {order['OrderLineWH']}")
        lines = order['acu_soline_response']
        chair = [line for line in lines if line['InventoryID']['value'] != '27222'][0] or {}
        chair_removal = [line for line in lines if line['InventoryID']['value'] == '27222'][0] or {}
        if chair == {} or chair_removal == {}:
            self.logger.error(f'{'Chair not found! ' if chair == {} else ''}{'Chair Removal not found!' if chair_removal == {} else ''}')
            return {}
        update_soline_wh_payload = {
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
                }
            ]      
        }
        dl_entry = self._format_pre_response_data_log_entry_(entity='SalesOrder', key_value=order['OrderNbr'], operation=f"PUT - Update SOLine Warehouse", payload=update_soline_wh_payload)
        return update_soline_wh_payload, dl_entry
    #endregion

    #region format_ship_separately
    def format_ship_separately(self, order: dict):
        ''':class:`~AcumaticaAPIHelper`.:meth:`~format_ship_separately` (self, order: *dict*):
        ---
        <hr>
        
        Given a dict of order data, formats payload to be sent to Acumatica API to update the Ship Separately value to ***`False`*** on the given order
        
        ### Upstream Calls 
         #### :class:`~integration_platform.load.acu_api_loader.AcuAPILoader`.:meth:`~integration_platform.load.acu_api_loader.AcuAPILoader.__update_ship_sep_or_wh__`
            - If ShipSeparately equals True, then this method is called so we can change value to False
            
        <hr>
        
        Parameters
        ---
        :param (*dict*) `order`: dict of order data. Must contain `***OrderType***` and `***OrderNbr***`
        
        <hr>
        
        Returns
        ---
        :return `ship_sep_payload` (dict): Formatted payload to send to ACumatica API
        :return `dl_entry` (dict): data log entry. The "pre-response" data_log entry. Once we hit the api, we add the response details, then the dict is loaded to central store for logging
        '''
        self.logger.info(f"Updating ShipSeparately to False!")
        ship_sep_payload = {
            "OrderType": 
            {
                "value": order['OrderType']
            },
            "OrderNbr": 
            {
                "value": order['OrderNbr']
            },
            # "": 
            # {
            #     "value": order['AcctCD']
            # },
            'ShippingSettings':{
                "ShipSeparately":{
                    "value": False
                }                
            }
        }
        dl_entry = self._format_pre_response_data_log_entry_(entity='SalesOrder', key_value=order['OrderNbr'], operation=f"PUT - Updating {order['OrderNbr']}'s Ship Separately value to False", payload=ship_sep_payload)
        return ship_sep_payload, dl_entry
    #endregion

    def _format_pre_response_data_log_entry_(self, entity: str, key_value: str, operation: str, payload: dict = {}):
        data_log_entry = {
            'Entity': entity,
            'KeyValue': key_value,
            'Operation': operation,
            'Payload': payload
        }
        return data_log_entry
    #region format_order_create_receipt
    def format_order_create_receipt(self, order: dict) -> dict:
        ''':class:`~AcumaticaAPIHelper`.:meth:`~format_order_create_receipt` (self, order: *dict*):
        ---
        <hr>
        
        Given a dict of order data, formats payload to be sent to Acumatica API to create a receipt for the given order
        
        ### Upstream Calls 
         #### :class:`~integration_platform.connectors.acu_api.AcumaticaAPI`.:meth:`~integration_platform.connectors.acu_api.AcumaticaAPI.order_create_receipt`
            
        <hr>
        
        Parameters
        ---
        :param (*dict*) `order`: dict of order data. Must contain `***OrderType***`, `***OrderNbr***`, and `***AcctCD***`
        
        <hr>
        
        Returns
        ---
        :return `create_receipt_payload` (dict): payload to send to acu api to create receipt for a given order
        '''
        create_receipt_payload = {
            "entity":{
                "CustomerID": { "value": f"{order['AcctCD']}" },
                "OrderType": {"value": f"{order['OrderType']}"},
                "OrderNbr": { "value": f"{order['OrderNbr']}"}
            }
        }
        return create_receipt_payload
    #endregion

    #region format_order_create_shipment
    def format_order_create_shipment(self, order: dict) -> dict:
        ''':class:`~AcumaticaAPIHelper`.:meth:`~format_order_create_shipment` (self, order: *dict*):
        ---
        <hr>
        
        Given a dict of order data, formats payload to be sent to Acumatica API to create a ***shipment*** for the given order
        
        ### Upstream Calls 
         #### :class:`~integration_platform.connectors.acu_api.AcumaticaAPI`.:meth:`~integration_platform.connectors.acu_api.AcumaticaAPI.order_create_receipt`
            
        <hr>
        
        Parameters
        ---
        :param (*dict*) `order`: dict of order data. Must contain `***OrderType***`, `***OrderNbr***`, and `***AcctCD***`
        
        <hr>
        
        Returns
        ---
        :return `create_shipment_payload` (dict): payload to send to acu api to create ***shipment*** for a given order
        '''
        create_shipment_payload = {
            "entity":{
                "CustomerID": {"value": f"{order['AcctCD']}" },
                "OrderType": {"value": f"{order['OrderType']}"},
                "OrderNbr": {"value": f"{order['OrderNbr']}"}
            }
        }
        if order.get('properties'):
            create_shipment_payload['properties'] = {
                "ShipmentDate": {"value": f'{datetime.now(ZoneInfo('America/New_York'))}'}, 
                "WarehouseID": {"value": order['properties']['WarehouseID']}, 
            }
        return create_shipment_payload
    #endregion

    #region format_rc_send_to_wh
    def format_rc_send_to_wh(self, order: dict) -> dict:
        ''':class:`~AcumaticaAPIHelper`.:meth:`~format_rc_send_to_wh` (self, order: *dict*):
        ---
        <hr>
        
        put_summary_here
        
        ### Downstream Calls 
         #### :class:`~class`.:meth:`~method`
            - Description
         #### :class:`~folder.file.class`.:meth:`~folder.file.class.method`
            - Description
        
        ### Upstream Calls 
         #### :class:`~class`.:meth:`~method`
            - Description
         #### :class:`~folder.file.class`.:meth:`~folder.file.class.method`
            - Description
            
        <hr>
        
        Parameters
        ---
        :param (*dict*) `order`: dict of order data. Must contain `***OrderType***`, `***OrderNbr***`, and `***CustomerID***`
        
        <hr>
        
        Returns
        ---
        :return `create_shipment_payload` (dict): payload to send to acu api to mark an RC order as sent to Warehouse (toggle AttributeRCSHP2WH to True) ***shipment*** for a given order
        '''
        mark_rc_as_sent_payload = {
            "CustomerID": { "value": order['CustomerID'] },
            "OrderType": {"value": order['OrderType']},
            "OrderNbr": { "value": order['OrderNbr']},
            "custom": {
                "Document": {
                    "AttributeRCSHP2WH": {
                        "value": True
                    },
                    "AttributeRCSHP2WHDT": {
                        "value": True
                    }
                }
            } 
        }
        return mark_rc_as_sent_payload
    #endregion


    #region format_validate_order_address
    def format_validate_order_address(self, order: dict) -> dict:
        payload = self._format_sales_order_entity_payload_(order)
        return payload

    #endregion

    #region format_sales_order_entity_payload
    def _format_sales_order_entity_payload_(self, order: dict) -> dict:
        ''':class:`~`.:meth:`~_format_sales_order_entity_payload_` (self, order: *dict*, ):
        ---
        <hr>
        
        put_summary_here
        
        ### Downstream Calls 
         #### :class:`~class`.:meth:`~method`
            - Description
         #### :class:`~folder.file.class`.:meth:`~folder.file.class.method`
            - Description
        
        ### Upstream Calls 
         #### :class:`~class`.:meth:`~method`
            - Description
         #### :class:`~folder.file.class`.:meth:`~folder.file.class.method`
            - Description
            
        <hr>
        
        Parameters
        ---
        :param (*dict*) `order`: _description_
        
        <hr>
        
        Returns
        ---
        :return `payload` (dict): Standard Sales Order Entity type payload
        '''               
        payload = {
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
        return payload

