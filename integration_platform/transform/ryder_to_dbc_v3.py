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
        self.orders = {}
        total = len(data_extract)
        for i, (shipment_nbr, history__and_milestones) in enumerate(data_extract.items()):
            self.log_prefix = f'{shipment_nbr}, {i+1}/{total}: '
            self.current_shipment = {shipment_nbr: history__and_milestones}
            self.current_shipnbr = shipment_nbr
            self.current_history = history__and_milestones['history']
            self.current_milestones = history__and_milestones['milestones']
            if history__and_milestones['history'] == {} and history__and_milestones['milestones'] == {}:
                self.logger.warning(f'{self.log_prefix}No data available')
                continue
            parsed_order_info = self._parse_order_info_(order_info=self.current_history['orderInfo'], sender='history')
            parsed_shipment_info = self._parse_shipment_info_(shipment_info=self.current_history['shipmentInfo'])
            self.orders[shipment_nbr] = {
                'parsed_order_info': parsed_order_info,
                'count_shipments': len(parsed_shipment_info),
                'parsed_shipment_info': parsed_shipment_info,
                'extract_time': history__and_milestones['extract_time']
            }
            
            # self._compare_diff_()
            bp = 'here'
        return self.orders
        

    def _parse_shipment_info_(self, shipment_info: list[dict]):
        fmt_shipments = []
        total = len(shipment_info)
        self.logger.info(f'{self.log_prefix}{total} shipments found')
        for i, shipment in enumerate(shipment_info):
            self.current_order_shipment = shipment
            rlm_shipment_id = shipment['shipmentId']
            self.current_order_ship_delivery_type = shipment['deliveryType']
            self.current_order_ship_order_type = shipment['orderType']
            fmt_sku_info = [self.__parse_sku_info__(item) for item in shipment['skuInfo']]
            fmt_events = [self.__parse_shipment_events__(event, event_nbr=i+1) for i, event in enumerate(shipment['events'])]
            self.logger.info(f'{self.log_prefix}Parsed Shipment {rlm_shipment_id} sku and event data, {len(fmt_sku_info)} items and {len(fmt_events)} events')
            fmt_shipment = {
                'ship_events': fmt_events,
                'ship_items': fmt_sku_info,
                'count_items': len(fmt_sku_info),
                'count_events': len(fmt_events)
            }
            fmt_shipments.append(fmt_shipment)
        return fmt_shipments

    def __parse_sku_info__(self, sku_info):
        fmt_sku = {
            'RLM_OrderNumber': self.rlm_order_nbr,
            'TrackingNbr': self.tracking_nbr,
            'ShipmentNbr': self.current_refs['ShipmentNbr'],
            'RyderID': self.current_refs['RyderID'],
            'ShipmentID': self.current_order_shipment['shipmentId'],
            'TrackingNbr': self.tracking_nbr,
            'DeliveryType': self.current_order_ship_delivery_type,
            'OrderType': self.current_order_ship_order_type,
            'InventoryCD': self.pipeline.default_transformer.clean_string(string=sku_info['code'], string_descr='sku', log_prefix=self.log_prefix),
            'Description': self.pipeline.default_transformer.clean_string(string=sku_info['description'], string_descr='sku description', log_prefix=self.log_prefix),
            'Length': self.pipeline.default_transformer.string_to_int(int_str=sku_info['dims']['length'], str_descr='sku length', log_prefix=self.log_prefix),
            'Wdith': self.pipeline.default_transformer.string_to_int(int_str=sku_info['dims']['width'], str_descr='sku width', log_prefix=self.log_prefix),
            'Height': self.pipeline.default_transformer.string_to_int(int_str=sku_info['dims']['height'], str_descr='sku height', log_prefix=self.log_prefix),
            'Weight': self.pipeline.default_transformer.string_to_int(int_str=sku_info['dims']['weight'], str_descr='sku weight', log_prefix=self.log_prefix),
            'FAK': self.pipeline.default_transformer.string_to_int(int_str=sku_info['dims']['fak'], str_descr='sku fak', log_prefix=self.log_prefix),
            'CartonID': self.pipeline.default_transformer.clean_string(string=sku_info['references']['cartonID'], string_descr='sku cartonID', log_prefix=self.log_prefix),
            'Serial': self.pipeline.default_transformer.clean_string(string=sku_info['references']['serial'], string_descr='sku serial', log_prefix=self.log_prefix),
            'RANbr': self.pipeline.default_transformer.clean_string(string=sku_info['references']['raNumber'], string_descr='sku raNumber', log_prefix=self.log_prefix),
            'ClientLineID': self.pipeline.default_transformer.string_to_int(int_str=sku_info['references']['clientLineID'], str_descr='sku client line id', log_prefix=self.log_prefix),
            'CosigneePO': self.pipeline.default_transformer.clean_string(string=sku_info['references']['consigneePO'], string_descr='sku consigneePO', log_prefix=self.log_prefix),
            'CosigneeOrd': self.pipeline.default_transformer.clean_string(string=sku_info['references']['consigneeOrd'], string_descr='sku consigneeOrd', log_prefix=self.log_prefix),
            'BrandCode': self.pipeline.default_transformer.clean_string(string=sku_info['references']['brandCode'], string_descr='sku brandCode', log_prefix=self.log_prefix),
            'TrackingID': self.pipeline.default_transformer.clean_string(string=sku_info['references']['trackingID'], string_descr= 'sku trackingId', log_prefix=self.log_prefix),
        }
        return fmt_sku

    def __parse_shipment_events__(self, event: dict, event_nbr: int):
        fmt_event = {
            'RLM_OrderNumber': self.rlm_order_nbr,
            'TrackingNbr': self.tracking_nbr,
            'ShipmentNbr': self.current_refs['ShipmentNbr'],
            'RyderID': self.current_refs['RyderID'],
            'ShipmentID': self.current_order_shipment['shipmentId'],
            'DeliveryType': self.current_order_ship_delivery_type,
            'OrderType': self.current_order_ship_order_type,
            'EventID': event['id'],
            'EventNbr': event_nbr,
            'Code': self.pipeline.default_transformer.clean_string(event['code']),
            'Reason': self.pipeline.default_transformer.clean_string(event['reason']),
            'Description': self.pipeline.default_transformer.clean_string(event['description']),
            'Comments': self.pipeline.default_transformer.clean_string(event['comments']),
            'Location': self.pipeline.default_transformer.string_case_pascal(event['eventLocation']),
            'Datetime': self.pipeline.default_transformer.parse_date_str(date_str=event['dateTime'], tries=0),
        }
        self.logger.info(f'{self.log_prefix}Parsed Shipment Event {event_nbr} ({event['id']}) successfully!')
        return fmt_event

    def _parse_order_info_(self, order_info: dict, sender: Literal['history', 'milestone']):
        '''We can expect  account, brand, consigneeInfo, serviceLocation, shipperInfo to not be in milestone'''

        self.logger.info(f'{self.log_prefix}Parsing Order information')
        tracking_nbr = order_info['lobTracking']
        rlm_order_nbr= order_info['orderNumber']
        references = order_info['orderReferences']
        current_status = order_info['currentOrderStatus']
        events = order_info['mileStoneEvents']
        self.tracking_nbr = tracking_nbr
        self.rlm_order_nbr = rlm_order_nbr
        #history only
        consignee_info = order_info.get('consigneeInfo') or {}
        service_location = order_info.get('serviceLocation') or {}
        shipper_info = order_info.get('shipperInfo') or {}


        fmt_references = self.__parse_references__(references=references)
        fmt_current_status = self.__parse_event__(event=current_status, event_nbr=current_status['sequence'])
        self.logger.info(f'{self.log_prefix}{len(events)} found')
        fmt_events = [self.__parse_event__(event=event, event_nbr=i+1) for i, event in enumerate(events)]
        fmt_cosignee = self._parse_cosignee_info_(cosignee=consignee_info)
        fmt_service_location = self.__parse_service_location__(service_location=service_location)
        fmt_shipper = self.__parse_shipper_info__(shipper_info=shipper_info)

        fmt_order = {
            'RLM_OrderNumber': rlm_order_nbr,
            'TrackingNbr': tracking_nbr,
            **fmt_references,
            'CurrentStatus': fmt_current_status,
            'Events': fmt_events,
            'ShipTo': fmt_cosignee,
            'ServiceLocation': fmt_service_location,
            'Shipper': fmt_shipper
        }
        return fmt_order




        

    def __parse_references__(self, references: list[dict]) -> dict:
        ''':class:`~Transform`.:meth:`~__parse_references__` (self, references: *list[dict]*):
        ---
        <hr>
        
        Parses the references list from Ryder API, which contains our key values
        
        ### Downstream Calls 
         #### :class:`~integration_platform.transform.ryder_to_dbc_v3.Transform`.:meth:`~integration_platform.transform.ryder_to_dbc_v3.Transform.___get_order_nbr_from_reference___`
            - Gets `Ordertype` and `OrderNbr` when referenceType == 'PO'
        
        ### Upstream Calls 
         #### :class:`~integration_platform.transform.ryder_to_dbc_v3.Transform`.:meth:`~integration_platform.transform.ryder_to_dbc_v3.Transform._parse_order_info_`
            - Description
            
        <hr>
        
        Parameters
        ---
        :param (*list[dict]*) `references`: list of dicts, each dict containing info for a different reference/key value
        
        <hr>
        
        Returns
        ---
        :return `refs` (dict): Reference numbers in dictionary format. We should get `ShipmentNbr`, `RyderID`, `OrderNbr` and `OrderType`
        '''        
        refs = {}
        for ref in references:
            if ref['referenceType'].lower() in['client', 'oo']:
                refs['ShipmentNbr'] = ref['referenceNumber']
            elif ref['referenceType'].lower() == 'orid':
                refs['RyderID'] = ref['referenceNumber']
            elif ref['referenceType'].lower() == 'po':
                refs = self.___get_order_nbr_from_reference___(ref_nbr=ref['referenceNumber'], refs=refs)
        self.current_refs = refs
        self.logger.info(f'{self.log_prefix}Parsed references successfully! set self.current_refs to refs ({refs.get('ShipmentNbr')})')
        return refs

    def __parse_event__(self, event: dict, event_nbr: int):
        ''':class:`~Transform`.:meth:`~__parse_event__` (self, event: *dict*, event_nbr: *int*, refs: *dict*, ):
        ---
        <hr>
        
        Given a milestone event OR the current status, clean up and format for SQL
        
        ### Downstream Calls 
         #### :class:`~integration_platform.transform.default_transformer.DefaultTransformer`.:meth:`~integration_platform.transform.default_transformer.DefaultTransformer.parse_date_str`
            - Parses dates
        
        ### Upstream Calls 
         #### :class:`~integration_platform.transform.ryder_to_dbc_v3.Transform`.:meth:`~integration_platform.transform.ryder_to_dbc_v3.Transform._parse_order_info_` x2

        <hr>
        
        Parameters
        ---
        :param (*dict*) `event`: dictionary of even data
        :param (*int*) `event_nbr`: The event number or sequence. 1 is frst, every other event incremenmts by 1
        
        <hr>
        
        Returns
        ---
        :return `fmt_event` (*dict*): Formatted dictionary of event/current status data.
        '''        
        fmt_event = {
            'ShipmentNbr': self.current_refs['ShipmentNbr'],
            'RyderID': self.current_refs['RyderID'],
            'EventNbr': event_nbr,
            'StatusCode': self.pipeline.default_transformer.clean_string(string=event['statusCode'], string_descr='statusCode', log_prefix=self.log_prefix),
            'Description': self.pipeline.default_transformer.clean_string(string=event['description'], string_descr='description', log_prefix=self.log_prefix),
            'City': self.pipeline.default_transformer.string_case_pascal(string=event['city'], string_descr='city', log_prefix=self.log_prefix),
            'State': self.pipeline.default_transformer.clean_string(string=event['state'], string_descr='state', log_prefix=self.log_prefix),
            'Zip': self.pipeline.default_transformer.clean_string(string=event['zip'], string_descr='zip', log_prefix=self.log_prefix),
            'DatetimeLocal': self.pipeline.default_transformer.parse_date_str(date_str=event['dateTime'], tries=0, log_prefix=self.log_prefix),
            'DatetimeUTC': self.pipeline.default_transformer.parse_date_str(date_str=event['localDateTime'], tries=0, offset=True, log_prefix=self.log_prefix),
        }
        self.logger.info(f'{self.log_prefix}Parsed order level Event {event_nbr} successfully!') if event.get('sequence') == None else self.logger.info(f'{self.log_prefix}Parsed Current Order Status event(#{event_nbr}) successfully!')
        return fmt_event






    
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





    def _parse_cosignee_info_(self, cosignee: dict):
        ''':class:`~Transform`.:meth:`~_parse_cosignee_` (self, cosignee: *dict*, ):
        ---
        <hr>
        
        Given a dictionary of cosignee info (Ship-To name, address, phones and email), format for SQL
        
        ### Downstream Calls 
         #### :class:`~integration_platform.transform.default_transformer.DefaultTransformer`.:meth:`~integration_platform.transform.default_transformer.DefaultTransformer.clean_string`
            - Description
         #### :class:`~integration_platform.transform.default_transformer.DefaultTransformer`.:meth:`~integration_platform.transform.default_transformer.DefaultTransformer.parse_phone`
            - Description
        
        ### Upstream Calls 
         #### :class:`~integration_platform.transform.ryder_to_dbc_v3.Transform`.:meth:`~integration_platform.transform.ryder_to_dbc_v3.Transform._parse_order_info_`
            
        <hr>
        
        Parameters
        ---
        :param (*dict*) `cosignee`: dictionary of ship to info
        
        <hr>
        
        Returns
        ---
        :return `fmt_cosignee` (_dict_): Dictionary with cleaned up ship-to data  
        '''        
        bp = 'here'
        if cosignee == {}:
            self.logger.info(f'{self.log_prefix}No cosignee, returning None...')
            return None
        fmt_cosignee = {
            'ShipmentNbr': self.current_refs['ShipmentNbr'],
            'RyderID': self.current_refs['RyderID'],
            'Name': self.pipeline.default_transformer.string_case_pascal(string=cosignee['name'], string_descr='cosignee name', log_prefix=self.log_prefix),
            'Address1': self.pipeline.default_transformer.string_case_pascal(string=cosignee['address1'], string_descr='cosginee address1', log_prefix=self.log_prefix),
            'Address2': self.pipeline.default_transformer.string_case_pascal(string=cosignee['address2'], string_descr='cosginee address2', log_prefix=self.log_prefix),
            'Address3': self.pipeline.default_transformer.string_case_pascal(string=cosignee['address3'], string_descr='cosginee address3', log_prefix=self.log_prefix),
            'Address4': self.pipeline.default_transformer.string_case_pascal(string=cosignee['address4'], string_descr='cosginee address4', log_prefix=self.log_prefix),
            'City': self.pipeline.default_transformer.string_case_pascal(string=cosignee['city'], string_descr='cosginee city', log_prefix=self.log_prefix),
            'State': cosignee['state'],
            'State': self.pipeline.default_transformer.clean_string(string=cosignee['state'], string_descr='cosginee state', log_prefix=self.log_prefix),
            'Zip': self.pipeline.default_transformer.string_case_pascal(string=cosignee['zip'], string_descr='cosignee zip'),
            'Email': self.pipeline.default_transformer.clean_string(string=cosignee['email'], string_descr='cosginee email', log_prefix=self.log_prefix),
            'PhonePrimary': self.pipeline.default_transformer.parse_phone(phone_str=cosignee['primaryContact'], string_descr='cosignee phone1 (primaryContact)', log_prefix=self.log_prefix),
            'PhoneCell': self.pipeline.default_transformer.parse_phone(phone_str=cosignee['cell'], string_descr='cosignee cell', log_prefix=self.log_prefix),
            'PhoneAlt': self.pipeline.default_transformer.parse_phone(phone_str=cosignee['alternatePhone'], string_descr='cosignee alternatePhone', log_prefix=self.log_prefix),
            'PhoneOffice': self.pipeline.default_transformer.parse_phone(phone_str=cosignee['officePhone'], string_descr='cosignee officePhone', log_prefix=self.log_prefix),
            'PhoneExt': self.pipeline.default_transformer.parse_phone(phone_str=cosignee['extensionPhone'], string_descr='cosignee extensionPhone', log_prefix=self.log_prefix),
            # 'AltPhone': cosignee['alternatePhone'] if cosignee['alternatePhone'] != '' else None,
        }
        self.logger.info(f'{self.log_prefix}Parsed order level Cosignee Info successfully!')
        return fmt_cosignee







    def __parse_emails__(self, emails: str | None):
        emails = self.pipeline.default_transformer._handle_none_and_empty_strings_(string=emails, string_descr='Emails', log_prefix=self.log_prefix)
        if emails == None:
            return
        if ' ' not in emails.strip():
            return emails.strip().lower()
        spl_email = emails.strip().split(' ')
        self.logger.warning(f'{self.log_prefix}{len(spl_email)} email addresses found!')
        return ';'.join([e.lower() for e in spl_email])
        


    def __parse_service_location__(self, service_location: dict):
        if service_location == {}:
            self.logger.info(f'{self.log_prefix}No Service Location provided, returning None...')
            return None
        emails = self.__parse_emails__(emails=service_location['email'])
        fmt_service_location = {
            'ShipmentNbr': self.current_refs['ShipmentNbr'],
            'RyderID': self.current_refs['RyderID'],
            'LocationType': self.pipeline.default_transformer.clean_string(string=service_location['locationType'], string_descr='locationType', log_prefix=self.log_prefix),
            'HubCode': self.pipeline.default_transformer.clean_string(string=service_location['hubCode'], string_descr='hubCode', log_prefix=self.log_prefix),
            'Name': self.pipeline.default_transformer.clean_string(string=service_location['name'], string_descr='name', log_prefix=self.log_prefix),
            'Address1': self.pipeline.default_transformer.string_case_pascal(string=service_location['address1'], string_descr='address1',log_prefix=self.log_prefix),
            'Address2': self.pipeline.default_transformer.string_case_pascal(string=service_location['address2'], string_descr='address2',log_prefix=self.log_prefix),
            'City':  self.pipeline.default_transformer.string_case_pascal(string=service_location['city'], string_descr='city', log_prefix=self.log_prefix),
            'State': self.pipeline.default_transformer.clean_string(string=service_location['state'], string_descr='state', log_prefix=self.log_prefix),
            'Zip': self.pipeline.default_transformer.clean_string(string=service_location['zip'], string_descr='zip', log_prefix=self.log_prefix),
            'Phone': self.pipeline.default_transformer.clean_string(string=service_location['phone1'], string_descr='phone1', log_prefix=self.log_prefix),
            'Phone2': self.pipeline.default_transformer.clean_string(string=service_location['phone2'], string_descr='phone2', log_prefix=self.log_prefix),
            'Phone3': self.pipeline.default_transformer.clean_string(string=service_location['phone3'], string_descr='phone3', log_prefix=self.log_prefix),
            'Email': self.__parse_emails__(emails=emails),            
        }
        self.logger.info(f'{self.log_prefix}Parsed order level Service Location successfully!')
        return fmt_service_location
        
    def __parse_shipper_info__(self, shipper_info: dict):
        if shipper_info == {}:
            self.logger.info(f'{self.log_prefix}No Shipper Info provided, returning None...')
            return None
        fmt_shipper_info = {
            'ShipmentNbr': self.current_refs['ShipmentNbr'],
            'RyderID': self.current_refs['RyderID'],
            'Name': self.pipeline.default_transformer.string_case_pascal(string=shipper_info['shipperName'], string_descr='shipperName', log_prefix=self.log_prefix),
            'Address1': self.pipeline.default_transformer.string_case_pascal(string=shipper_info['shipperAddress1'], string_descr='shipperAddress1', log_prefix=self.log_prefix),
            'Address2': self.pipeline.default_transformer.string_case_pascal(string=shipper_info['shipperAddress2'], string_descr='shipperAddress2', log_prefix=self.log_prefix),
            'Address3': self.pipeline.default_transformer.string_case_pascal(string=shipper_info['shipperAddress3'], string_descr='shipperAddress3', log_prefix=self.log_prefix),
            'Address4': self.pipeline.default_transformer.string_case_pascal(string=shipper_info['shipperAddress4'], string_descr='shipperAddress4', log_prefix=self.log_prefix),
            'City':  self.pipeline.default_transformer.string_case_pascal(string=shipper_info['shipperCity'], string_descr='shipperCity', log_prefix=self.log_prefix),
            'State': self.pipeline.default_transformer.clean_string(string=shipper_info['shipperState'], string_descr='shipperState', log_prefix=self.log_prefix),
            'Zip': self.pipeline.default_transformer.clean_string(string=shipper_info['shipperZip'], string_descr='shipperZip', log_prefix=self.log_prefix),
            'Phone': self.pipeline.default_transformer.clean_string(string=shipper_info['shipperPhone'], string_descr='shipperPhone', log_prefix=self.log_prefix),
        }
        self.logger.info(f'{self.log_prefix}Parsed order level Shipper Info successfully!')
        return fmt_shipper_info


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




        