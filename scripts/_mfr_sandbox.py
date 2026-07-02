import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines import CallCenterMFR
import polars as pl


mfr = CallCenterMFR('.debug')
data_extract = mfr.extract()
data_transformed = mfr.transform(data_extract=data_extract)
transformed_dicts = {}
for key, dataframe in data_transformed.items():
    transformed_dicts[key] = dataframe.to_dicts()

# for key, data in transformed_dicts.items():
#     print(f"{key} = transformed_dicts['{key}']")



bp = 'here'






tables = pl.SQLContext(
    InventorySummary_Product = data_transformed['InventorySummary_Product'],
    PhoneRevPreStaging = data_transformed['PhoneRevPreStaging'],
    AdPhonePriorityDates = data_transformed['AdPhonePriorityDates'],
    AdVersionProduct = data_transformed['AdVersionProduct'],
    CallCounts = data_transformed['CallCounts'],
    AdDetailVersion = data_transformed['AdDetailVersion'],

    adphone_full = data_transformed['adphone_full'],
    aggregate_call_counts = data_transformed['aggregate_call_counts'],
    phone_revenue_staging = data_transformed['phone_revenue_staging'],
    lineamt_calc = data_transformed['lineamt_calc'],
    phone_revenue = data_transformed['phone_revenue'],
    inter_mfr_matched = data_transformed['inter_mfr_matched'],
    inter_mfr_rownum = data_transformed['inter_mfr_rownum'],
    inter_mfr_allocated = data_transformed['inter_mfr_allocated'],
    acu_mfr_allocated = data_transformed['acu_mfr_allocated'],
    mfr_allocated = data_transformed['mfr_allocated'],
    calls_by_skill_month = data_transformed['calls_by_skill_month'],
    calls_by_skill_day = data_transformed['calls_by_skill_day'],
    calls_by_agent_month = data_transformed['calls_by_agent_month'],
    calls_by_agent_day = data_transformed['calls_by_agent_day'],
    calls_by_skill_agent_month = data_transformed['calls_by_skill_agent_month'],
    calls_by_skill_agent_day = data_transformed['calls_by_skill_agent_day'],
    calls_by_dept_month = data_transformed['calls_by_dept_month'],
    calls_by_dept_day = data_transformed['calls_by_dept_day'],
    calls_by_skill_dept_month = data_transformed['calls_by_skill_dept_month'],
    calls_by_skill_dept_day = data_transformed['calls_by_skill_dept_day'],
    calls_by_business_hr_month = data_transformed['calls_by_business_hr_month'],
    calls_by_business_hr_day = data_transformed['calls_by_business_hr_day'],
    agents_by_month = data_transformed['agents_by_month'],
    agents_by_day = data_transformed['agents_by_day'],
)


InventorySummaryProduct = transformed_dicts['InventorySummary_Product']
PhoneRevPreStaging = transformed_dicts['PhoneRevPreStaging']
AdPhonePriorityDates = transformed_dicts['AdPhonePriorityDates']
AdVersionProduct = transformed_dicts['AdVersionProduct']

CallCounts = transformed_dicts['CallCounts']

AdDetailVersion = transformed_dicts['AdDetailVersion']

AdPhoneFull = transformed_dicts['adphone_full']

AggregateCallCounts = transformed_dicts['aggregate_call_counts']
PhoneRevenueStaging = transformed_dicts['phone_revenue_staging']
LineamtCalc = transformed_dicts['lineamt_calc']
PhoneRevenue = transformed_dicts['phone_revenue']

InterMFRMatched = transformed_dicts['inter_mfr_matched']
InterMFRRownum = transformed_dicts['inter_mfr_rownum']
InterMFRAllocated = transformed_dicts['inter_mfr_allocated']

AcuMFRAllocated = transformed_dicts['acu_mfr_allocated']
MFRAllocated = transformed_dicts['mfr_allocated']

CallsBySkillMonth = transformed_dicts['calls_by_skill_month']
CallsBySkillDay = transformed_dicts['calls_by_skill_day']
CallsByAgentMonth = transformed_dicts['calls_by_agent_month']
CallsByAgentDay = transformed_dicts['calls_by_agent_day']
CallsBySkillAgentMonth = transformed_dicts['calls_by_skill_agent_month']
CallsBySkillAgentDay = transformed_dicts['calls_by_skill_agent_day']
CallsByDeptMonth = transformed_dicts['calls_by_dept_month']
CallsByDeptDay = transformed_dicts['calls_by_dept_day']
CallsBySkillDeptMonth = transformed_dicts['calls_by_skill_dept_month']
CallsBySkillDeptDay = transformed_dicts['calls_by_skill_dept_day']
CallsByDuringBusinessHrMonth = transformed_dicts['calls_by_business_hr_month']
CallsByDuringBusinessHrDay = transformed_dicts['calls_by_business_hr_day']
AgentsByMonth = transformed_dicts['agents_by_month']
AgentsByDay = transformed_dicts['agents_by_day']


bp = 'here'


take = [

]