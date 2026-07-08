if not exists(
select *
from sys.schemas s
where s.name = 'analytics'
)
exec('create schema analytics');
if not exists(
select * 
from sys.tables t 
inner join sys.schemas s on t.schema_id = s.schema_id
where t.name = 'JHL_CallsByAgentMonth' and s.name = 'analytics'
)
create table analytics.JHL_CallsByAgentMonth(
Agent varchar(100) not null,
Calls int,
Month int not null,
Year int not null,
FinPeriod varchar(7) not null,
InsertedDT datetime,
LastChecked datetime,
primary key(Agent, Month, Year, FinPeriod))
