
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
	where t.name = 'JHL_B2BCustomerCohorts' and s.name = 'analytics'
)
begin
    create table analytics.JHL_B2BCustomerCohorts(
    CustomerID varchar(15) not null,
    Cohort varchar(95),
    AnchorDate date,
    AnchorType varchar(95),
    LastProductDate date,
    LastPADate date,
    MonthsSinceProduct int,
    MonthsSincePA int,
    CustomerCreated datetime,
    InsertedDT datetime,
    LastChecked datetime,
    primary key(CustomerID))
end