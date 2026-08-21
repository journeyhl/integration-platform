
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
    where t.name = 'ShipmentEvents' and s.name = 'ryder'
)
begin
    create table ryder.ShipmentEvents(
    ShipmentNbr varchar(10) not null,
    TrackingNbr varchar(55) not null,
    RyderID varchar(36) not null,
    ShipmentID varchar(11) not null,
    DeliveryType varchar(6),
    OrderType varchar(6),
    EventID int not null,
    EventNbr int not null,
    Code varchar(10),
    Reason varchar(10),
    Description varchar(155),
    Comments varchar(255),
    Location varchar(35),
    Datetime datetime,
    RLM_OrderNumber varchar(10) not null,
    LastChecked datetime,
    InsertedDT datetime,
    primary key(ShipmentNbr, TrackingNbr, RyderID, ShipmentID, EventID, EventNbr, RLM_OrderNumber)
    )
end
