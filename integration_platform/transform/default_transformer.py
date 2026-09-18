import logging
import polars as pl
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Literal


class DefaultTransformer:
    def __init__(self, pipeline):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.DefaultTransformer')
        pass


    #MARK: clean_string
    def clean_string(self, string: str | None, string_descr: str = '', log_prefix: str = ''):
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
        string = self._handle_none_and_empty_strings_(string=string, string_descr=string_descr, log_prefix=log_prefix)
        if string == None:
            return None
        string = string.strip()
        return string

    #MARK: string_case_pascal
    def string_case_pascal(self, string: str | None, string_descr: str= '', log_prefix: str = ''):
        ''':class:`~integration_platform.transform.default_transformer.DefaultTransformer`.:meth:`~integration_platform.transform.default_transformer.DefaultTransformer.string_case_pascal`
        ---
        
        Given a string value, normalize and convert to pascal case
        
        Parameters
        ---
        :param (*str | None*) `string`: _description_
        
                
           ### ***Optional***
        :param (*str = ''*) `log_prefix`: String to prepend to any logger outputs. Usually used when iterating, like `'keyvalue1, 1/150: '`, `'keyvalue2, 2/150: '` and so on 
        
        Returns
        ---
        :return `new_str` (str): _description_
        
        <hr>
        
        ## Downstream Calls (Methods/Functions called)
        
         ### :class:`~DefaultTransformer`.:meth:`~_handle_none_and_empty_strings_`
        '''
        string = self._handle_none_and_empty_strings_(string=string, string_descr=string_descr, log_prefix=log_prefix)
        if string == None:
            return None
        def split_by_character(check_str: str, split_char: str = ' '):
            new_str = ''
            if split_char == '-':
                bp = 'here'
            if split_char in check_str:
                strlist = check_str.split(split_char)
                for s in strlist:
                    if s in acronyms:
                        new_str += s
                    elif s.strip() != '':
                        new_str += f'{s[0].upper()}{'' if len(s) == 1 else s[1:].lower()}'       
            else:
                new_str += f'{check_str[0].upper()}{check_str[1:].lower()}' if check_str.lower() != 'id' else 'ID'
            return new_str
        new_str = split_by_character(check_str=string)
        bp = 'here'
        
        return new_str

    
    #MARK: string_to_int
    def string_to_int(self, int_str: str | None, str_descr: str = '', log_prefix: str = ''):
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
        int_str = self._handle_none_and_empty_strings_(string=int_str, string_descr=str_descr, log_prefix=log_prefix)
        if int_str == None:
            return None
        try:
            integer = int(int_str)
        except Exception as e:
            self.logger.error(f'{log_prefix}Error while converting string to integer! {e}')
            return None
        return integer

    
    #MARK: parse_phone
    def parse_phone(self, phone_str: str | None, string_descr: str = '',log_prefix: str = ''):
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

    #MARK: parse_date_str
    def parse_date_str(self, date_str: str | None, tries: int, format: str = '%Y-%m-%dT%H:%M:%S.%fZ', offset: bool = False, log_prefix: str = ''):
        # self.logger.info(f'{log_prefix}Date string provided: {date_str}, format provided: {format}. {'No offset' if not offset else 'Offset'}')
        date_str = self._handle_none_and_empty_strings_(string=date_str, string_descr='Date', additional_conditions=tries<5, log_prefix=log_prefix, additional_log_str='string is blank or fifth try has been exceeded, returning None...')
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
            # self.logger.warning(f"{log_prefix}Couldn't parse `{date_str}` in the format provided ({format}), trying backup format...")
            tries += 1
            try:
                date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ') + timedelta(hours=offset_hrs)
            except ValueError as e:
                # self.logger.warning(f"{log_prefix}Couldn't parse date again...Appending Z and trying again as `{date_str}Z{offset_hr_str}`...")
                tries += 1
                date = self.parse_date_str(date_str=f'{date_str}Z{offset_hr_str}', tries=tries, offset=offset_hr_str!='', log_prefix=log_prefix)
        # self.logger.info(f'{log_prefix}Parsed date successfully!')
        return date


    #MARK: _handle_none_and_empty_strings_
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

         ### :class:`~integration_platform.transform.default_transformer.DefaultTransformer`.:meth:`~integration_platform.transform.default_transformer.DefaultTransformer.parse_phone`

         ### :class:`~integration_platform.transform.default_transformer.DefaultTransformer`.:meth:`~integration_platform.transform.default_transformer.DefaultTransformer.parse_date_str`
            
         ### _______replace_me_______
        '''
        if string == None or string.strip() == '' or not additional_conditions:
            # self.logger.error(f'{log_prefix}{string_descr} {'value is blank, returning None...' if additional_log_str == '' else additional_log_str}')
            return None
        return string.strip()

   

    #MARK: rename_columns
    def rename_columns(self, data: list | dict | pl.DataFrame, output_format: Literal['dict', 'df'], strategy: Literal['.get', '[]'], dict_name: str = ''):
        if isinstance(data, pl.DataFrame):
            data = data.to_dicts()
        if isinstance(data, list):
            first: dict = data[0]
            last: dict = data[-1]
            if first.keys() != last.keys():
                data = last
                self.logger.error(f'Key mismatch!')
                bp = 'here'
            else:
                data = first
        printstr = ''
        ts_str = 'hh:mm:ss'
        len_ts_str = len(ts_str)
        for column in data.keys():
            col_copy = column.replace('$', '').replace('  ', ' ')
            if ' ' in column or '-' in column or ':' in column or '–' in column or '_' in column:
                col_copy = col_copy.replace('(', '').replace(')', '').replace('–', '-').replace('-', ' ').replace('_', ' ').replace(ts_str, '').replace(':', '').replace(',', '').replace('  ', ' ')
            col_copy2 = self.string_case_pascal(string=col_copy)
            bp = 'here'
            stripped = ''.join([s for s in col_copy2.split(' ')]) if col_copy2 != None else ''
            if strategy == '.get':
                pstr = f"'{column}': '{stripped}'," if output_format == 'df' else f"'{stripped}': {dict_name}.get('{column}'),"
            else:
                pstr = f"'{column}': '{stripped}'," if output_format == 'df' else f"'{stripped}': {dict_name}['{column}'],"
            printstr += f'{pstr}\n'
            bp = 'here'
        bp = 'here'
        self.logger.info(f'\n{printstr}')
        bp = 'here'




acronyms = ['B2B', 'HTML', 'AI', 'STL', 'IP', 'D2C', 'ID', 'BPS', 'NPS', 'CSAT', 'JHL', 'GPS', 'DNC', 'IQL', 'URL']

