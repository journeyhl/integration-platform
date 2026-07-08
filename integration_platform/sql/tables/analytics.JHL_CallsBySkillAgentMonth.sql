
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
where t.name = 'JHL_CallsBySkillAgentMonth' and s.name = 'analytics'
)
create table analytics.JHL_CallsBySkillAgentMonth(
RawSkill varchar(65) not null,
SkillProduct varchar(65) not null,
Agent varchar(65) not null,
Calls int,
Month int not null,
Year int not null,
FinPeriod varchar(7) not null,
InsertedDT datetime,
LastChecked datetime,
primary key(RawSkill, SkillProduct, Agent, Month, Year, FinPeriod))