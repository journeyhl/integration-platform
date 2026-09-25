
from __future__ import annotations
from typing import TYPE_CHECKING, Literal
if TYPE_CHECKING:
    from integration_platform.connectors.rmi_api import RMIAPI
import logging
import requests
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from requests import Response
import polars as pl

class RMIAPIHelper:
    def __init__(self, rmi_api: RMIAPI) -> None:
        self.rmi = rmi_api
        if type(rmi_api.pipeline) == str:
            self.logger = logging.getLogger(f'{rmi_api.pipeline}.RMIAPIHelper')
        else:
            self.logger = logging.getLogger(f'{rmi_api.pipeline.pipeline_name}.RMIAPIHelper')        
        pass
    

    #MARK: parse_inventory
    def parse_inventory(self, response: Response, url: str = 'RMIAPI') -> list:
        ''':class:`~integration_platform.helpers.rmi_api_helper.RMIAPIHelper`.:meth:`~integration_platform.helpers.rmi_api_helper.RMIAPIHelper.parse_inventory`
        ---
        
        Given a response from the RMIAPI when hitting an inventory related endpoint, return the inventory data as a list
        
        Parameters
        ---
        :param (*Response*) `response`: Response from RMI api
        :param (*str*) `url`: Full url request was sent to. *Not required*
                
        Returns
        ---
        :return `inventory_response` (list): inventory data from RMIAPI as a list
        
        <hr>
        
        ## Upstream Calls 

         ### :class:`~integration_platform.connectors.rmi_api.RMIAPI`.:meth:`~integration_platform.connectors.rmi_api.RMIAPI.get_inventory_data`
            
        '''        
        bp = 'here'
        try:
            jresponse = response.json()
            inventory_response = jresponse['inventory']
            return inventory_response
        except Exception as e:
            self.logger.error(f"Couldn't parse response from {url}! {e}")
            return []


    #MARK: parse_auth
    def parse_auth(self, response: Response, url: str):
        
        ''':class:`~integration_platform.helpers.rmi_api_helper.RMIAPIHelper`.:meth:`~integration_platform.helpers.rmi_api_helper.RMIAPIHelper.parse_auth`
        ---
        
        After sending an authorization request to RMIAPI, parse the response and return the token value to :class:`~integration_platform.connectors.rmi_api.RMIAPI`.:attr:`~integration_platform.connectors.rmi_api.RMIAPI.token`
        
        Parameters
        ---
        :param (*Response*) `response`: response from RMIAPI after sending a request to authenticate
        :param (*str*) `url`: the full url of the endpoint we sent the request to
                
        Returns
        ---
        :return `token` (_str_): Token used in headers sent with each request to RMI API

        <hr>
        
        ## Upstream Calls 
         
         ### :class:`~integration_platform.connectors.rmi_api.RMIAPI`.:meth:`~integration_platform.connectors.rmi_api.RMIAPI._auth_`
        '''        
        try:            
            jresponse = response.json()
            token = jresponse['token']
            self.logger.info('RMI API is online and authenticated')
            return token
        except Exception as e:
            self.logger.critical(f"Couldn't login to RMI API at {url}! {e}")
            raise


        

    #MARK: format_headers
    def format_headers(self):
        ''':class:`~integration_platform.helpers.rmi_api_helper.RMIAPIHelper`.:meth:`~integration_platform.helpers.rmi_api_helper.RMIAPIHelper.format_headers`
        ---
        
        Formats headers to send with RMI API request
        
        Returns
        ---
        :return `headers` (dict): headers dict

        <hr>
        
        ## Upstream Calls 

         ### :class:`~integration_platform.connectors.rmi_api.RMIAPI`.:meth:`~integration_platform.connectors.rmi_api.RMIAPI._auth_`
        '''        
        headers = {
            **self.rmi.headers, 
            "Accept": "application/json",
            "Content-Type": "application/json",
            "authorization": f"Bearer {self.rmi.token}",
            "User-Agent": "axios/1.12.2",
            "Accept-Encoding": "gzip, compress, deflate, br",
        }
        return headers
