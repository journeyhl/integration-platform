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
        self.tracking_nbr = tracking_nbr
        rlm_order_nbr= order_info['orderNumber']
        references = order_info['orderReferences']
        current_status = order_info['currentOrderStatus']
        events = order_info['mileStoneEvents']
        #history only
        consignee_info = order_info.get('consigneeInfo') or {}
        service_location = order_info.get('serviceLocation') or {}
        shipper_info = order_info.get('shipperInfo') or {}


        fmt_references = self.__parse_references__(references=references)
        fmt_current_status = self.__parse_event__(event=current_status, event_nbr=current_status['sequence'], refs=fmt_references)
        fmt_events = [self.__parse_event__(event=event, event_nbr=i+1, refs=fmt_references) for i, event in enumerate(events)]
        fmt_cosignee = self._parse_cosignee_info_(cosignee=consignee_info)
        fmt_service_location = self.__parse_service_location__(service_location=service_location)
        fmt_shipper = self.__parse_shipper_info__(shipper_info=shipper_info)

        bp = 'here'




        

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
        return refs

    def __parse_event__(self, event: dict, event_nbr: int, refs: dict):
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
        :param (*dict*) `refs`: Formatted reference number dict
        
        <hr>
        
        Returns
        ---
        :return `fmt_event` (*dict*): Formatted dictionary of event/current status data.
        '''        
        fmt_event = {
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
            'Name': cosignee['name'],
            'Address1': self.pipeline.default_transformer.clean_string(string=cosignee['address1']),
            'Address2': self.pipeline.default_transformer.clean_string(string=cosignee['address2']),
            'Address3': self.pipeline.default_transformer.clean_string(string=cosignee['address3']),
            'Address4': self.pipeline.default_transformer.clean_string(string=cosignee['address4']),
            'City': cosignee['city'],
            'State': cosignee['state'],
            'Zip': cosignee['zip'],
            'Email': cosignee['email'] if cosignee['email'] != '' else None,
            'PhonePrimary': self.pipeline.default_transformer.parse_phone(phone_str=cosignee['primaryContact'], log_prefix=self.log_prefix),
            'PhoneCell': self.pipeline.default_transformer.parse_phone(phone_str=cosignee['cell'], log_prefix=self.log_prefix),
            'PhoneAlt': self.pipeline.default_transformer.parse_phone(phone_str=cosignee['alternatePhone'], log_prefix=self.log_prefix),
            'PhoneOffice': self.pipeline.default_transformer.parse_phone(phone_str=cosignee['officePhone'], log_prefix=self.log_prefix),
            'PhoneExt': self.pipeline.default_transformer.parse_phone(phone_str=cosignee['extensionPhone'], log_prefix=self.log_prefix),
            # 'AltPhone': cosignee['alternatePhone'] if cosignee['alternatePhone'] != '' else None,
        }
        return fmt_cosignee







    def __parse_emails__(self, emails: str | None):
        emails = self.pipeline.default_transformer._handle_none_and_empty_strings_(string=emails, string_descr='Emails', log_prefix=self.log_prefix)
        if emails == None:
            return
        if ' ' not in emails.strip():
            return emails.strip().lower()
        spl_email = emails.strip().split(' ')
        self.logger.warning(f'{len(spl_email)} email addresses found!')
        return ';'.join([e.lower() for e in spl_email])
        


    def __parse_service_location__(self, service_location: dict):
        if service_location == {}:
            self.logger.info(f'No Service Location provided, returning None...')
            return None
        emails = self.__parse_emails__(emails=service_location['email'])
        fmt_service_location = {
            'LocationType': self.pipeline.default_transformer.clean_string(string=service_location['locationType'], log_prefix=self.log_prefix),
            'HubCode': self.pipeline.default_transformer.clean_string(string=service_location['hubCode'], log_prefix=self.log_prefix),
            'Name': self.pipeline.default_transformer.clean_string(string=service_location['name'], log_prefix=self.log_prefix),
            'Address1': self.pipeline.default_transformer.clean_string(string=service_location['address1'], log_prefix=self.log_prefix),
            'Address2': self.pipeline.default_transformer.clean_string(string=service_location['address2'], log_prefix=self.log_prefix),
            'City':  self.pipeline.default_transformer.string_case_pascal(string=service_location['city'], log_prefix=self.log_prefix),
            'State': self.pipeline.default_transformer.clean_string(string=service_location['state'], log_prefix=self.log_prefix),
            'Zip': self.pipeline.default_transformer.clean_string(string=service_location['zip'], log_prefix=self.log_prefix),
            'Phone': self.pipeline.default_transformer.clean_string(string=service_location['phone1'], log_prefix=self.log_prefix),
            'Phone2': self.pipeline.default_transformer.clean_string(string=service_location['phone2'], log_prefix=self.log_prefix),
            'Phone3': self.pipeline.default_transformer.clean_string(string=service_location['phone3'], log_prefix=self.log_prefix),
            'Email': self.__parse_emails__(emails=emails),            
        }
        bp = 'here'
        return fmt_service_location
        
    def __parse_shipper_info__(self, shipper_info: dict):
        if shipper_info == {}:
            self.logger.info(f'No Shipper Info provided, returning None...')
            return None
        fmt_shipper_info = {
            'Name': self.pipeline.default_transformer.clean_string(string=shipper_info['shipperName'], log_prefix=self.log_prefix),
            'Address1': self.pipeline.default_transformer.clean_string(string=shipper_info['shipperAddress1'], log_prefix=self.log_prefix),
            'Address2': self.pipeline.default_transformer.clean_string(string=shipper_info['shipperAddress2'], log_prefix=self.log_prefix),
            'Address3': self.pipeline.default_transformer.clean_string(string=shipper_info['shipperAddress3'], log_prefix=self.log_prefix),
            'Address4': self.pipeline.default_transformer.clean_string(string=shipper_info['shipperAddress4'], log_prefix=self.log_prefix),
            'City':  self.pipeline.default_transformer.string_case_pascal(string=shipper_info['shipperCity'], log_prefix=self.log_prefix),
            'State': self.pipeline.default_transformer.clean_string(string=shipper_info['shipperState'], log_prefix=self.log_prefix),
            'Zip': self.pipeline.default_transformer.clean_string(string=shipper_info['shipperZip'], log_prefix=self.log_prefix),
            'Phone': self.pipeline.default_transformer.clean_string(string=shipper_info['shipperPhone'], log_prefix=self.log_prefix),         
        }
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




        