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
	create table analytics.int_B2BCustomerOrderHistory(
		CustomerID varchar(12) not null,
		AccountName varchar(255),
		OrderNbr varchar(10),
		ItemClassDesc varchar(155),
		Item varchar(20),
		DatePlaced date,
		EarliestFirst int not null,
		RecentFirst int,
		FirstOrder date,
		LastOrder date,
		CreatedOn datetime,
		Phone varchar(12),
		InsertedDT datetime,
		LastChecked datetime,
		primary key(CustomerID, EarliestFirst))
end

