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


    def clean_string(self, string: str | None, log_prefix: str = ''):
        ''':class:`~DefaultTransformer`.:meth:`~clean_string` 
        ---
        
        Strips a string of any whitespace and returns None if the string is None or ''
            
        <hr>
        
        Parameters
        ---
        :param (*str | None*) `string`: String to clean (can be None)
        
            ### ***Optional***
        :param (*str = ''*) `log_prefix`: String to prepend to any logger outputs. Usually used when iterating, like `'keyvalue1, 1/150: '`, `'keyvalue2, 2/150: '` and so on 
        
        <hr>
        
        Returns
        ---
        :return `string` (_str_): Cleaned string value
        '''        
        bp = 'here'
        string = self._handle_none_and_empty_strings_(string=string, string_descr='str', log_prefix=log_prefix)
        if string == None:
            return None
        string = string.strip()
        return string

    def string_case_pascal(self, string: str | None, log_prefix: str = ''):
        string = self._handle_none_and_empty_strings_(string=string, string_descr='str', log_prefix=log_prefix)
        if string == None:
            return None
        if ' ' in string:
            self.logger.info(f'Space found in string...')
            strlist = string.split(' ')
            string = ' '.join([f'{s[0].upper()}{s[1].lower()}' for s in strlist])
            bp = 'here'
        else:
            string = f'{string[0].upper()}{string[1:].lower()}'
        return string

    
    def string_to_int(self, int_str: str | None, log_prefix: str = ''):
        ''':class:`~DefaultTransformer`.:meth:`~string_to_int`
        ---
        
        Given a string, attempt to convert it to an integer.
            
        <hr>
        
        Parameters
        ---
        :param (*str | None*) `int_str`: string that should be cast to int

            ### ***Optional***
        :param (*str = ''*) `log_prefix`: String to prepend to any logger outputs. Usually used when iterating, like `'keyvalue1, 1/150: '`, `'keyvalue2, 2/150: '` and so on 
        
        <hr>
        
        Returns
        ---
        :return `integer` (*int | None*): returns int value of int_str parameter if able to be parsed, otherwise returns None
        '''
        int_str = self._handle_none_and_empty_strings_(string=int_str, string_descr='string', log_prefix=log_prefix)
        if int_str == None:
            return None
        try:
            integer = int(int_str)
        except Exception as e:
            self.logger.error(f'{log_prefix}Error while converting string to integer! {e}')
            return None
        return integer

    
    def parse_phone(self, phone_str: str | None, log_prefix: str = ''):
        ''':class:`~DefaultTransformer`.:meth:`~parse_phone`
        ---
        
        Given an unformatted Phone Number string (or None value), remove non numeric characters.

        If ***phone_str*** value is None, empty or contains whitespace, will return None
            
        <hr>
        
        Parameters
        ---
        :param (*str | None*) `phone_str`: Phone Number string to parse.

            ### ***Optional***
        :param (*str = ''*) `log_prefix`: String to prepend to any logger outputs. Usually used when iterating, like `'keyvalue1, 1/150: '`, `'keyvalue2, 2/150: '` and so on 
        
        <hr>
        
        Returns
        ---
        :return `variablename` (_type_): _description_
        '''
        phone_str = self._handle_none_and_empty_strings_(string=phone_str, string_descr='Phone', log_prefix=log_prefix)
        if phone_str == None or phone_str.strip() == '':
            return None
        phone_fmt = phone_str.replace('-', '').replace('(', '').replace(')', '').replace('+1', '').replace(' ', '').strip()
        if len(phone_fmt) != 10:
            copy_phone_fmt = phone_fmt
            self.logger.warning(f'{log_prefix}Unconventional Phone number length!')
            if phone_fmt[0] == '+':
                phone_fmt = copy_phone_fmt[-10:]
                country_code = copy_phone_fmt[:-10]
            else:
                self.logger.error(f"{log_prefix}Phone doesn't begin with '+', returning None...")
                return None
        return phone_fmt


    def parse_date_str(self, date_str: str | None, tries: int, format: str = '%Y-%m-%dT%H:%M:%S.%fZ', offset: bool = False, log_prefix: str = ''):
        self.logger.info(f'{log_prefix}Date string provided: {date_str}, format provided: {format}. {'No offset' if not offset else 'Offset'}')
        date_str = self._handle_none_and_empty_strings_(string=date_str, string_descr='Date', additional_conditions=tries>=5, log_prefix=log_prefix, additional_log_str='string is blank or fifth try has been exceeded, returning None...')
        if date_str == None:            
            return None        
        offset_hrs = 0
        offset_hr_str = ''
        if offset == True:
            offset_hr_str = date_str[-6:]
            offset_hrs = int(date_str[-6:-3]) * -1
            date_str = date_str[:-6]
            bp = 'here'
        try:
            date = datetime.strptime(date_str, format) + timedelta(hours=offset_hrs)
        except ValueError as e:
            self.logger.warning(f"{log_prefix}Couldn't parse `{date_str}` in the format provided ({format}), trying backup format...")
            tries += 1
            try:
                date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
            except ValueError as e:
                self.logger.warning(f"{log_prefix}Couldn't parse date again...Appending Z and trying again as `{date_str}Z{offset_hr_str}`...")
                tries += 1
                date = self.parse_date_str(date_str=f'{date_str}Z{offset_hr_str}', tries=tries, offset=offset_hr_str!='', log_prefix=log_prefix)
        self.logger.info(f'{log_prefix}Parsed date successfully!')
        return date



    def _handle_none_and_empty_strings_(self, string: str | None, string_descr: str, additional_conditions: bool = True, log_prefix: str = '', additional_log_str: str = ''):
        ''':class:`~DefaultTransformer`.:meth:`~_handle_none_and_empty_strings_`
        ---
        
        Instead of duplicating  lines to handle None/empty strings in each method, do so here
        
        Parameters
        ---
        :param (*str | None*) `string`: string to check
        :param (*str*) `string_descr`: Description of string to use in log output

            ### ***Optional***
        :param (*bool = True*) `additional_conditions`: If additional conditions need to be met, pass them here. ***Default value is `True`***, *meaning if nothing is passed, method will ex as normal*
        :param (*str = ''*) `log_prefix`: String to prepend to any logger outputs. Usually used when iterating, like `'keyvalue1, 1/150: '`, `'keyvalue2, 2/150: '` and so on 
        :param (*str = ''*) `additional_log_str`: Instead of the default log output, send your own if you want to be appended after the log_prefix & string_descr
        
        <hr>
        
        Returns
        ---
        :return `variablename` (str): test

        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)

         ### _______replace_me_______

         ### :class:`~integration_platform.transform.default_transformer.DefaultTransformer`.:meth:`~integration_platform.transform.default_transformer.DefaultTransformer.parse_phone`

         ### :class:`~integration_platform.transform.default_transformer.DefaultTransformer`.:meth:`~integration_platform.transform.default_transformer.DefaultTransformer.parse_date_str`
            
         ### _______replace_me_______
        '''
        if string == None or string.strip() == '' or not additional_conditions:
            # self.logger.error(f'{log_prefix}{string_descr} {'value is blank, returning None...' if additional_log_str == '' else additional_log_str}')
            return None
        return string.strip()
