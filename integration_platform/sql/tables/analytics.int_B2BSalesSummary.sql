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
	where t.name = 'int_B2BSalesSummary' and s.name = 'analytics'
)
begin
	create table analytics.int_B2BSalesSummary(
		Salesperson varchar(12) not null,
		FinPeriod varchar(10) not null,
		Orders int,
		UnitsSold int,
		Booked decimal(18,2),
		Shipped decimal(18,2),
		FinPeriodTotal int,
		InsertedDT datetime,
		LastChecked datetime,
		primary key(Salesperson, FinPeriod))
end

