import requests
import logging
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from integration_platform.config.settings import RMI
from integration_platform.helpers.rmi_api_helper import RMIAPIHelper
import urllib3

class RMIAPI():

    def __init__(self, pipeline):
        """`init`(self, pipeline: *Pipeline | str*)
        ---
        <hr>
        
        Initializes RMIAPI connector and Authenticates
            
        <hr>
        
        Parameters
        ---
        :param (*Pipeline | str*) `pipeline`: Pipeline the connector belongs to
        
        <hr>
        
        Sets
        ---
        >>> self.logger = logging.getLogger(f'{pipeline.pipeline_name}.rmi_api')
        >>> self.base_uri = 'https://api.backtracksrl.com/'
        >>> self.auth_type = 'Token'
        >>> self.headers = {
            'Content-Type': 'application/json', 
            'ident': '64A648DD-E186-42E1-8A46-23D76A401FF0'
        }

        >>> self.username = RMI['username']
        >>> self.password = RMI['password']
        >>> self.session = requests.Session()
        >>> self._auth()
        
        **self._auth** Authenticates using creds from :data:`~config.settings.RMI`
        """
        self.pipeline = pipeline
        if type(pipeline) == str:
            self.logger = logging.getLogger(f'{pipeline}.RMIAPI')
        else:
            self.logger = logging.getLogger(f'{pipeline.pipeline_name}.RMIAPI')
        self.helper = RMIAPIHelper(self)
        self.base_uri = 'https://api.backtracksrl.com/'
        self.auth_type = 'Token'
        self.headers = {
            'Content-Type': 'application/json', 
            'ident': '64A648DD-E186-42E1-8A46-23D76A401FF0'
        }

        self.username = RMI['username']
        self.password = RMI['password']
        self.session = requests.Session()
        self.session.verify = False
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self._set_endpoints_()
        self._auth_()
        pass



    def _set_endpoints_(self):
        ''':class:`~RMIAPI`.:meth:`~_set_endpoints_` (self, ):
        ---
        <hr>
        
        When :class:`~integration_platform.connectors.rmi_api.RMIAPI` is initialized, this method sets endpoints used by pipelines
        
        ### Upstream Calls 
         #### :class:`~integration_platform.connectors.rmi_api.RMIAPI`.:meth:`~integration_platform.connectors.rmi_api.RMIAPI.__init__`
            
        <hr>
        
        Sets
        ---
        :class:`~integration_platform.connectors.rmi_api.RMIAPI`.:attr:`~integration_platform.connectors.rmi_api.RMIAPI.ep_auth`
        :class:`~integration_platform.connectors.rmi_api.RMIAPI`.:attr:`~integration_platform.connectors.rmi_api.RMIAPI.ep_inventory_by_facility`
        :class:`~integration_platform.connectors.rmi_api.RMIAPI`.:attr:`~integration_platform.connectors.rmi_api.RMIAPI.ep_inventory_by_location`
        :class:`~integration_platform.connectors.rmi_api.RMIAPI`.:attr:`~integration_platform.connectors.rmi_api.RMIAPI.ep_inventory_with_serials`
        '''        
        self.ep_auth = f'{self.base_uri}Auth/Login'
        self.ep_inventory_by_facility = f'{self.base_uri}api/InventoryByFacility'
        self.ep_inventory_by_location = f'{self.base_uri}api/InventoryByLocation'
        self.ep_inventory_with_serials = f'{self.base_uri}api/InventoryWithSerials'
        
    def _auth_(self):
        
        ''':class:`~RMIAPI`.:meth:`~_auth_` (self):
        ---
        <hr>
        
        Authenticates and logs into RMI API. Sets :class:`~integration_platform.connectors.rmi_api.RMIAPI`.:attr:`~integration_platform.connectors.rmi_api.RMIAPI.token` and :class:`~integration_platform.connectors.rmi_api.RMIAPI`.:attr:`~integration_platform.connectors.rmi_api.RMIAPI.headers`
        
        ### Downstream Calls 
         #### :class:`~integration_platform.helpers.rmi_api_helper.RMIAPIHelper`.:meth:`~integration_platform.helpers.rmi_api_helper.RMIAPIHelper.parse_auth`
            - Parses response from RMI API following an authentication request
         #### :class:`~integration_platform.helpers.rmi_api_helper.RMIAPIHelper`.:meth:`~integration_platform.helpers.rmi_api_helper.RMIAPIHelper.format_headers`
            - Formats connector wide headers

        ### Upstream Calls 
         #### :class:`~integration_platform.connectors.rmi_api.RMIAPI`.:meth:`~integration_platform.connectors.rmi_api.RMIAPI.__init__`
            - Called at connector initialization
            
        <hr>
        
        Sets
        ---
         - #### :class:`~integration_platform.connectors.rmi_api.RMIAPI`.:attr:`~integration_platform.connectors.rmi_api.RMIAPI.token`
            - Returned by :class:`~integration_platform.helpers.rmi_api_helper.RMIAPIHelper`.:meth:`~integration_platform.helpers.rmi_api_helper.RMIAPIHelper.parse_auth`
         - #### :class:`~integration_platform.connectors.rmi_api.RMIAPI`.:attr:`~integration_platform.connectors.rmi_api.RMIAPI.headers`
            - Returned by :class:`~integration_platform.helpers.rmi_api_helper.RMIAPIHelper`.:meth:`~integration_platform.helpers.rmi_api_helper.RMIAPIHelper.format_headers`
        '''        
        body = {
            "name": self.username,
            "password": self.password 
        }
        response = self.session.post(
            url = self.ep_auth,
            headers = self.headers,
            json=body
        )   
        self.token = self.helper.parse_auth(response=response, url=self.ep_auth)
        self.headers = self.helper.format_headers()
        pass
        

    def target_api(self, endpoint: str, payload: list, lookback_window_days: int = 21):
        bp = 'here'
        url = f'{self.base_uri}api/{endpoint}'
        from_date = datetime.today() - timedelta(days=lookback_window_days)
        from_date = from_date.date().strftime('%Y-%m-%dT%H:%M:%SZ')
        to_date = datetime.now(ZoneInfo('America/New_York')).strftime('%Y-%m-%dT%H:%M:%SZ')
        # headers = self.format_headers()
        body = {
            payload[0]: from_date,
            payload[1]: to_date
        }
        try:
            response = self.session.post(
                url = url,
                headers = self.headers,
                json = body
            )
            json_response = json.loads(response.text)
            bp = 'here'
            return json_response
        except Exception as e:
            bp = 'here'



    def get_rma(self, rma_number):
        url = f'{self.base_uri}api/RMA'
        from_date = datetime.today() - timedelta(days=180)
        from_date = from_date.date().strftime('%Y-%m-%dT%H:%M:%SZ')
        to_date = datetime.now(ZoneInfo('America/New_York')).strftime('%Y-%m-%dT%H:%M:%SZ')
        body = {
            "fromDate": from_date,
            "toDate": to_date
        }
        try:
            response = self.session.post(
                url = url,
                headers = self.headers,
                json = body,
                params={'RMANumber': f'{rma_number}'}
            )
            json_response = json.loads(response.text)
            if json_response == {'message': 'Bad Request', 'status': 400}:
                self.logger.error(f'{json_response['status']} ERROR: {json_response['message']}')
            bp = 'here'
            return json_response
        except Exception as e:
            bp = 'here'





    def get_inventory_data(self, url: str) -> list:
        ''':class:`~RMIAPI`.:meth:`~get_inventory_data` (self, url: *str*, ):
        ---
        <hr>
        
        Given a url, retrieves inventory data 
        
        ### Downstream Calls 
         #### :class:`~integration_platform.helpers.rmi_api_helper.RMIAPIHelper`.:meth:`~integration_platform.helpers.rmi_api_helper.RMIAPIHelper.parse_inventory`
            - Returns inventory data from RMI as a list
        
        ### Upstream Calls 
         #### :class:`~integration_platform.pipelines.rmi_inventory.RMIInventory`.:meth:`~integration_platform.pipelines.rmi_inventory.RMIInventory.extract`
            - Called three times during extraction step of RMIInventory pipeline
            
        <hr>
        
        Parameters
        ---
        :param (*str*) `url`: Full url of endpoint to hit RMIAPI at
        
        <hr>
        
        Returns
        ---
        :return `parsed_response` (_list_): Inventory data returned from RMI as a list
        '''
        self.logger.info(f'Hitting {url}')
        response = self.session.post(url=url, headers=self.headers)
        parsed_response = self.helper.parse_inventory(response=response, url=url)
        self.logger.info(f'{len(parsed_response)} rows returned from {url}')
        return parsed_response