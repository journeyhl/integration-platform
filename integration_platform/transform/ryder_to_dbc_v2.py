from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.ryder_to_dbc import RyderToDbc
import logging
import polars as pl
from datetime import datetime

class Transform:
    def __init__(self, pipeline: RyderToDbc):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.Transform')
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
            parsed_milestones = self._parse_milestones_()
            parsed_history = self._parse_history_()
            bp = 'here'
        bp = 'here'
        

    def _parse_history_(self):
        self.logger.info(f'{self.log_prefix} Parsing history data...')
        if self.current_history == {}:
            self.logger.info(f'{self.log_prefix}No history data found for {self.current_shipnbr}...skipping')
            return
        bp = 'here'

    def _parse_milestones_(self):
        self.logger.info(f'{self.log_prefix} Parsing milestone events...')
        if self.current_milestones == {}:
            self.logger.info(f'{self.log_prefix}No milestone data found for {self.current_shipnbr}...skipping')
            return
        tracking = self.current_milestones['lobParentTracking']
        order_info = self.current_milestones['orderInfo']
        references = self.__parse_milestone_references__(order_info['orderReferences'])
        current_status = self.__parse_milestone_event_current_status__(event=order_info['currentOrderStatus'], event_nbr=order_info['currentOrderStatus']['sequence'])
        milestone_events = self.__parse_milestone_events__(order_info['mileStoneEvents'])
        bp = 'here'

    def __parse_milestone_events__(self, milestone_events: list):
        total_events = len(milestone_events)
        events = []
        self.logger.info(f'{self.log_prefix}Parsing {f'{total_events} event' if total_events == 1 else f'{total_events} events'}...')
        for i, event in enumerate(milestone_events):
            event_nbr = i+1
            fmt_event = self.__parse_milestone_event_current_status__(event=event, event_nbr=event_nbr)
            events.append(fmt_event)
            bp = 'here'
        return events

    def __parse_milestone_event_current_status__(self, event: dict, event_nbr: int):
        fmt_current_status = {
            'ShipmentNbr': self.current_reference_nbrs['jhl_ShipmentNbr'],
            'RyderID': self.current_reference_nbrs['rlm_ID'],
            'EventNbr': event_nbr,
            'StatusCode': event['statusCode'],
            'Description': event['description'],
            'City': event['city'],
            'State': event['state'],
            'Zip': event['zip'],
            'Datetime': self.pipeline.default_transformer.parse_date_str(date_str=event['dateTime'], tries=0, log_prefix=self.log_prefix),
            'DatetimeUTC': self.pipeline.default_transformer.parse_date_str(date_str=event['localDateTime'], tries=0, offset=True, log_prefix=self.log_prefix),
        }
        return fmt_current_status

    #region __parse_references__
    def __parse_milestone_references__(self, order_references: list[dict]) -> dict:
        '''
        :class:`~Transform`.:meth:`~parse_references` (self):
        ---
        <hr>
        
        Parses each shipment's `references` value, which Ryder gives as a list
        
        ### Downstream Calls 
         #### :class:`~integration_platform.transform.ryder_to_dbc.Transform`.:meth:`~integration_platform.transform.ryder_to_dbc.Transform._get_order_nbr_from_reference_`
            - Parses OrderLineNbr (PH100001-1) and gets OrderType, OrderNbr and LineNbr
        
        ### Upstream Calls 
         #### :class:`~integration_platform.transform.ryder_to_dbc.Transform`.:meth:`~integration_platform.transform.ryder_to_dbc.Transform.landing`
            
        <hr>
        
        Returns
        ---
        :return `documents` (_dict_): dictionary containing Ryder RefNbrs and their corresponding key values in Acumatica

        Sets
        ---
            - #### self.:attr:`~integration_platform.transform.ryder_to_dbc_v2.Transform.current_reference_nbrs`
        '''        
        reference_nbrs = {}
        bp = 'here'
        for ref in order_references:
            bp = 'here'
            if ref['referenceType'].lower() in['client', 'oo']:
                reference_nbrs['rlm_ClientRefNbr'] = ref['referenceNumber']
                reference_nbrs['jhl_ShipmentNbr'] = ref['referenceNumber']
            elif ref['referenceType'].lower() == 'orid':
                reference_nbrs['rlm_ID'] = ref['referenceNumber']
            elif ref['referenceType'].lower() == 'po':
                reference_nbrs = self.___get_order_nbr_from_reference___(ref_nbr=ref['referenceNumber'], reference_nbrs=reference_nbrs)
            else:
                self.logger.warning(f'No code written for non CLIENT/PO type orders!')
                bp = 'here'
        self.current_reference_nbrs = reference_nbrs
        return reference_nbrs
    #endregion


    
    #region _get_order_nbr_from_reference_
    def ___get_order_nbr_from_reference___(self, ref_nbr: str, reference_nbrs: dict) -> dict:
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
        :param (*dict*) `reference_nbrs`: dictionary to add rlm_PORefNbr, jhl_OrderLineNbr, jhl_OrderType, jhl_OrderNbr 
        
        <hr>
        
        Returns
        ---
        :return `documents` (*dict*): originally passed dict with the parsed values added
        '''
        reference_nbrs['rlm_PORefNbr'] = ref_nbr
        reference_nbrs['jhl_OrderLineNbr'] = ref_nbr
        reference_nbrs['jhl_OrderType'] = ref_nbr[:2] or None
        if '-' in ref_nbr:
            dash = ref_nbr.find('-')
            reference_nbrs['jhl_OrderNbr'] = ref_nbr[:dash] 
            reference_nbrs['jhl_LineNbr'] = int(ref_nbr[dash+1:])
        else:
            reference_nbrs['jhl_OrderNbr'] = ref_nbr
            reference_nbrs['jhl_LineNbr'] = None
        return reference_nbrs
    #endregion
