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
	where t.name = 'raw_B2BSalesSummary' and s.name = 'analytics'
)
begin
	create table analytics.raw_B2BSalesSummary(
		Salesperson varchar(12),
		OrderType varchar(3),
		OrderNbr varchar(12),
		DatePlaced date,
		FinPeriod varchar(12),
		CustomerID varchar(12) not null,
		CustomerClass varchar(5),
		Total_Qty int,
		Total_LinePrice decimal(18,2),
		Total_Discount decimal(18,2),
		Total_Revenue decimal(18,2),
		Total_LineCost decimal(18,2),
		Total_WarrantyRevenue decimal(18,2),
		Status varchar(55),
		CustTypeBucket varchar(55),
		Channel varchar(55),
		MetricBucket varchar(55),
		Booked bit,
		Shipped bit,	
		Lines int,
		InsertedDT datetime,
		LastChecked datetime,
		primary key (CustomerID, OrderType, OrderNbr))
end

