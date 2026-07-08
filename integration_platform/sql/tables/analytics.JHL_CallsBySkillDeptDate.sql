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
where t.name = 'JHL_CallsBySkillDeptDate' and s.name = 'analytics'
)
create table analytics.JHL_CallsBySkillDeptDate(
RawSkill varchar(65) not null,
SkillProduct varchar(65) not null,
Department varchar(65) not null,
Calls int,
Date date not null,
Month int not null,
Year int not null,
FinPeriod varchar(7) not null,
InsertedDT datetime,
LastChecked datetime,
primary key(RawSkill, SkillProduct, Department, Month, Year, Date, FinPeriod))
