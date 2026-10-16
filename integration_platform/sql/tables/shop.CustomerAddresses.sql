
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
    where t.name = 'CustomerAddresses' and s.name = 'shop'
)
begin
create table shop.CustomerAddresses(
CustomerID varchar(20) not null,
AddressID varchar(20) not null,
Address1 varchar(90),
City varchar(90),
Province varchar(90),
Zip varchar(25),
Country varchar(55),
LastChecked datetime,
InsertedDT datetime,
primary key(CustomerID, AddressID))
end