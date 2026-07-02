from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.call_center_mfr import CallCenterMFR
import logging
import time
import polars as pl


class Load:
    def __init__(self, pipeline: CallCenterMFR):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.load')
        bp = 'here'



    def landing_loader(self, data_transformed: dict[str, dict[str, pl.DataFrame] | dict[str, dict]]):
        dataframes = data_transformed['dataframes']
        dicts = data_transformed['dicts']
        self.get_dataframes_to_sql(dataframes=dataframes)
        self.get_dicts_to_sql(dicts=dicts)
        bp = 'here'
        for df in self.dfs:
            self.logger.info(f'Inserting {df['df'].height} rows to {df['table_name']}')
            bp = 'here'
            self.pipeline.centralstore.insert_df(df_data_loaded=df['df'], table_name=df['table_name'])
            bp = 'here'







    def get_dataframes_to_sql(self, dataframes):
        
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
            {
                'df': self.df_AdPhoneFull,
                'table_name': 'analytics.jhl_AdPhone'
            },
            {
                'df': self.df_AcuMFRAllocated,
                'table_name': 'analytics.JHL_acuMFRAllocated'
            },
            {
                'df': self.df_MFRAllocated,
                'table_name': 'analytics.JHL_MFRAllocated'
            },
            {
                'df': self.df_CallsBySkillMonth,
                'table_name': 'analytics.JHL_CallsBySkillMonth'
            },
            {
                'df': self.df_CallsBySkillDate,
                'table_name': 'analytics.JHL_CallsBySkillDate'
            },
            {
                'df': self.df_CallsByAgentMonth,
                'table_name': 'analytics.JHL_CallsByAgentMonth'
            },
            {
                'df': self.df_CallsByAgentDate,
                'table_name': 'analytics.JHL_CallsByAgentDate'
            },
            {
                'df': self.df_CallsBySkillAgentMonth,
                'table_name': 'analytics.JHL_CallsBySkillAgentMonth'
            },
            {
                'df': self.df_CallsBySkillAgentDate,
                'table_name': 'analytics.JHL_CallsBySkillAgentDate'
            },
            {
                'df': self.df_CallsByDeptMonth,
                'table_name': 'analytics.JHL_CallsByDeptMonth'
            },
            {
                'df': self.df_CallsByDeptDate,
                'table_name': 'analytics.JHL_CallsByDeptDate'
            },
            {
                'df': self.df_CallsBySkillDeptMonth,
                'table_name': 'analytics.JHL_CallsBySkillDeptMonth'
            },
            {
                'df': self.df_CallsBySkillDeptDate,
                'table_name': 'analytics.JHL_CallsBySkillDeptDate'
            },
            {
                'df': self.df_CallsByDuringBusinessHrMonth,
                'table_name': 'analytics.JHL_CallsByDuringBusinessHrMonth'
            },
            {
                'df': self.df_CallsByDuringBusinessHrDate,
                'table_name': 'analytics.JHL_CallsByDuringBusinessHrDate'
            },
            {
                'df': self.df_AgentsByMonth,
                'table_name': 'analytics.JHL_AgentsByMonth'
            },
            {
                'df': self.df_AgentsByDate,
                'table_name': 'analytics.JHL_AgentsByDate'
            },
            {
                'df': self.df_CallCounts,
                'table_name': 'analytics.int_CallCounts'
            }
        ]
        


    def get_dicts_to_sql(self, dicts):

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