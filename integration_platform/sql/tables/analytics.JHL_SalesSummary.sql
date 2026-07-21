
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
    where t.name = 'jhl_SalesSummary' and s.name = 'analytics'
)
begin
    create table analytics.JHL_SalesSummary(
    MetricBucket varchar(25) not null,
    FinPeriod varchar(7) not null,
    Booked decimal(18, 2),
    Shipped decimal(18, 2),
    FinPeriodTotal bit not null,
    InsertedDT datetime,
    LastChecked datetime,
    Primary key(MetricBucket, FinPeriod, FinPeriodTotal))
end