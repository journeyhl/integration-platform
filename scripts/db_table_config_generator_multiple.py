import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.connectors import SQLConnector
import polars as pl
import pyperclip

'''
This file generates the neccessary entry in TABLES (config/settings.py) for checked_upsert to function. 

Use when adding multiple tables in one go
'''


dbc = 'db_CentralStore'
acudb = 'AcumaticaDb'
query = '''

with TopLevel as(
select s.schema_id SchemaID
     , t.object_id TableID
     , c.column_id ColumnID
     , s.name sName
     , t.name tName
     , c.Name cName
     , case when k.object_id is not null then 'Key' 
            when c.is_nullable = 0 then 'Not Null (Maybe key)'
       else 'Update' end ColumnType
     , row_number() over(partition by s.schema_id, t.object_id, c.column_id order by case when k.object_id is not null then 'Key' when c.is_nullable = 0 then 'Not Null (Maybe key)' else 'Update' end ) rownum
from sys.schemas s
inner join sys.tables t on s.schema_id = t.schema_id
inner join sys.columns c on t.object_id = c.object_id
left join sys.index_columns k on t.object_id = k.object_id and c.column_id = k.column_id 
where s.name = '{schema}' and t.name = '{table}'
)
select t.SchemaID
     , t.TableID
     , t.ColumnID
     , t.sName
     , t.tName
     , t.cName
     , t.ColumnType
from TopLevel t
where rownum = 1
'''

# db_input = input('Enter db name or at least first 2 characters: ').lower()
db_input = dbc

try:
    is_str = str(db_input)
except Exception as e:
    print("That's not a string!")
    db_input = input('Enter db name or at least first 2 characters: ').lower()
    
input_len = len(db_input)
if db_input.lower() == dbc[0:input_len].lower():
    db = dbc
elif db_input.lower() == acudb[0:input_len].lower():
    db = acudb

db = SQLConnector('config-generator', db)
tables = [
'analytics.B2BCollectionsByStatus',
'analytics.B2BCollectionsByStatus_Snapshot',
'analytics.B2BCollectionsBySalesRep',
'analytics.B2BCollectionsBySalesRep_Snapshot',
# 'analytics.B2BCollectionsDetail',
# 'analytics.B2BCollectionsSummary',
# 'analytics.B2BCollectionsSummary_Snapshot',
# 'analytics.JHL_SalesSummary',
# 'analytics.int_SalesSummary',
# 'analytics.raw_SalesSummary',
# 'analytics.jhl_AdPhone',
# 'analytics.JHL_acuMFRAllocated',
# 'analytics.JHL_MFRAllocated',
# 'analytics.JHL_CallsBySkillMonth',
# 'analytics.JHL_CallsBySkillDate',
# 'analytics.JHL_CallsByAgentMonth',
# 'analytics.JHL_CallsByAgentDate',
# 'analytics.JHL_CallsBySkillAgentMonth',
# 'analytics.JHL_CallsBySkillAgentDate',
# 'analytics.JHL_CallsByDeptMonth',
# 'analytics.JHL_CallsByDeptDate',
# 'analytics.JHL_CallsBySkillDeptMonth',
# 'analytics.JHL_CallsBySkillDeptDate',
# 'analytics.JHL_CallsByDuringBusinessHrMonth',
# 'analytics.JHL_CallsByDuringBusinessHrDate',
# 'analytics.JHL_AgentsByMonth',
# 'analytics.JHL_AgentsByDate',
# 'analytics.int_CallCounts',
]

table_str = ''
for name in tables:
    sname = name.split('.')
    schema = sname[0]
    table = sname[1]
    config_results = db.query_db(query.format(schema=schema, table=table))
    results = {
        name: {}
    }
    results[name]['keys'] = [value['cName'] for value in config_results.sql("select cName from self where ColumnType in('Key', 'Not Null (Maybe key)')").to_dicts()]
    results[name]['columns'] = [row['cName'] for row in config_results.iter_rows(named=True)]
    results[name]['update_columns'] = [value['cName'] for value in config_results.sql("select cName from self where ColumnType = 'Update'").to_dicts()]
    bp = 'here'

    def format_entry(table_name, cfg):
        lines = [f"'{table_name}': {{"]
        for section in ('keys', 'columns', 'update_columns'):
            lines.append(f"        '{section}': [")
            for item in cfg[section]:
                lines.append(f"            '{item}',")
            lines.append("        ],")
        lines.append("    },")
        table = '\n'.join(lines)
        return table
    table = format_entry(name, results[name])
    table_str += f'{table}\n    '
    pyperclip.copy(table)
    bp = 'here'

bp = 'here'
pyperclip.copy(table_str)

bp = 'here'
