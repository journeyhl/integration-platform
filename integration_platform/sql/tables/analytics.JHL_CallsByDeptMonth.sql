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
    where t.name = 'JHL_CallsByDeptMonth' and s.name = 'analytics'
)
begin
    create table analytics.JHL_CallsByDeptMonth(
    Department varchar(55) not null,
    Calls int,
    Month int not null,
    Year int not null,
    FinPeriod varchar(7) not null,
    InsertedDT datetime,
    LastChecked datetime,
    primary key(Department, Month, Year, FinPeriod))
end