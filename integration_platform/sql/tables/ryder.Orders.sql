
if not exists(
    select *
    from sys.schemas s
    where s.name = 'ryder'
)
begin
    exec('create schema ryder');
end
if not exists(
    select * 
    from sys.tables t 
    inner join sys.schemas s on t.schema_id = s.schema_id
    where t.name = 'Orders' and s.name = 'ryder'
)
begin
    create table ryder.Orders(
    RLM_OrderNumber varchar(10) not null,
    TrackingNbr varchar(55) not null,
    ShipmentNbr varchar(10) not null,
    RyderID varchar(36) not null,
    OrderType varchar(2),
    OrderNbr varchar(12),
    CurrentEventNbr int,
    CurrentStatusCode varchar(10),
    CurrentStatusDescr varchar(55),
    CurrentCity varchar(100),
    StatusDatetimeUTC datetime,
    ShipName varchar(30),
    ShipAddress1 varchar(100),
    ShipAddress2 varchar(100),
    ShipAddress3 varchar(100),
    ShipAddress4 varchar(100),
    ShipCity varchar(100),
    ShipState varchar(5),
    ShipZip varchar(12),
    ShipEmail varchar(50),
    ShipPhone varchar(10),
    CountShipments int,
    LastChecked datetime,
    InsertedDT datetime,
    primary key(RLM_OrderNumber, TrackingNbr, ShipmentNbr, RyderID)
    )
end