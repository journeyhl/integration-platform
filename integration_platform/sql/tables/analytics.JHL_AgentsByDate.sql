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
where t.name = 'JHL_AgentsByDate' and s.name = 'analytics'
)
create table analytics.JHL_AgentsByDate(
Year int not null,
FinPeriod varchar(7) not null,
Month int not null,
Date date not null,
DuringBusinessHours int not null,
Agents int,
InsertedDT datetime,
LastChecked datetime,
primary key(Year, FinPeriod, Month, Date, DuringBusinessHours))