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


    def landing(self, data_extract):
        bp = 'here'
        self.shipments = []
        self.shipment_addresses = {}
        for i, shipment in enumerate(data_extract):
            self.shipment = shipment
            header = self.parse_header_level()
            references = self.parse_references()
            dates = self.parse_order_dates()
            line_items = self.parse_line_items()
            parsed_shipment = {
                **references,
                **header,
                **dates,
                'Lines': line_items
            }
            self.shipments.append(parsed_shipment)
        bp = 'here'
        return self.shipments




    #region parse_header_level
    def parse_header_level(self) -> dict:
        ''':class:`~Transform`.:meth:`~parse_header_level` (self, ):
        ---
        <hr>
        
        Parses header level of each shipment extracted from Ryder for Ryder's OrderType, Workflow and RefType data

        ### Upstream Calls 
         #### :class:`~integration_platform.transform.ryder_to_dbc.Transform`.:meth:`~integration_platform.transform.ryder_to_dbc.Transform.landing`
            
        <hr>
        
        <hr>
        
        Returns
        ---
        :return `header` (_dict_): dict containing `rlm_OrderType`, `rlm_Workflow`, `rlm_ClientRefType`, corresponding to `enterpriseClientID`, `OrderreqWorkflow` and `ClientRefType` from Ryder
        '''
        header = {
            'rlm_OrderType': self.shipment['enterpriseClientID'],
            'rlm_Workflow': self.shipment['OrderreqWorkflow'],
            'rlm_ClientRefType': self.shipment['ClientRefType'],            
        }
        return header
    #endregion

    #region parse_references
    def parse_references(self) -> dict:
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
        '''        
        documents = {}
        if len(self.shipment['references']) > 2:
            self.logger.warning(f'No code written for line shipment dates!')
            bp = 'here'
        for ref in self.shipment['references']:
            bp = 'here'
            if ref['referenceType'].lower() == 'client':
                documents['rlm_ClientRefNbr'] = ref['referenceNumber']
                documents['jhl_ShipmentNbr'] = ref['referenceNumber']
            elif ref['referenceType'].lower() == 'po':
                documents = self._get_order_nbr_from_reference_(ref_nbr=ref['referenceNumber'], documents=documents)
            else:
                self.logger.warning(f'No code written for non CLIENT/PO type orders!')
                bp = 'here'
        self.references = documents
        return documents
    #endregion


    #region parse_dates
    def parse_order_dates(self) -> dict:
        ''':class:`~Transform`.:meth:`~parse_order_dates` (self, ):
        ---
        <hr>
        
        For each date on the ryder order, parse it and add to dates dictionary=
        
        ### Upstream Calls 
         #### :class:`~integration_platform.transform.ryder_to_dbc.Transform`.:meth:`~integration_platform.transform.ryder_to_dbc.Transform.landing`
            
        <hr>
        
        Returns
        ---
        :return `dates` (dict): dictionary containing all parsed date values
        '''
        dates = {}
        for date_entry in self.shipment['orderreq-dates']:
            if date_entry['dateType'].lower() == 'entry':
                dates['rlm_EntryDate'] = datetime.strptime(date_entry['date'], '%Y-%m-%dT%H:%M:%S')
            else:
                dates['rlm_EntryDate'] = None
                bp = 'here'
        self.dates = dates
        return dates
    #endregion

    #region parse_line_items
    def parse_line_items(self):
        lines = self.shipment['orderlineItems']
        new_lines = []
        for i, line in enumerate(lines):
            line_nbr = i+1
            services = line['lineitemResource']['Services']
            shipments = line['lineitemResource']['Shipments']
            line_services = self._parse_line_services_(line=line, services=services)
            line_shipments = self._parse_line_shipments_(line=line, shipments=shipments)
            new_line = {
                'rlm_LineNbr': line_nbr,
                **line_services,
                **line_shipments
            }
            new_lines.append(new_line)
            bp = 'here'
        return new_lines
    #endregion

    #region _parse_line_services_
    def _parse_line_services_(self, line: dict, services: dict):
        ''':class:`~Transform`.:meth:`~_parse_line_services_` (self, line: *dict*, services: *dict*, ):
        ---
        <hr>
        
        For each line on an order at Ryder, parse the services provided
        
        ### Upstream Calls 
         #### :class:`~integration_platform.transform.ryder_to_dbc.Transform`.:meth:`~integration_platform.transform.ryder_to_dbc.Transform.parse_line_items`
            - Called for each line
            
        <hr>
        
        Parameters
        ---
        :param (*dict*) `line`: dict of line level data
        :param (*dict*) `services`: dict of services being rendered for order
        
        <hr>
        
        Returns
        ---
        :return `line_services` (_dict_): Parsed dictionary of service data for a particular line
        '''        
        line_services = {
            'InventoryCD': services['item']['itemId'],
            'Qty': int(services['item']['quantity']),
            'ServiceType': services['serviceType'],
            'ItemQualifier': services['itemQualifier']
        }
        return line_services
    #endregion

    #region _parse_line_shipments_
    def _parse_line_shipments_(self, line: dict, shipments: dict) -> dict:
        cosignee = shipments['consigneeName']
        phone = shipments['toPhone'][0]['phoneNumber'] if len(shipments['toPhone']) > 0 else None
        addr1 = shipments['shipTo']['address1']
        zip = shipments['shipTo']['postalCode']
        key_shipment = self.references['jhl_ShipmentNbr']
        key_addr = f'{cosignee}-{phone}-{addr1}-{zip}'
        line_shipments = {
            'Consignee': shipments['consigneeName'],
            'Phone': shipments['toPhone'][0]['phoneNumber'] if len(shipments['toPhone']) > 0 else None,
            'Email': shipments['contactEmail'],
            'AddressLine1': shipments['shipTo']['address1'],
            'AddressLine2': shipments['shipTo']['address2'] if shipments['shipTo']['address2'] != '' else None,
            'City': shipments['shipTo']['city'],
            'State': shipments['shipTo']['stateProvince'],
            'ZipCode': shipments['shipTo']['postalCode'],
            'Country': shipments['shipTo']['country'],
            'AddressValidated': shipments['shipTo']['validatedAddress'],
            'Phone2': shipments['toPhone'][1]['phoneNumber'] if len(shipments['toPhone']) > 1 else None,
        }
        self._check_shipment_addresses_(key_shipment=key_shipment, key_addr=key_addr, addr=line_shipments)
        if len(shipments['shipmentDates']) > 0:
            self.logger.warning(f'No code written for line shipment dates!')
            bp = 'here'
        return line_shipments
    #endregion
    

    #region _get_order_nbr_from_reference_
    def _get_order_nbr_from_reference_(self, ref_nbr: str, documents: dict) -> dict:
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
        :param (*dict*) `documents`: dictionary to add rlm_PORefNbr, jhl_OrderLineNbr, jhl_OrderType, jhl_OrderNbr 
        
        <hr>
        
        Returns
        ---
        :return `documents` (*dict*): originally passed dict with the parsed values added
        '''
        documents['rlm_PORefNbr'] = ref_nbr
        documents['jhl_OrderLineNbr'] = ref_nbr
        documents['jhl_OrderType'] = ref_nbr[:2] or None
        if '-' in ref_nbr:
            dash = ref_nbr.find('-')
            documents['jhl_OrderNbr'] = ref_nbr[:dash] 
            documents['jhl_LineNbr'] = ref_nbr[:dash]
        else:
            documents['jhl_OrderNbr'] = ref_nbr
            documents['jhl_LineNbr'] = None
            bp = 'here'
        return documents
    #endregion



    def _check_shipment_addresses_(self, key_shipment: str, key_addr: str, addr: dict):
        if self.shipment_addresses.get(key_shipment) == None:
                self.shipment_addresses[key_shipment] = {key_addr: addr}
        else:            
            if self.shipment_addresses[key_shipment].get(key_addr) == None:
                self.logger.warning(f'Multiple addresses detected!')
                self.shipment_addresses[key_shipment][key_addr] = addr
            else:
                self.logger.info(f'Same address found on all lines, no issues.')
                bp = 'here'
        bp = 'here'