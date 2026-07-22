
from __future__ import annotations
from typing import TYPE_CHECKING, Literal
if TYPE_CHECKING:
    from integration_platform.connectors.acu_api import AcumaticaAPI
import logging
import requests
import time
from datetime import datetime, timedelta
import polars as pl

class AcumaticaAPIHelper:
    def __init__(self, acu_api: AcumaticaAPI) -> None:
        self.acu = acu_api
        if type(acu_api.pipeline) == str:
            self.logger = logging.getLogger(f'{acu_api.pipeline}.AcumaticaAPIHelper')
        else:
            self.logger = logging.getLogger(f'{acu_api.pipeline.pipeline_name}.AcumaticaAPIHelper')
        
        pass


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




    def format_data_log_entry(self, entity: str, key_value: str, operation: str, payload: dict, response: str, tstamp: datetime, options: Literal['append', 'return']):
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
