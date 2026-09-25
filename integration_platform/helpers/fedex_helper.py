
from __future__ import annotations
from typing import TYPE_CHECKING, Literal
if TYPE_CHECKING:
    from integration_platform.connectors.fedex import Fedex
import logging
import requests
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from requests import Response
import polars as pl
from typing import Literal

class FedexHelper:
    def __init__(self, fedex: Fedex) -> None:
        self.fedex = fedex
        if type(fedex.pipeline) == str:
            self.logger = logging.getLogger(f'{fedex.pipeline}.FedexHelper')
        else:
            self.logger = logging.getLogger(f'{fedex.pipeline.pipeline_name}.FedexHelper')

        self.zips = {
            'RMI': '60089',
            'REDSTAGSWT': '37874',
            'REDSTAGSLC': '84116',
            'JHL': '23230',
        }
        pass

    #MARK: format_rate_payload
    def format_rate_payload(self, customer_zip: str, jhl_wh_zip: Literal['60089','37874','84116','23230',]):
        payload = {
            'accountNumber': {'value': self.fedex.account_id},
            'requestedShipment': {
                'shipper': {
                    'address': {
                        'postalCode': customer_zip,
                        'countryCode': 'US'
                    }
                },
                'recipient': {
                    'address': {
                        'postalCode': jhl_wh_zip,
                        'countryCode': 'US',
                        'residential': True
                    }
                },
                'pickupType': 'CONTACT_FEDEX_TO_SCHEDULE',
                'rateRequestType': ['LIST', 'ACCOUNT'],
                'requestedPackageLineItems': [{
                    'weight': {
                        'units': 'LB',
                        'value': 5
                    }
                }]
            }
        }
        return payload

    #MARK: parse_rate_response
    def parse_rate_response(self, response: requests.Response):
        try:
            jresponse = response.json()
        except Exception as e:
            self.logger.warning(f"Couldn't parse response from Fedex to dict!")
            return
        if self._check_rate_errors_(jresponse=jresponse):
            return
        rates = jresponse['output']['rateReplyDetails']
        parsed_rates = []
        for rate in rates:
            parsed_rate = self._parse_rate_details(rate=rate)
            parsed_rates.append(parsed_rate)
        bp = 'here'
        return jresponse

    #MARK: _check_rate_errors_
    def _check_rate_errors_(self, jresponse: dict) -> bool:
        ''':class:`~integration_platform.helpers.fedex_helper.FedexHelper`.:meth:`~integration_platform.helpers.fedex_helper.FedexHelper._check_rate_errors_`
        ---
        
        Checks response dict from Fedex to determine if they returned any errors, or if we are good to continue
        
        Parameters
        ---
        :param (*dict*) `jresponse`: Response from Fedex as dict
        
        Returns
        ---
        :return `errors` (bool): True if there are errors, false if not
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.helpers.fedex_helper.FedexHelper`.:meth:`~integration_platform.helpers.fedex_helper.FedexHelper.parse_rate_response`
        '''        
        errors = jresponse.get('errors')
        if errors:
            cnt = len(errors)
            self.logger.error(f"Error! {errors[0]['message'] if cnt == 1 else ','.join([e['message'] for e in errors]) if cnt > 1 else ''}")
            bp = 'here'
            return True
        self.logger.info(f'No errors found!')
        return False

    def _parse_rate_details(self, rate: dict):
        parsed_rate = {
            'ServiceType': rate['serviceType'],
            'ServiceName': rate['serviceName'],

        }

        for r in rate['ratedShipmentDetails']:
            parsed_rate[f'{r['rateType']}_TotalCharge'] = r['totalNetFedExCharge']
            parsed_rate[f'{r['rateType']}_TotalDiscounted'] = r['totalDiscounts']
            parsed_rate[f'{r['rateType']}_BillingWeight'] = r['shipmentRateDetail']['totalBillingWeight']['value']
            
        bp = 'here'
        return parsed_rate