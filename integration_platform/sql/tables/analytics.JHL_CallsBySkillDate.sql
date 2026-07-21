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
    where t.name = 'JHL_CallsBySkillDate' and s.name = 'analytics'
)
begin
    create table analytics.JHL_CallsBySkillDate(
    RawSkill varchar(65) not null,
    SkillProduct varchar(65) not null,
    Calls int,
    Date date not null,
    Month int not null,
    Year int not null,
    FinPeriod varchar(7) not null,
    InsertedDT datetime,
    LastChecked datetime,
    primary key(RawSkill, SkillProduct, Month, Year, Date, FinPeriod))
end