
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
    where t.name = 'ShipmentItems' and s.name = 'ryder'
)
begin
    create table ryder.ShipmentItems(
    ShipmentNbr varchar(10) not null,
    TrackingNbr varchar(55) not null,
    RyderID varchar(36) not null,
    ShipmentID varchar(11) not null,
    DeliveryType varchar(6),
    OrderType varchar(6),
    InventoryCD varchar(35) not null,
    Description varchar(155),
    Length int,
    Wdith int,
    Height int,
    Weight int,
    FAK int,
    CartonID varchar(55),
    Serial varchar(155),
    RANbr varchar(20),
    ClientLineID int,
    CosigneePO varchar(255),
    CosigneeOrd varchar(255),
    BrandCode varchar(255),
    TrackingID varchar(255),
    RLM_OrderNumber varchar(15),
    LastChecked datetime,
    InsertedDT datetime,
    primary key(ShipmentNbr, TrackingNbr, RyderID, ShipmentID, RLM_OrderNumber, InventoryCD)
    )
end