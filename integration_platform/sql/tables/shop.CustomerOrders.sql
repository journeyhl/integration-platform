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
    where t.name = 'CustomerOrders' and s.name = 'shop'
)
begin
create table shop.CustomerOrders(
CustomerID varchar(20) not null,
OrderID varchar(20) not null,
ShopOrderNbr varchar(35),
CreatedAt datetime,
Price decimal(18,2),
LastChecked datetime,
CustomerOrderSeq int,
InsertedDT datetime,
primary key(CustomerID, OrderID))
end