if not exists(
    select *
    from sys.schemas s
    where s.name = 'analytics'
)
begin
    exec('create schema analytics');
end
if not exists(
    select * 
    from sys.tables t 
    inner join sys.schemas s on t.schema_id = s.schema_id
    where t.name = 'JHL_AgentsByMonth' and s.name = 'analytics'
)
begin
    create table analytics.JHL_AgentsByMonth(
    Year int not null,
    FinPeriod varchar(7) not null,
    Month int not null,
    Agents int,
    InsertedDT datetime,
    LastChecked datetime,
    primary key(Year, FinPeriod, Month))
end