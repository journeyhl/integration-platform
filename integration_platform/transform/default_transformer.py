import logging
import polars as pl
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo



class DefaultTransformer:
    def __init__(self, pipeline):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.DefaultTransformer')
        pass


    def clean_string(self, string: str | None):
        bp = 'here'
        if string == None or string.strip() == '':
            self.logger.info(f'str value is blank, returning None')
            return None
        string = string.strip()
        return string


    
    def string_to_int(self, int_str: str | None):
        ''':class:`~DefaultTransformer`.:meth:`~string_to_int` (self, int_str: *str | None*):
        ---
        <hr>
        
        Given a string, attempt to convert it to an integer.
            
        <hr>
        
        Parameters
        ---
        :param (*str | None*) `int_str`: string that should be cast to int
        
        <hr>
        
        Returns
        ---
        :return `integer` (*int | None*): returns int value of int_str parameter if able to be parsed, otherwise returns None
        '''
        if int_str == None or int_str.strip() == '':
            self.logger.warning(f"string value is blank, returning None...")
            return None
        try:
            integer = int(int_str)
        except Exception as e:
            self.logger.error(f'Error while converting string to integer! {e}')
            return None
        return integer

    
    def parse_phone(self, phone_str: str | None):
        ''':class:`~DefaultTransformer`.:meth:`~parse_phone` (self, phone_str: *str | None*, ):
        ---
        <hr>
        
        Given an unformatted Phone Number string (or None value), remove non numeric characters.

        If ***phone_str*** value is None, empty or contains whitespace, will return None
            
        <hr>
        
        Parameters
        ---
        :param (*str | None*) `phone_str`: Phone Number string to parse.
        
        <hr>
        
        Returns
        ---
        :return `variablename` (_type_): _description_
        '''
        if phone_str == None or phone_str.strip() == '':
            self.logger.warning(f"Phone value is blank, returning None...")
            return None
        phone_fmt = phone_str.replace('-', '').replace('(', '').replace(')', '').replace('+1', '').replace(' ', '').strip()
        if len(phone_fmt) != 10:
            copy_phone_fmt = phone_fmt
            self.logger.warning(f'Unconventional Phone number length!')
            if phone_fmt[0] == '+':
                phone_fmt = copy_phone_fmt[-10:]
                country_code = copy_phone_fmt[:-10]
            else:
                self.logger.error(f"Phone doesn't begin with '+', returning None...")
                return None
        return phone_fmt



    