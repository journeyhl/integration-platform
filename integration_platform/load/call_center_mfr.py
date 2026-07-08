from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.call_center_mfr import CallCenterMFR
import logging
import time
import polars as pl
from datetime import datetime
from zoneinfo import ZoneInfo

class Load:
    def __init__(self, pipeline: CallCenterMFR):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.load')
        bp = 'here'


    def landing_loader(self, data_transformed: dict[str, dict[str, pl.DataFrame] | dict[str, dict]]):
        ''':class:`~Load`.:meth:`~landing_loader` (data_transformed: *dict[str, dict[str, pl.DataFrame]  |  dict[str, dict]]*, ):
        ---
        <hr>
        
        "Landing" method for :class:`~Load` class. This method is called from :class:`~pipelines.call_center_mfr.CallCenterMFR`.:meth:`~pipelines.call_center_mfr.CallCenterMFR.load`
        
        ### Downstream Calls 
         #### :class:`~Load`.:meth:`~get_dataframes_to_sql`
            - Given `data_transformed['dataframes']`, add each DataFrame as an attribute and then to self.dfs for insert to sql
         #### :class:`~Load`.:meth:`~get_dicts_to_sql`
            - Given `data_transformed['dicts']`, add each DataFrame as an attribute and then to self.dicts for upsert to sql
            
        <hr>
        
        Parameters
        ---
        :param (*dict[str, dict[str, pl.DataFrame]  |  dict[str, dict]]*) `data_transformed`: A dict containing results of data_transformed within two dicts, `dataframes` and `dicts`. `dataframes` contains pl.DataFrames and `dicts` contains dicts
        '''        
        dataframes = data_transformed['dataframes']
        dicts = data_transformed['dicts']
        self.get_dataframes_to_sql(dataframes=dataframes)
        self.get_dicts_to_sql(dicts=dicts)

        # self.upsert_dicts()
        self._insert_all_dfs_()
        bp = 'here'


    def _insert_all_dfs_(self):
        ''':class:`~Load`.:meth:`~_insert_all_dfs_` (self):
        ---
        <hr>
        
        Method to insert all DataFrames found in self.dfs. This will result in duplicate rows if the tables are already populated
        '''
        total_dfs = len(self.dfs)
        self.logger.info(f'')
        total_rows = sum([df['data'].height for df in self.dfs])
        for i, df in enumerate(self.dfs):
            self.logger.info(f'{i+1}/{total_dfs}: Deleting {df['data'].height} rows from {df['table_name']}...')
            self.pipeline.centralstore.raw_execute(f'delete from {df['table_name']}')
            self.logger.info(f'{i+1}/{total_dfs}: Inserting {df['data'].height} rows to {df['table_name']}...')
            bp = 'here'
            df_stamped: pl.DataFrame = df['data'].with_columns(pl.lit(datetime.now(ZoneInfo('America/New_York')), pl.Datetime).alias('InsertedDT'))
            self.pipeline.centralstore.insert_df(df_data_loaded=df_stamped, table_name=df['table_name'])
            bp = 'here'
        self.logger.info(f'{total_dfs} DataFrames created as tables and {total_rows} rows inserted!')
        bp = 'here'
        

    def upsert_dicts(self):
        for table in self.dicts:
            self.logger.info(f'Beginning upsert to {table['table_name']}')
            table['data'] = [{**t, 'InsertedDT': datetime.now(ZoneInfo('America/New_York'))} for t in table['data']]
            bp = 'here'
            
            self.pipeline.centralstore.checked_upsert_paginated(table_name=table['table_name'], data=table['data'])
            bp = 'here'



    def get_dataframes_to_sql(self, dataframes):
        ''':class:`~Load`.:meth:`~get_dataframes_to_sql` (self, dataframes: *dict[str, pl.DataFrame*):
        ---
        <hr>
        
        Using `data_transformed['dataframes']`, sets each dataframe to an attribute of the Load class, as well as gives each a dict entry with the name of its respective table in db_CentralStore

        ### Upstream Calls 
         #### :class:`~Load`.:meth:`~landing_loader`
            - Called at start of method before any real operations are done 
            
        <hr>
        
        Parameters
        ---
        :param (*dict[str, pl.DataFrame]*) `dataframes`: dictionary containing DataFrames from data_transformed
        
        <hr>
        
        Sets
        ---
        - #### self.:attr:`~df_AdPhoneFull`
        - #### self.:attr:`~df_AcuMFRAllocated`
        - #### self.:attr:`~df_MFRAllocated`
        - #### self.:attr:`~df_CallsBySkillMonth`
        - #### self.:attr:`~df_CallsBySkillDate`
        - #### self.:attr:`~df_CallsByAgentMonth`
        - #### self.:attr:`~df_CallsByAgentDate`
        - #### self.:attr:`~df_CallsBySkillAgentMonth`
        - #### self.:attr:`~df_CallsBySkillAgentDate`
        - #### self.:attr:`~df_CallsByDeptMonth`
        - #### self.:attr:`~df_CallsByDeptDate`
        - #### self.:attr:`~df_CallsBySkillDeptMonth`
        - #### self.:attr:`~df_CallsBySkillDeptDate`
        - #### self.:attr:`~df_CallsByDuringBusinessHrMonth`
        - #### self.:attr:`~df_CallsByDuringBusinessHrDate`
        - #### self.:attr:`~df_AgentsByMonth`
        - #### self.:attr:`~df_AgentsByDate`
        - #### self.:attr:`~df_CallCounts`
        - ### self.:attr:`~dfs`
        '''
        self.df_AdPhoneFull = dataframes['adphone_full'] #analytics.jhl_AdPhone
        self.df_AcuMFRAllocated = dataframes['acu_mfr_allocated'] #analytics.JHL_acuMFRAllocated
        self.df_MFRAllocated = dataframes['mfr_allocated'] #analytics.JHL_MFRAllocated
        self.df_CallsBySkillMonth = dataframes['calls_by_skill_month'] #analytics.JHL_CallsBySkillMonth
        self.df_CallsBySkillDate = dataframes['calls_by_skill_day'] #analytics.JHL_CallsBySkillDate
        self.df_CallsByAgentMonth = dataframes['calls_by_agent_month'] #analytics.JHL_CallsByAgentMonth
        self.df_CallsByAgentDate = dataframes['calls_by_agent_day'] #analytics.JHL_CallsByAgentDate
        self.df_CallsBySkillAgentMonth = dataframes['calls_by_skill_agent_month'] #analytics.JHL_CallsBySkillAgentMonth
        self.df_CallsBySkillAgentDate = dataframes['calls_by_skill_agent_day'] #analytics.JHL_CallsBySkillAgentDate
        self.df_CallsByDeptMonth = dataframes['calls_by_dept_month'] #analytics.JHL_CallsByDeptMonth
        self.df_CallsByDeptDate = dataframes['calls_by_dept_day'] #analytics.JHL_CallsByDeptDate
        self.df_CallsBySkillDeptMonth = dataframes['calls_by_skill_dept_month'] #analytics.JHL_CallsBySkillDeptMonth
        self.df_CallsBySkillDeptDate = dataframes['calls_by_skill_dept_day'] #analytics.JHL_CallsBySkillDeptDate
        self.df_CallsByDuringBusinessHrMonth = dataframes['calls_by_business_hr_month'] #analytics.JHL_CallsByDuringBusinessHrMonth
        self.df_CallsByDuringBusinessHrDate = dataframes['calls_by_business_hr_day'] #analytics.JHL_CallsByDuringBusinessHrDate
        self.df_AgentsByMonth = dataframes['agents_by_month'] #analytics.AgentsByMonth
        self.df_AgentsByDate = dataframes['agents_by_day'] #analytics.AgentsByDate
        self.df_CallCounts = dataframes['CallCounts'] #analytics.int_CallCounts        
        self.dfs = [
            {'data':self.df_AdPhoneFull, 'table_name': 'analytics.jhl_AdPhone'},
            {'data':self.df_AcuMFRAllocated, 'table_name': 'analytics.JHL_acuMFRAllocated'},
            {'data':self.df_MFRAllocated, 'table_name': 'analytics.JHL_MFRAllocated'},
            {'data':self.df_CallsBySkillMonth, 'table_name': 'analytics.JHL_CallsBySkillMonth'},
            {'data':self.df_CallsBySkillDate, 'table_name': 'analytics.JHL_CallsBySkillDate'},
            {'data':self.df_CallsByAgentMonth, 'table_name': 'analytics.JHL_CallsByAgentMonth'},
            {'data':self.df_CallsByAgentDate, 'table_name': 'analytics.JHL_CallsByAgentDate'},
            {'data':self.df_CallsBySkillAgentMonth, 'table_name': 'analytics.JHL_CallsBySkillAgentMonth'},
            {'data':self.df_CallsBySkillAgentDate, 'table_name': 'analytics.JHL_CallsBySkillAgentDate'},
            {'data':self.df_CallsByDeptMonth, 'table_name': 'analytics.JHL_CallsByDeptMonth'},
            {'data':self.df_CallsByDeptDate, 'table_name': 'analytics.JHL_CallsByDeptDate'},
            {'data':self.df_CallsBySkillDeptMonth, 'table_name': 'analytics.JHL_CallsBySkillDeptMonth'},
            {'data':self.df_CallsBySkillDeptDate, 'table_name': 'analytics.JHL_CallsBySkillDeptDate'},
            {'data':self.df_CallsByDuringBusinessHrMonth, 'table_name': 'analytics.JHL_CallsByDuringBusinessHrMonth'},
            {'data':self.df_CallsByDuringBusinessHrDate, 'table_name': 'analytics.JHL_CallsByDuringBusinessHrDate'},
            {'data':self.df_AgentsByMonth, 'table_name': 'analytics.JHL_AgentsByMonth'},
            {'data':self.df_AgentsByDate, 'table_name': 'analytics.JHL_AgentsByDate'},
            {'data':self.df_CallCounts, 'table_name': 'analytics.int_CallCounts'},
        ]
        


    def get_dicts_to_sql(self, dicts):
        ''':class:`~Load`.:meth:`~get_dicts_to_sql` (self, dicts: *dict[str, dict*):
        ---
        <hr>
        
        Using `data_transformed['dicts']`, sets each dataframe to an attribute of the Load class, as well as gives each a dict entry with the name of its respective table in db_CentralStore

        ### Upstream Calls 
         #### :class:`~Load`.:meth:`~landing_loader`
            - Called at start of method before any real operations are done 
            
        <hr>
        
        Parameters
        ---
        :param (*dict[str, dict]*) `dicts`: dictionary containing dicts of DataFrames from data_transformed
        
        <hr>
        
        Sets
        ---
        - #### self.:attr:`~AdPhoneFull`
        - #### self.:attr:`~AcuMFRAllocated`
        - #### self.:attr:`~MFRAllocated`
        - #### self.:attr:`~CallsBySkillMonth`
        - #### self.:attr:`~CallsBySkillDate`
        - #### self.:attr:`~CallsByAgentMonth`
        - #### self.:attr:`~CallsByAgentDate`
        - #### self.:attr:`~CallsBySkillAgentMonth`
        - #### self.:attr:`~CallsBySkillAgentDate`
        - #### self.:attr:`~CallsByDeptMonth`
        - #### self.:attr:`~CallsByDeptDate`
        - #### self.:attr:`~CallsBySkillDeptMonth`
        - #### self.:attr:`~CallsBySkillDeptDate`
        - #### self.:attr:`~CallsByDuringBusinessHrMonth`
        - #### self.:attr:`~CallsByDuringBusinessHrDate`
        - #### self.:attr:`~AgentsByMonth`
        - #### self.:attr:`~AgentsByDate`
        - #### self.:attr:`~CallCounts`
        - ### self.:attr:`~dicts`
        '''
        self.CallCounts = dicts['CallCounts']
        self.AdPhoneFull = dicts['adphone_full']
        self.AcuMFRAllocated = dicts['acu_mfr_allocated']
        self.MFRAllocated = dicts['mfr_allocated']
        self.CallsBySkillMonth = dicts['calls_by_skill_month']
        self.CallsBySkillDate = dicts['calls_by_skill_day']
        self.CallsByAgentMonth = dicts['calls_by_agent_month']
        self.CallsByAgentDate = dicts['calls_by_agent_day']
        self.CallsBySkillAgentMonth = dicts['calls_by_skill_agent_month']
        self.CallsBySkillAgentDate = dicts['calls_by_skill_agent_day']
        self.CallsByDeptMonth = dicts['calls_by_dept_month']
        self.CallsByDeptDate = dicts['calls_by_dept_day']
        self.CallsBySkillDeptMonth = dicts['calls_by_skill_dept_month']
        self.CallsBySkillDeptDate = dicts['calls_by_skill_dept_day']
        self.CallsByDuringBusinessHrMonth = dicts['calls_by_business_hr_month']
        self.CallsByDuringBusinessHrDate = dicts['calls_by_business_hr_day']
        self.AgentsByMonth = dicts['agents_by_month']
        self.AgentsByDate = dicts['agents_by_day']
        self.dicts = [
            {'data':self.AdPhoneFull, 'table_name': 'analytics.jhl_AdPhone'},
            {'data':self.AcuMFRAllocated, 'table_name': 'analytics.JHL_acuMFRAllocated'},
            {'data':self.MFRAllocated, 'table_name': 'analytics.JHL_MFRAllocated'},
            {'data':self.CallsBySkillMonth, 'table_name': 'analytics.JHL_CallsBySkillMonth',},
            {'data':self.CallsBySkillDate, 'table_name': 'analytics.JHL_CallsBySkillDate',},
            {'data':self.CallsByAgentMonth, 'table_name': 'analytics.JHL_CallsByAgentMonth',},
            {'data':self.CallsByAgentDate, 'table_name': 'analytics.JHL_CallsByAgentDate',},
            {'data':self.CallsBySkillAgentMonth, 'table_name': 'analytics.JHL_CallsBySkillAgentMonth',},
            {'data':self.CallsBySkillAgentDate, 'table_name': 'analytics.JHL_CallsBySkillAgentDate',},
            {'data':self.CallsByDeptMonth, 'table_name': 'analytics.JHL_CallsByDeptMonth',},
            {'data':self.CallsByDeptDate, 'table_name': 'analytics.JHL_CallsByDeptDate',},
            {'data':self.CallsBySkillDeptMonth, 'table_name': 'analytics.JHL_CallsBySkillDeptMonth',},
            {'data':self.CallsBySkillDeptDate, 'table_name': 'analytics.JHL_CallsBySkillDeptDate',},
            {'data':self.CallsByDuringBusinessHrMonth, 'table_name': 'analytics.JHL_CallsByDuringBusinessHrMonth',},
            {'data':self.CallsByDuringBusinessHrDate, 'table_name': 'analytics.JHL_CallsByDuringBusinessHrDate',},
            {'data':self.AgentsByMonth, 'table_name': 'analytics.JHL_AgentsByMonth'},
            {'data':self.AgentsByDate, 'table_name': 'analytics.JHL_AgentsByDate'},
            {'data':self.CallCounts, 'table_name': 'analytics.int_CallCounts'},
        ]