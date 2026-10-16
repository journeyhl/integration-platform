from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.ucmi_shopify import UCMI_ShopifyCustomers
import logging
import polars as pl
from datetime import datetime

class Transform:
    def __init__(self, pipeline: UCMI_ShopifyCustomers):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.Transform')
        self.def_transformer = self.pipeline.default_transformer
        pass

    def landing(self, data_extract):
        bp = 'here'
        self.total = len(data_extract)
        data_transformed = {
            'shop.Customers': [],
            'shop.CustomerOrders': [],
            'shop.CustomerAddresses': []
        }

        
        for i, customer in enumerate(data_extract):
            self.prefix = f'{i+1}/{self.total}: '
            self._format_header_(customer=customer)
            self._get_default_email_fields_(def_email=customer['defaultEmailAddress'])
            self._get_default_phone_number_(def_phone=customer['defaultPhoneNumber'])
            fmt_orders = self._get_orders_(orders=customer['orders'])
            fmt_addresses = self._get_addresses_(addresses=customer['addresses'])
            data_transformed['shop.Customers'].append(self.fmt_customer)
            data_transformed['shop.CustomerOrders'].extend(fmt_orders)
            data_transformed['shop.CustomerAddresses'].extend(fmt_addresses)
            # metafields = self._get_metafields_(metafields=customer['metafields'])
            bp = 'here'
        return data_transformed


    #region done
    def _format_header_(self, customer: dict):
        self.fmt_customer = {
            'CustomerID': customer['id'].replace('gid://shopify/Customer/', ''),
            'FirstName':   self.def_transformer.clean_string(customer['firstName']),
            'LastName':    self.def_transformer.clean_string(customer['lastName']),
            'Email': None,
            'EmailMarketingState': None,
            'PhoneNumber': None,
            'PhoneNumberFmt': None,
            'NumberOfOrders': self.def_transformer.string_to_int(int_str=customer['numberOfOrders']),
            'Tags': self.def_transformer.clean_string(string=','.join(customer['tags'])),
            'AmountSpent': self.def_transformer.string_to_float(float_str=(customer['amountSpent'] or {}).get('amount')),
            'Address': None,
            'Metafields': None,
            'Orders': None,
            'CreatedAt': self.def_transformer.parse_date_str(date_str=customer['createdAt'], tries=0, format='%Y-%m-%dT%H:%M:%SZ'),
            'LastChecked': self.pipeline.ts_extract
        }

    
    def _get_default_email_fields_(self, def_email):
        if not def_email:
            return None, None
        email = self.def_transformer.clean_string(string=def_email['emailAddress'])
        marketing_state = def_email.get('MarketingState')
        self.fmt_customer['Email'] = email
        self.fmt_customer['EmailMarketingState'] = marketing_state

    def _get_default_phone_number_(self, def_phone):
        if not def_phone:
            return None, None
        phone = def_phone['phoneNumber']
        phone_fmt = self.def_transformer.parse_phone(phone_str=phone)
        self.fmt_customer['PhoneNumber'] = phone
        self.fmt_customer['PhoneNumberFmt'] = phone_fmt
    
    #endregion

    def _get_orders_(self, orders: list) -> list:
        if not orders or orders == []:
            return []
        fmt_orders = [
            {
                'CustomerID': o['__parentId'].replace('gid://shopify/Customer/', ''),
                'OrderID': o['id'].replace('gid://shopify/Order/', ''),
                'ShopOrderNbr': o['name'],
                'CreatedAt': self.def_transformer.parse_date_str(date_str=o['createdAt'], tries=0, format='%Y-%m-%dT%H:%M:%SZ'),
                'Price': self.def_transformer.string_to_float(float_str=(o['totalPriceSet'].get('shopMoney') or {}).get('amount')),
                'LastChecked': self.pipeline.ts_extract
            } for o in orders
        ]
        fmt_orders.sort(key=lambda x: x['CreatedAt'])
        fmt_orders = [
            {
                **order,
                'CustomerOrderSeq': i+1
            } for i, order in enumerate(fmt_orders)
        ]
        return fmt_orders

    def _get_addresses_(self, addresses: list) -> list:
        if not addresses or addresses == []:
            return []
        new_addresses = {}
        addr_keys = ['address1', 'city', 'province', 'zip', 'country']
        if len(addresses) > 1:
            for addr in addresses:
                populated = [v for k, v in addr.items() if k in addr_keys and v]
                new_key = '-'.join(populated)
                if len(populated) > 1:
                    existing_values = [v.get('address1') for k, v in new_addresses.items()]
                    if not new_addresses.get(new_key) and addr['address1'] not in existing_values:
                        new_addresses[new_key] = addr
            if len(addresses) != len(new_addresses): self.logger.info(f'{self.prefix}Customer addresses trimmed from {len(addresses)} to {len(new_addresses)}')
        if len(new_addresses) >= 1:
            addresses = list(new_addresses.values())
        bp = 'here'

        fmt_addresses = [
            {
                'CustomerID': adr['__parentId'].replace('gid://shopify/Customer/', ''),
                'AddressID': adr['id'].replace('gid://shopify/MailingAddress/', '').replace('?model_name=CustomerAddress', ''),
                'Address1': self.def_transformer.clean_string(string=adr['address1']),
                'City': self.def_transformer.clean_string(string=adr['city']),
                'Province': self.def_transformer.clean_string(string=adr['province']),
                'Zip': self.def_transformer.clean_string(string=adr['zip']),
                'Country': self.def_transformer.clean_string(string=adr['country']),
                'LastChecked': self.pipeline.ts_extract
            } for adr in addresses
        ]
        bp = 'here'
        return fmt_addresses

    def _get_metafields_(self, metafields: list):
        if not metafields or metafields == []:
            return None
        bp = 'here'
        fmt_metafields = [
            {
                'CustomerID': mf['__parentId'].replace('gid://shopify/Customer/', ''),

            } for mf in metafields
        ]
        if len(metafields) > 1:
            bp = 'here'
        return fmt_metafields