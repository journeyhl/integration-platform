

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
	where t.name = 'JHL_D2CCustomerOrderHistory' and s.name = 'analytics'
)
begin
    create table analytics.JHL_D2CCustomerOrderHistory(
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
    OrdersAsc_Phone int,
    OrdersDesc_Phone int,
    OrdersAsc_Email int,
    OrdersDesc_Email int,
    CreatedOn datetime,
    Phone varchar(20),
    Email varchar(100),
    OrderProdAsc int,
    OrderProdDesc int,
    OrderProdAsc_Phone int,
    OrderProdDesc_Phone int,
    OrderProdAsc_Email int,
    OrderProdDesc_Email int,
    InsertedDT datetime,
    LastChecked datetime,
    primary key(CustomerID, OrdersAsc))
end