
if not exists(
    select *
    from sys.schemas s
    where s.name = 'shop'
)
begin
    exec('create schema shop');
end
if not exists(
    select * 
    from sys.tables t 
    inner join sys.schemas s on t.schema_id = s.schema_id
    where t.name = 'Customers' and s.name = 'shop'
)
begin
	create table shop.Customers(
	CustomerID varchar(20) not null,
	FirstName varchar(255),
	LastName varchar(255),
	Email varchar(65),
	EmailMarketingState varchar(55),
	PhoneNumber varchar(13),
	PhoneNumberFmt varchar(10),
	NumberOfOrders int,
	Tags varchar(255),
	AmountSpent decimal(18,2),
	CreatedAt datetime,
	LastChecked datetime,
	InsertedDT datetime,
	primary key(CustomerID))
end