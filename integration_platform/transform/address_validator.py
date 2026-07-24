from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.address_validator import AddressValidator
import logging
import polars as pl

class Transform:    
    def __init__(self, pipeline: AddressValidator):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.Transform')
        pass
    
    def transform(self, data_extract: dict[str, pl.DataFrame]):
        data_transformed = []
        filtered_extract = self.filter(data_extract).to_dicts()
        for order in filtered_extract:
            if order['Match'] == 1:
                self.logger.info(f'{order['OrderNbr']}: Customer has same original Shipping/ Billing address')
                order_avs = self.pipeline.avs.validate(order_data=order, s_or_b='s')
            else:
                self.logger.info(f'{order['OrderNbr']}: Customer has different original Shipping/ Billing addresses')
                order_avs = self.pipeline.avs.validate(order_data=order, s_or_b='s') #validate both
                order_avs = self.pipeline.avs.validate(order_data=order, s_or_b='b') #validate both
            if order_avs['Match'] == 0 and order_avs.get(f'vbAddressLine1') == None and order_avs.get(f'vsAddressLine1') != None:
                self.logger.warning(f'{order['OrderNbr']}: Issue parsing billing address, only validating shipping address')
            if order_avs.get(f'vsAddressLine1') == None:
                self.logger.error(f'{order_avs['OrderNbr']}: No AddressLine1 returned from AVS')
                bp = 'ERROR'
            else:
                order_avs['update_order_address_payload'] = self.format_order_address_payload(order_avs)
                order_avs['acu_api_log_update_override'] = self.format_acu_api_log_update_override(order_avs)
                order_avs['acu_api_log_validate'] = self.format_acu_api_log_validate(order_avs)
                # order_avs['update_customer_address_payload'] = self.format_customer_address_payload(order_avs)
            data_transformed.append(order_avs)
        return data_transformed

    

    def filter(self, data_extract: dict[str, pl.DataFrame]) ->  pl.DataFrame:
        ''':meth:`~filter` (self, data_extract: *dict[str, pl.DataFrame]*):
        ---
        <hr>
        
        Filters out any orders that need to be allocated before they have their address validated
        
        ### Upstream Calls 
         #### :class:`~Transform`.:meth:`~transform`
            - Filters before running main address validation process
            
        <hr>
        
        Parameters
        ---
        :param (*dict[str, pl.DataFrame]*) `data_extract`: dict containing two polars DataFrames, one frame containing the orders to validate, another with orders to filter out
        
        <hr>
        
        Returns
        ---
        :return `filtered_extract` (_pl.DataFrame_): Main polars DataFrame, but with only rows **NOT** having a match in our DataFrame of orders filter out
        '''        
        main_extract = data_extract['main_extract']
        if data_extract['main_extract'].height == 0:
            self.logger.warning(f'No Orders need validation, returning main_extract with 0 rows')
            return main_extract
        filter_extract = data_extract['filter_extract']
        filtered_extract = main_extract.join(filter_extract, on='OrderNbr', how='anti')
        self.logger.info(f'Orders originally pulled: {', '.join([f['OrderNbr'] for f in main_extract.to_dicts()])}')
        self.logger.info(f'Filtered {main_extract.height - filtered_extract.height} rows out of {main_extract.height}...{filtered_extract.height} orders to validate')
        self.logger.warning(f'Filtered out: {', '.join([f['OrderNbr'] for f in filter_extract.to_dicts()])}')
        return filtered_extract
        

    
    def format_order_address_payload(self, order_avs: dict):
        '''
        `format_order_address_payload`(self, order_avs: *dict*)
        ---
        <hr>
        
        Given a dictionary containing a response from AVS, format the payload needed to override and update a Customer's ShipTo Address on a particular **Order**
        
        ### Downstream Function Calls 
         #### :meth:`~_log_differences`
            - Calls out changes that will be made to Order's ShipTo Address in Acumatica
        
        <hr>
        
        Parameters
        ---
        :param (*dict*) `order_avs`: Dictionary containing **OrderType**, **OrderNbr**, **CustomerID**, and a **formatted AVS address response**

         - **vAddressLine1**, **vAddressLine2**, **vCity**, **vState**, **vPostalCode**, **vCountryID**
        
        <hr>
        
        Returns
        ---
        :return `payload` (dict): payload ready to send to Acumatica API (SalesOrder endpoint)
        '''
        payload = {
            "OrderType":   { "value": order_avs['OrderType'] },
            "OrderNbr":    { "value": order_avs['OrderNbr'] },
            "CustomerID": {"value": order_avs['AcctCD']},
            "ShipToAddressOverride": { "value": True },
            "ShipToAddress": {
                "AddressLine1": {"value": order_avs['vsAddressLine1']},
                "AddressLine2": {"value": order_avs['vsAddressLine2']},
                "City":         {"value": order_avs['vsCity']},
                "State":        {"value": order_avs['vsState']},
                "PostalCode":   {"value": order_avs['vsPostalCode']},
                "Country":      {"value": order_avs['vsCountryID']},                
            }
        }
        if order_avs['Match'] == 1:
            payload['BillToAddressOverride'] = { "value": True }
            payload['BillToAddress'] = {
                "AddressLine1": {"value": order_avs['vsAddressLine1']},
                "AddressLine2": {"value": order_avs['vsAddressLine2']},
                "City":         {"value": order_avs['vsCity']},
                "State":        {"value": order_avs['vsState']},
                "PostalCode":   {"value": order_avs['vsPostalCode']},
                "Country":      {"value": order_avs['vsCountryID']},                
            }
        elif order_avs['Match'] == 0 and order_avs.get('vbAddressLine1') != None:
            payload['BillToAddressOverride'] = { "value": True }
            payload['BillToAddress'] = {
                "AddressLine1": {"value": order_avs['vbAddressLine1']},
                "AddressLine2": {"value": order_avs['vbAddressLine2']},
                "City":         {"value": order_avs['vbCity']},
                "State":        {"value": order_avs['vbState']},
                "PostalCode":   {"value": order_avs['vbPostalCode']},
                "Country":      {"value": order_avs['vbCountryID']},                
            }
        if order_avs['WhichPhone'] != 'Valid':
            payload = self.determine_which_phone(order_avs, payload)
        self._log_differences(order_avs)
        return payload
    

    def determine_which_phone(self, order_avs: dict, payload: dict) -> dict:
        bp = 'here'
        if 'Invalid' not in order_avs['WhichPhone']:
            phone_to_use = order_avs[order_avs['WhichPhone']]
            bp = 'here'
            if order_avs['WhichPhone'] == 'defPhone':
                self.logger.info(f"Swapping BOTH ShipTo and BillTo Phone1 values with Customer's default phone number")
                payload['ShipToContactOverride'] = { "value": True }
                payload['ShipToContact'] = {"Phone1": {"value": order_avs['defPhone']}}
                payload['BillToContactOverride'] = { "value": True }
                payload['BillToContact'] = {"Phone1": {"value": order_avs['defPhone']}}
            elif order_avs['WhichPhone'] == 'sPhone':
                self.logger.info(f"Swapping BillTo Phone1 value with Customer's ShipTo phone number")
                payload['BillToContactOverride'] = {"value": True}
                payload['BillToContact'] = {"Phone1": {"value": order_avs['sPhone']},}
            elif order_avs['WhichPhone'] == 'bPhone':
                self.logger.info(f"Swapping ShipTo Phone1 value with Customer's BillTo phone number")
                payload['ShipToContactOverride'] = {"value": True}
                payload['ShipToContact'] = {"Phone1": {"value": order_avs['bPhone']}}

        else:
            self.logger.warning(f'Phone number is invalid! {order_avs['WhichPhone']}...')
            self.logger.warning(f'Using default company phone (800-958-8324)')
            payload['ShipToContactOverride'] = { "value": True }
            payload['ShipToContact'] = {
                "Phone1": {"value": '8009588324'},               
            }
            payload['BillToContactOverride'] = { "value": True }
            payload['BillToContact'] = {
                "Phone1": {"value": '8009588324'},               
            }


        return payload



    def format_acu_api_log_update_override(self, order_avs: dict):
        '''`format_acu_api_log_update_override`(self, order_avs: *dict*)
        ---
        <hr>
        
        Formats the constant part of the dict of data that we'll load to **_util.acu_api_log** when overriding and updating an address
            
        <hr>
        
        Parameters
        ---
        :param (*dict*) `order_avs`: Dictionary containing **OrderNbr**, and **update_order_address_payload** (the return from :meth:`~format_order_address_payload`)
        
        <hr>
        
        Returns
        ---
        :return `data_log_entry` (dict): _description_
        '''
        data_log_entry = {            
            'Entity': 'SalesOrder',
            'KeyValue': f'{order_avs['OrderNbr']}',
            'Operation': f'PUT - Override & Update Address',
            'Payload': order_avs['update_order_address_payload'],
        }
        return data_log_entry
    
    def format_acu_api_log_validate(self, order_avs: dict):
        '''`format_acu_api_log_validate`(self, order_avs: *dict*)
        ---
        <hr>
        
        Formats the constant part of the dict of data that we'll load to **_util.acu_api_log** when validating an address
            
        <hr>
        
        Parameters
        ---
        :param (*dict*) `order_avs`: Dictionary containing **OrderNbr**, and **update_order_address_payload** (the return from :meth:`~format_order_address_payload`)
        
        <hr>
        
        Returns
        ---
        :return `data_log_entry` (dict): constant values used for _util.acu_aupi_log
        '''
        data_log_entry = {            
            'Entity': 'SalesOrder',
            'KeyValue': f'{order_avs['OrderNbr']}',
            'Operation': f'POST - Validate Address',
        }
        return data_log_entry





    
    def _log_differences(self, order_avs: dict):
        '''`_log_differences`(self, order_avs: *_type_*)
        ---
        <hr>
        
        Notes differences between the original address we got from Acumatica and the response from AVS
        '''
        self.logger.info(f'{order_avs['OrderNbr']}: Comparing AVS address to original...')
        if order_avs['Match'] == 1 or order_avs.get('vbAddressLine1') == None:
            for (current, new, name) in [
                (order_avs['sAddressLine1'], order_avs['vsAddressLine1'], 'AddressLine1'),
                (order_avs['sAddressLine2'], order_avs['vsAddressLine2'], 'AddressLine2'),
                (order_avs['sCity'], order_avs['vsCity'], 'City'),
                (order_avs['sState'], order_avs['vsState'], 'State'),
                (order_avs['sPostalCode'], order_avs['vsPostalCode'], 'PostalCode'),
                (order_avs['sCountryID'], order_avs['vsCountryID'], 'CountryID'),
            ]:
                if current != new:
                    self.logger.info(f'{order_avs['OrderNbr']}: {name}: {current} -> {new}')
                    bp = 'here'
                bp = 'here'
        elif order_avs['Match'] == 0:
            for (current, new, name) in [
                (order_avs['sAddressLine1'], order_avs['vsAddressLine1'], 'ShipToAddressLine1'),
                (order_avs['sAddressLine2'], order_avs['vsAddressLine2'], 'ShipToAddressLine2'),
                (order_avs['sCity'], order_avs['vsCity'], 'ShipToCity'),
                (order_avs['sState'], order_avs['vsState'], 'ShipToState'),
                (order_avs['sPostalCode'], order_avs['vsPostalCode'], 'ShipToPostalCode'),
                (order_avs['sCountryID'], order_avs['vsCountryID'], 'ShipToCountryID'),
                (order_avs['bAddressLine1'], order_avs['vbAddressLine1'], 'BillToAddressLine1'),
                (order_avs['bAddressLine2'], order_avs['vbAddressLine2'], 'BillToAddressLine2'),
                (order_avs['bCity'], order_avs['vbCity'], 'BillToCity'),
                (order_avs['bState'], order_avs['vbState'], 'BillToState'),
                (order_avs['bPostalCode'], order_avs['vbPostalCode'], 'BillToPostalCode'),
                (order_avs['bCountryID'], order_avs['vbCountryID'], 'BillToCountryID'),
            ]:
                if current != new:
                    self.logger.info(f'{order_avs['OrderNbr']}: {name}: {current} -> {new}')
                    bp = 'here'
                bp = 'here'


