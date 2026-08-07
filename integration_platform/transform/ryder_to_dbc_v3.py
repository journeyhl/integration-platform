from __future__ import annotations
from typing import TYPE_CHECKING, Literal, Any
if TYPE_CHECKING:
    from integration_platform.pipelines.ryder_to_dbc import RyderToDbc
import logging
import polars as pl
from datetime import datetime

class Transform:
    def __init__(self, pipeline: RyderToDbc):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.Transform')
        self.found_in_history_not_milestone = {}
        pass


    def landing(self, data_extract: dict[str, dict]):
        bp = 'here'
        self.orders = []
        total = len(data_extract)
        for i, (shipment_nbr, history__and_milestones) in enumerate(data_extract.items()):
            self.log_prefix = f'{shipment_nbr}, {i+1}/{total}: '
            self.current_shipment = {shipment_nbr: history__and_milestones}
            self.current_shipnbr = shipment_nbr
            self.current_history = history__and_milestones['history']
            self.current_milestones = history__and_milestones['milestones']

            self._parse_order_info_(order_info=self.current_history['orderInfo'], sender='history')
            # self._compare_diff_()
            # parsed_milestones = self._parse_milestones_()
            bp = 'here'
        bp = 'here'
        


    def _parse_order_info_(self, order_info: dict, sender: Literal['history', 'milestone']):
        '''We can expect  account, brand, consigneeInfo, serviceLocation, shipperInfo to not be in milestone'''
        tracking_nbr = order_info['lobTracking']
        rlm_order_nbr= order_info['orderNumber']
        references = order_info['orderReferences']
        current_status = order_info['currentOrderStatus']
        events = order_info['mileStoneEvents']
        #history only
        consignee_info = order_info.get('consigneeInfo')
        service_location = order_info.get('serviceLocation')
        shipper_info = order_info.get('shipperInfo')


        fmt_references = self.__parse_references__(references=references)
        fmt_current_status = self.__parse_event__(event=current_status, event_nbr=current_status['sequence'], refs=fmt_references)
        fmt_events = [self.__parse_event__(event=event, event_nbr=i+1, refs=fmt_references) for i, event in enumerate(events)]


        bp = 'here'


    def __parse_references__(self, references: list[dict]) -> dict:
        refs = {}
        for ref in references:
            if ref['referenceType'].lower() in['client', 'oo']:
                refs['ShipmentNbr'] = ref['referenceNumber']
            elif ref['referenceType'].lower() == 'orid':
                refs['RyderID'] = ref['referenceNumber']
            elif ref['referenceType'].lower() == 'po':
                refs = self.___get_order_nbr_from_reference___(ref_nbr=ref['referenceNumber'], refs=refs)
        return refs

    def __parse_event__(self, event: dict, event_nbr: int, refs: dict):
        fmt_current_status = {
            'ShipmentNbr': refs['ShipmentNbr'],
            'RyderID': refs['RyderID'],
            'EventNbr': event_nbr,
            'StatusCode': event['statusCode'],
            'Description': event['description'],
            'City': event['city'],
            'State': event['state'],
            'Zip': event['zip'],
            'DatetimeLocal': self.pipeline.default_transformer.parse_date_str(date_str=event['dateTime'], tries=0, log_prefix=self.log_prefix),
            'DatetimeUTC': self.pipeline.default_transformer.parse_date_str(date_str=event['localDateTime'], tries=0, offset=True, log_prefix=self.log_prefix),
        }
        return fmt_current_status






    
    #region _get_order_nbr_from_reference_
    def ___get_order_nbr_from_reference___(self, ref_nbr: str, refs: dict) -> dict:
        '''
        :class:`~Transform`.:meth:`~_get_order_nbr_from_reference_` (self, ref_nbr: *str*, documents: *dict*):
        ---
        <hr>
        
        Given the Ryder referenceNumber for a PO type reference (JHL Order) and a dict, parse ref_nbr
        
        ### Upstream Calls 
         #### :class:`~integration_platform.transform.ryder_to_dbc.Transform`.:meth:`~integration_platform.transform.ryder_to_dbc.Transform.parse_references`
            - Called when Ryder's `referenceType` == 'PO'
            
        <hr>
        
        Parameters
        ---
        :param (*str*) `ref_nbr`: Ryder referenceNumber or JHL OrderNbr-LineNbr (PH100001-1)
        :param (*dict*) `refs`: dictionary to add OrderType and OrderNbr
        
        <hr>
        
        Returns
        ---
        :return `refs` (*dict*): originally passed dict with the parsed values added
        '''
        refs['OrderType'] = ref_nbr[:2] or None
        if '-' in ref_nbr:
            dash = ref_nbr.find('-')
            refs['OrderNbr'] = ref_nbr[:dash] 
        else:
            refs['jhl_OrderNbr'] = ref_nbr
        return refs
    #endregion





    def _compare_diff_(self):
        bp = 'here'
        h_info: dict = self.current_history['orderInfo']
        m_info: dict = self.current_milestones['orderInfo']

        #remove this when done
        not_in = []
        is_in = []
        for key, item in h_info.items():
            if m_info.get(key) == None:
                self.logger.error(f'{key} is in History, but not milestone')
                if self.found_in_history_not_milestone.get(key) == None:
                    not_in.append(key)
                    self.found_in_history_not_milestone[key] = item
            else:
                bp = 'here'
                if isinstance(item, dict):
                    for subkey, subitem in item.items():
                        key_subkey = f"{key}['{subkey}']"
                        if m_info[key].get(subkey) == None:
                            self.logger.error(f'{key_subkey} is in History, but not milestone')
                            if self.found_in_history_not_milestone.get(key_subkey) == None:
                                not_in.append(key_subkey)
                                self.found_in_history_not_milestone[key_subkey] = subitem
                            

                    bp = 'here'
                elif isinstance(item, list):
                    for litem in item:
                        for subkey, subitem in litem.items():
                            key_subkey = f"{key}['{subkey}']"
                            if litem.get(subkey) == None:
                                self.logger.error(f'{key_subkey} is in History, but not milestone')
                                if self.found_in_history_not_milestone.get(key_subkey) == None:
                                    not_in.append(key_subkey)
                                    self.found_in_history_not_milestone[key_subkey] = subitem



                    bp = 'here'
                else:
                    is_in.append(key)
        self.logger.warning(', '.join(not_in))
        bp = 'here'




        