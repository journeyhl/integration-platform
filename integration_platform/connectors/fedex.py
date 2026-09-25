import logging
from integration_platform.config.settings import FEDEX
from integration_platform.helpers.fedex_helper import FedexHelper
from datetime import datetime, timedelta
import requests
from typing import Literal

class Fedex:
    def __init__(self, pipeline):
        self.pipeline = pipeline
        if isinstance(pipeline, str):
            self.logger = logging.getLogger(f'{pipeline}.FedexAPI')
        else:
            self.logger = logging.getLogger(f'{pipeline.pipeline_name}.CriteoAPI')
        self.helper = FedexHelper(self)
        self.ep_rates = 'https://apis.fedex.com/rate/v1/rates/quotes'
        self._authenticate_()



    def _authenticate_(self):
        self.account_id = FEDEX['account_id']
        response = requests.post(
            url='https://apis.fedex.com/oauth/token',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data={
                'grant_type': 'client_credentials',
                'client_id': FEDEX['client_id'],
                'client_secret': FEDEX['client_secret']
            }
        )
    
        tokenData = response.json()
        token = tokenData['access_token']
        self.tokenExpiry = datetime.now() + timedelta(seconds=tokenData.get('expires_in', 3600) - 60)
        self.headers ={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        self.logger.info(f'FedexAPI online')
        bp = 'here'


    #MARK: get_rate
    def get_rate(self, from_zip: str, to_zip: str):
        parsed_response = self._get_rate_helper_(from_zip=from_zip, to_zip=to_zip)
        bp = 'here'
        return parsed_response

    #MARK: get_return_rate
    def get_return_rate(self, customer_zip: str, jhl_wh_zip: Literal['60089','37874','84116','23230',]):
        parsed_response = self._get_rate_helper_(from_zip=customer_zip, to_zip=jhl_wh_zip)
        bp = 'here'
        return parsed_response

    #MARK: get_jhlrateshopper_rate
    def get_jhlrateshopper_rate(self, jhl_wh_zip: Literal['37874', '84116'], customer_zip: str):
        ''':class:`~integration_platform.connectors.fedex.Fedex`.:meth:`~integration_platform.connectors.fedex.Fedex.get_jhlrateshopper_rate`
        ---
        
        Called when getting the freight rate for a package from a JHL warehouse (Redstag Sweetwater or Salt Lake City) to a Customer's zipcode
        
        Parameters
        ---
        :param (*Literal['37874', '84116']*) `jhl_wh_zip`: One of the zipcode values for Redstag's Sweetwater and Salt Lake City locations
        :param (*str*) `customer_zip`: The customer or recipient's zipcode
        
        Returns
        ---
        :return `parsed_response` (dict): Parsed freight rate response from FedEx
        
        <hr>
        
        ## Downstream Calls (Methods/Functions called)
        
         ### :class:`~integration_platform.connectors.fedex.Fedex`.:meth:`~integration_platform.connectors.fedex.Fedex._get_rate_helper_`
        '''        
        parsed_response = self._get_rate_helper_(from_zip=jhl_wh_zip, to_zip=customer_zip)
        bp = 'here'
        return parsed_response

    def _get_rate_helper_(self, from_zip, to_zip) -> dict:
        ''':class:`~integration_platform.connectors.fedex.Fedex`.:meth:`~integration_platform.connectors.fedex.Fedex._get_rate_helper_`
        ---
        
        Handles the API call to Fedex and parsing the response. Called from one of abstracted functions
        
        Parameters
        ---
        :param (*_type_*) `from_zip`: _description_
        :param (*_type_*) `to_zip`: _description_
        
                
           ### ***Optional***
        :param (*str = ''*) `log_prefix`: String to prepend to any logger outputs. Usually used when iterating, like `'keyvalue1, 1/150: '`, `'keyvalue2, 2/150: '` and so on 
        
        Returns
        ---
        :return `variablename` (dict): _description_
        
        <hr>
        
        Sets
        ---
        - #### ____replace_with_class_level_variable_pls____
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### _______replace_me_______
        
          - Description
        
         ### _______replace_me_______
           
          - Description
        
        ## Downstream Calls (Methods/Functions called)
        
         ### :class:`~integration_platform.helpers.fedex_helper.FedexHelper`.:meth:`~integration_platform.helpers.fedex_helper.FedexHelper.format_rate_payload`
        
          - Description
        
         ### :class:`~integration_platform.helpers.fedex_helper.FedexHelper`.:meth:`~integration_platform.helpers.fedex_helper.FedexHelper.parse_rate_response`
           
          - Description
        '''        
        payload = self.helper.format_rate_payload(from_zip=from_zip, to_zip='37874')
        response = requests.post(url=self.ep_rates, json=payload, headers=self.headers)
        parsed_response = self.helper.parse_rate_response(response=response)
        return parsed_response
