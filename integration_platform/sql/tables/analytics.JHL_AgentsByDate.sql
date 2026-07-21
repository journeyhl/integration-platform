if not exists(
    select *
    from sys.schemas s
    where s.name = 'analytics'
)
begin
    exec('create schema analytics');
end
exec('create schema analytics');
if not exists(
    select * 
    from sys.tables t 
    inner join sys.schemas s on t.schema_id = s.schema_id
    where t.name = 'JHL_AgentsByDate' and s.name = 'analytics'
)
begin
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
end