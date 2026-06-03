import pyperclip





def landing():
    text = pyperclip.paste()
    schema, table = get_schema(text)
    text = text.replace(
        'NOT NULL', 'not null'
        ).replace('\r\nGO', ''
        ).replace('SET ANSI_NULLS ON', ''
        ).replace('SET QUOTED_IDENTIFIER ON', ''
        ).replace('NULL', ''
        ).replace('CREATE TABLE', 'create table'
        ).replace('[', ''
        ).replace(' ,', ','
        ).replace(']', ''
        ).replace(' ASC\r\n)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON PRIMARY\r\n) ON PRIMARY\r\nGO\r\n', ''
        ).replace(' ASC\r\n)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON PRIMARY\r\n) ON PRIMARY\r\nGO', ''
        ).replace(' ASC\r\n)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON PRIMARY\r\n) ON PRIMARY\r\n', ''
        ).replace('\r\nPRIMARY KEY CLUSTERED \r\n(\r\n\t', '\nPrimary Key('
        ).replace('\r\n', '\n').replace('\t', ''
        ).replace('\n\n\n\n', '\n')
    text = text + '))'
    prepend = f'''if not exists(
select *
from sys.schemas s
where s.name = '{schema}'
)
exec('create schema {schema}');
if not exists(
select * 
from sys.tables t 
inner join sys.schemas s on t.schema_id = s.schema_id
where t.name = '{table}' and s.name = '{schema}'
)
'''
    pyperclip.copy(prepend + text)
    bp = 'here'

def get_schema(text):
    length = len('create table[')
    schema = text.find('CREATE TABLE [')
    start = text[schema + length:]
    schema_delim = start.find('.')
    schema = start[:schema_delim].replace('[', '').replace(']', '')

    table_start = start[schema_delim + 2:]
    table_delim = table_start.find(']')
    table = table_start[:table_delim]
    bp = 'here'
    return schema, table


landing()