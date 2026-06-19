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
where t.name = 'Shipments' and s.name = 'acu'
)
create table acu.Shipments(
ShipmentNbr varchar(10) not null,
ShipLineNbr int not null,
Status varchar(20),
OrderNbr varchar(10) not null,
OrderLineNbr int not null,
OrderDate date,
InventoryCD varchar(30),
OrderQTY int,
ShipQTY int,
ShipDate date,
CustomerID varchar(20),
AccountName varchar(300),
Email varchar(200),
AddressLine1 varchar(500),
AddressLine2 varchar(455),
City varchar(30),
State varchar(25),
Country varchar(2),
Zip varchar(15),
WarehouseID varchar(20),
PackageCount int,
SOLinePrice float,
FreightCost float,
SenttoWH bit,
InsertedDT datetime,
LastModifiedDT datetime,
Tracking varchar(455),
TrackingCreatedDate datetime,
CustomerPhone varchar(50),
Attention varchar(300),
ShipVia varchar(100),
Carrier varchar(50),
CourierCode varchar(100),
CourierName varchar(100),
ConfirmedDatetime datetime,
CreatedDatetime datetime,
SentToWHDatetime datetime,
PackageDescr varchar(355),
CreatedBy varchar(65),
LastModifiedBy varchar(65),
LastChecked datetime,
Primary Key(ShipmentNbr, ShipLineNbr, OrderNbr, OrderLineNbr))