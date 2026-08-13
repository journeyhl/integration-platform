
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
    where t.name = 'OrderEvents' and s.name = 'ryder'
)
begin
    create table ryder.OrderEvents(
    ShipmentNbr varchar(15) not null,
    TrackingNbr varchar(55) not null,
    RyderID varchar(36) not null,
    EventNbr int not null,
    StatusCode varchar(10),
    Description varchar(65),
    City varchar(55),
    State varchar(5),
    Zip varchar(12),
    DatetimeLocal datetime,
    DatetimeUTC datetime,
    LastChecked datetime,
    InsertedDT datetime,
    primary key(ShipmentNbr, RyderID, TrackingNbr, EventNbr)
    )
end