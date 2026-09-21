

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
	where t.name = 'JHL_B2BCustomerOrderHistory' and s.name = 'analytics'
)
begin
    create table analytics.JHL_B2BCustomerOrderHistory(
    CustomerClass varchar(5),
    CustomerID varchar(10) not null,
    AccountName varchar(1000),
    OrderNbr varchar(10),
    ItemClassDesc varchar(100),
    PartProdAccFee varchar(85),
    DatePlaced date,
    DaysAgo int,
    OrdersAsc int not null,
    OrdersDesc int,
    CreatedOn datetime,
    Phone varchar(20),
    Email varchar(100),
    OrderProdAsc int,
    OrderProdDesc int,
    InsertedDT datetime,
    LastChecked datetime,
    primary key(CustomerID, OrdersAsc))
end