from __future__ import annotations
from typing import TYPE_CHECKING, Literal
if TYPE_CHECKING:
    from integration_platform.connectors.sql import SQLConnector
import logging
import requests
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import polars as pl

class SQLHelper:
    
    def __init__(self, sqldb: SQLConnector) -> None:
        self.db = sqldb
        self.pipeline = self.db.pipeline
        try:
            self.default_transformer = self.pipeline.default_transformer
        except Exception as e:
            bp = 'here'
        if type(sqldb.pipeline) == str:
            self.logger = logging.getLogger(f'{sqldb.pipeline}.SQLHelper')
        else:
            self.logger = logging.getLogger(f'{sqldb.pipeline.pipeline_name}.SQLHelper')        
        pass


    
    def dataframe_to_sql_table(self, df: pl.DataFrame):
        ''':class:`~SQLHelper`.:meth:`~dataframe_to_sql_table`
        ---
        
        Given a dataframe with unnormalized column names, print/log in the format needed to place in `settings.py`'s :obj:`~integration_platform.config.settings.TABLES`
        >>> 'Unformatted column name': 'FormattedColumnName',
        
        Parameters
        ---
        :param (*pl.DataFrame*) `df`: dataframe table creation is being drafted for
        '''        
        printstr = ''
        ts_str = 'hh:mm:ss'
        len_ts_str = len(ts_str)
        for column in df.columns:
            if ' ' in column or '-' in column or ':' in column or '–' in column:
                col_copy = column
                col_copy = col_copy.replace('(', '').replace(')', '').replace('–', '-').replace('-', '_').replace(ts_str, '').replace(':', '').replace(',', '')
                col_copy2 = self.default_transformer.string_case_pascal(string=col_copy)
                bp = 'here'
                stripped = ''.join([s for s in col_copy2.split(' ')])
                pstr = f"'{column}': '{stripped}',"
                printstr += f'{pstr}\n'
                bp = 'here'
        bp = 'here'
        self.logger.info(f'\n{printstr}')
        bp = 'here'


    #MARK: dataframe_to_table_create_statement
    def dataframe_to_table_create_statement(self, df: pl.DataFrame, table_name: str = ''):
        ''':class:`~integration_platform.helpers.sql_helper.SQLHelper`.:meth:`~integration_platform.helpers.sql_helper.SQLHelper.dataframe_to_table_create_statement`
        ---
        
        Given a dataframe
        
        Parameters
        ---
        :param (*pl.DataFrame*) `df`: _description_
        
                
           ### ***Optional***
        :param (*str = ''*) `log_prefix`: String to prepend to any logger outputs. Usually used when iterating, like `'keyvalue1, 1/150: '`, `'keyvalue2, 2/150: '` and so on 
        
        Returns
        ---
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### _______replace_me_______
        
          - Description
        
         ### _______replace_me_______
           
          - Description
        
        ## Downstream Calls (Methods/Functions called)
        
         ### _______replace_me_______
        
          - Description
        
         ### _______replace_me_______
           
          - Description
        '''        
        table_string = ''
        schema = 'dbo'
        if '.' in table_name:
            schema = table_name.split('.')[0]
            table_name = table_name.split('.')[1]
            table_string += f"""
if not exists(
    select *
    from sys.schemas s
    where s.name = '{schema}'
)
begin
    exec('create schema {schema}');
end"""

        table_string += f"""
if not exists(
    select * 
    from sys.tables t 
    inner join sys.schemas s on t.schema_id = s.schema_id
    where t.name = '{table_name}' and s.name = '{schema}'
)
begin\n"""
        table_name = f'{schema}.{table_name}'
        table_string += f'create table {table_name}(\n'
        for column, dtype in df.schema.items():
            if dtype == pl.String:
                maxlen = df.select(pl.col(column).str.len_chars()).max().to_dicts()[0][column]
                maxlen = maxlen if maxlen != None else 85
                dtype_str = f'varchar({maxlen}),'
            elif str(dtype) == 'Decimal(precision=38, scale=2)':
                dtype_str = 'decimal(18,2),'
            elif str(dtype) == "Datetime(time_unit='us', time_zone='America/New_York')":
                dtype_str = 'datetime,'
            elif str(dtype) == "Datetime(time_unit='us', time_zone=None)":
                dtype_str = 'datetime,'
            elif str(dtype) == 'Boolean':
                dtype_str = 'bit,'
            elif str(dtype) == 'Int64':
                dtype_str = 'int,'
            elif str(dtype) == 'Date':
                dtype_str = 'Date,'
            else:
                dtype_str = str(dtype)
            if 'date' in column.lower():
                dtype_str = 'Date,'
            # dtype_str = 'varchar(replace_me_please),' if dtype == pl.String else 'decimal(18,2),' if str(dtype) == 'Decimal(precision=38, scale=2)' else 'datetime,'
            row_text = f'{column} {dtype_str}'
            table_string += f'{row_text}\n'
            bp = 'here'

        table_string += ')\nend'
        t = table_string[-3:]
        t2 = table_string[:-3]
        print(table_string)
        bp = 'here'