from integration_platform.config.settings import REDSTAG
import requests
import logging
import time

class RedStagAPI:
    def __init__(self, pipeline):
        '''`init`(self, pipeline: *Pipeline | str*)
        ---
        <hr>
        
        Initializes RedStagAPI connector and Authenticates
            
        <hr>
        
        Parameters
        ---
        :param (*Pipeline | str*) `pipeline`: Pipeline the connector belongs to
        
        <hr>
        
        Sets
        ---
        >>> self.logger = logging.getLogger(f'{pipeline.pipeline_name}.redstag_api')
        >>> self.logger = logging.getLogger(f'{pipeline.pipeline_name}.redstag_api')
        >>> self.base_uri = 'https://wms.redstagfulfillment.com/api/jsonrpc'
        >>> self.auth_type = 'Token'
        >>> self.username = REDSTAG['username']
        >>> self.password = REDSTAG['password']
        >>> self.headers = {
        "content-type": "application/json",
        "accept": "application/json"
        }
        >>> self.session = requests.Session()
        >>> self._auth() #Logs into RedStag API

        **self._auth** Authenticates using creds from :data:`~config.settings.REDSTAG`
        '''
        self.pipeline = pipeline
        if type(pipeline) == str:
            self.logger = logging.getLogger(f'{pipeline}.RedStagAPI')
        else:
            self.logger = logging.getLogger(f'{pipeline.pipeline_name}.RedStagAPI')
        self.base_uri = 'https://wms.redstagfulfillment.com/api/jsonrpc'
        self.auth_type = 'Token'
        self.username = REDSTAG['username']
        self.password = REDSTAG['password']
        self.headers = {
        "content-type": "application/json",
        "accept": "application/json"
        }
        self.session = requests.Session()
        self._auth()
        pass



    def _auth(self):
        '''`_auth`(self)
        ===
        <hr>
        
        Logins into RedStag's API. If response, gets a token and sets **self.token** 
        '''
        payload = {
            "jsonrpc" : 2.0,
            "id" : "2020",
            "method" : "login",
            "params" : [
                self.username,
                self.password
            ]
        }
        try:
            response = self.session.post(
                url = self.base_uri,
                headers = self.headers,
                json = payload
            )
            json_response = response.json()
            self.id = json_response['id']
            self.jsonrpc = json_response['jsonrpc']
            self.token = json_response['result']
            self.logger.info('RedStag API is online. Logged into RedStag and authenticated successfully')
        except:
            self.logger.critical(f'Could not login to RedStag API!')
            raise
        bp = 'here'


    def target_api(self, payload_target: list, operation: str, log_prefix: str = ''):
        ''':class:`~RedStagAPI`.:meth:`~target_api` (self, payload_target: *list*, operation: *str*, log_prefix: *str = ''*):
        ---
        <hr>

        Consolidates requests for all operation types within one method for RedStag
        
        ### Upstream Calls 
         #### :class:`~integration_platform.load.load_redstag_send.Load`.:meth:`~integration_platform.load.load_redstag_send.Load.send_shipments`
            - Sends new shipment to RedStag
         #### :class:`~integration_platform.pipelines.redstag_inventory.RedStagInventory`.:meth:`~integration_platform.pipelines.redstag_inventory.RedStagInventory.extract`
            - Pulls inventory details from RedStag

         #### :class:`~integration_platform.transform.redstag_send.Transform`.:meth:`~integration_platform.transform.redstag_send.Transform.transform_lookup_payload`
            - Searches order in RedStag's system

         #### _______replace_me_______
  
        <hr>
        
        Parameters
        ---
        :param (*list*) `payload_target`: list formatted for RedStag's API
        :param (*str*) `operation`: description of what the function will be doing during execution. Used for logging
        :param (*str*) `log_prefix`: ***Not Req***. String to prefix all logs. *default = ''*
        
        <hr>
        
        Returns
        ---
        :return `json_response` (dict): .json() formatted response from Redstag api

        <hr>

        # Examples

        - ### payload_target:

        >>> "order.create",
            [
                "journeyhealth",
                [
                    {
                        "sku": "08918LFT",
                        "qty": 1,
                        "item_ref": "[2]",
                        "shipVia": "GROUND"
                    }
                ],
                {
                    "lastname": "Carolyn Buden",
                    "street1": "65 Stonebridge way",
                    "city": "berlin",
                    "region": "CT",
                    "postcode": "06037-2517",
                    "country": "US",
                    "telephone": "8605059556"
                },
                {
                    "unique_id": "078828",
                    "shipping_method": "cheapest_ALL",
                    "other_shiping_options": [
                        {
                            "reference_numbers": {}
                        }
                    ]
                }
            ]

        '''
        time.sleep(1)
        payload = {
            "jsonrpc": self.jsonrpc,
            "id": self.id,
            "method": "call",
            "params": [
                self.token,
                *payload_target
            ]
        }
        try:
            response = self.session.post(
                url = self.base_uri,
                headers = self.headers,
                json = payload
            )
            json_response = response.json()
            self.logger.info(f'{log_prefix}Operation: {operation}: Response parsed successfully')
            if json_response.get('result'):
                return json_response['result']
            return json_response
        except Exception as e:
            self.logger.error(f'{log_prefix}Operation: {operation}: Failed to get a response from RedStag API')
            raise

        



