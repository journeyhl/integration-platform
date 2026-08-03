
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
    


    def parse_inventory(self, response: Response, url: str = 'RMIAPI') -> list:
        ''':class:`~RMIAPIHelper`.:meth:`~parse_inventory` (self, response: *Response*, url: *str = 'RMIAPI'*):
        ---
        <hr>
        
        Given a response from the RMIAPI when hitting an inventory related endpoint, return the inventory data as a list
        
        ### Upstream Calls 
         #### :class:`~integration_platform.connectors.rmi_api.RMIAPI`.:meth:`~integration_platform.connectors.rmi_api.RMIAPI.get_inventory_data`
            
        <hr>
        
        Parameters
        ---
        :param (*Response*) `response`: Response from RMI api
        :param (*str*) `url`: Full url request was sent to. *Not required*
        
        <hr>
        
        Returns
        ---
        :return `inventory_response` (list): inventory data from RMIAPI as a list
        '''        
        bp = 'here'
        try:
            jresponse = response.json()
            inventory_response = jresponse['inventory']
            return inventory_response
        except Exception as e:
            self.logger.error(f"Couldn't parse response from {url}! {e}")
            return []


    def parse_auth(self, response: Response, url: str):
        ''':class:`~RMIAPIHelper`.:meth:`~parse_auth` (self, response: *Response*, url: *str*):
        ---
        <hr>
        
        After sending an authorization request to RMIAPI, parse the response and return the token value to :class:`~integration_platform.connectors.rmi_api.RMIAPI`.:attr:`~integration_platform.connectors.rmi_api.RMIAPI.token`
        
        ### Upstream Calls 
         #### :class:`~integration_platform.connectors.rmi_api.RMIAPI`.:meth:`~integration_platform.connectors.rmi_api.RMIAPI._auth_`
            
        <hr>
        
        Parameters
        ---
        :param (*Response*) `response`: response from RMIAPI after sending a request to authenticate
        :param (*str*) `url`: the full url of the endpoint we sent the request to
        
        <hr>
        
        Returns
        ---
        :return `token` (_str_): Token used in headers sent with each request to RMI API
        '''        
        try:            
            jresponse = response.json()
            token = jresponse['token']
            self.logger.info('RMI API is online and authenticated')
            return token
        except Exception as e:
            self.logger.critical(f"Couldn't login to RMI API at {url}! {e}")
            raise


        

    def format_headers(self):
        ''':class:`~RMIAPIHelper`.:meth:`~format_headers` (self):
        ---
        <hr>
        
        Formats headers to send with RMI API request
        
        ### Upstream Calls 
         #### :class:`~integration_platform.connectors.rmi_api.RMIAPI`.:meth:`~integration_platform.connectors.rmi_api.RMIAPI._auth_`
            
        <hr>
        
        Parameters
        ---
        
        <hr>
        
        Returns
        ---
        :return `variablename` (_type_): _description_
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
