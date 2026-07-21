if not exists(
    select *
    from sys.schemas s
    where s.name = 'acu'
)
begin
    exec('create schema acu');
end
if not exists(
    select * 
    from sys.tables t 
    inner join sys.schemas s on t.schema_id = s.schema_id
    where t.name = 'AftershipExportDetailv2' and s.name = 'acu'
)
begin
    create table acu.TrialBalance(
    AccountCD int not null,
    Type varchar(15) not null,
    Sub varchar(25),
    Description varchar(355),
    FinPeriod varchar(10) not null,
    BeginningBalance decimal(18,2),
    Debit decimal(18,2),
    Credit decimal(18,2),
    EndingBalance decimal(18,2),
    StartDate date,
    EndDate date,
    TypeID varchar(1),
    SubCD varchar(15),
    FinPeriodID varchar(10),
    InsertedDT datetime,
    LastChecked datetime,
    primary key (AccountCD, Type, FinPeriod))
end