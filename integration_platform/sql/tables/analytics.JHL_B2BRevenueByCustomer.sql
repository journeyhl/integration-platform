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
	where t.name = 'int_B2BCustomerOrderHistory' and s.name = 'analytics'
)
begin
	create table analytics.JHL_B2BRevenueByCustomerType(
		CustomerType varchar(20) not null,
		FinPeriod varchar(8) not null,
		Orders int,
		UnitsSold int,
		Booked decimal(18,2),
		Shipped decimal(18,2),
		UnitsPerOrder decimal(18,2),
		AverageOrderValue decimal(18,2),
		InsertedDT datetime,
		LastChecked datetime,
		primary key(CustomerType, FinPeriod))
end

