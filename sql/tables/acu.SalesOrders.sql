if not exists(
select *
from sys.schemas s
where s.name = 'acu'
)
exec('create schema acu');
if not exists(
select * 
from sys.tables t 
inner join sys.schemas s on t.schema_id = s.schema_id
where t.name = 'SalesOrders' and s.name = 'acu'
)
create table acu.SalesOrders(
OrderType varchar(3) not null,
OrderNumber varchar(10) not null,
LineNbr int not null,
DatePlaced date,
CustomerID varchar(20),
CustomerName varchar(300),
CustomerClass varchar(3),
InventoryCD varchar(30),
Description varchar(100),
Quantity int,
LinePrice float,
OrderTotal float,
Status varchar(30),
CustOrderNumber varchar(100),
D2CSalesperson varchar(100),
SalespersonName varchar(100),
SalespersonEmail varchar(100),
B2BSalesperson varchar(100),
LastModifiedDT datetime,
DiscountCode varchar(30),
DiscountAmt float,
LineCost float,
Phone varchar(20),
Email varchar(255),
AddressLine1 varchar(355),
AddressLine2 varchar(255),
City varchar(255),
State varchar(50),
Zip varchar(30),
Country varchar(55),
LineAmount float,
ReplenishmentClass varchar(255),
StockItem bit,
OrderLineWH varchar(255),
ShipDate date,
ShipmentNbr varchar(255),
ShipStatus varchar(255),
ShipmentWH varchar(255),
Completed bit,
OriginalOrderType varchar(5),
OriginalOrderNbr varchar(30),
FreightPrice decimal(18, 2),
PremiumFreightPrice decimal(18, 2),
FreightTotal decimal(18, 2),
CreatedDT datetime,
CreatedBy varchar(100),
LastModifiedBy varchar(100),
LastChecked datetime,
Primary Key(OrderNumber,
LineNbr,
OrderType))