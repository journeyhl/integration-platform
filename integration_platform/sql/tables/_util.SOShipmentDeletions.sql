if not exists(
    select *
    from sys.schemas s
    where s.name = '_util'
)
begin
    exec('create schema _util');
end
if not exists(
    select * 
    from sys.tables t 
    inner join sys.schemas s on t.schema_id = s.schema_id
    where t.name = 'SOShipmentDeletions' and s.name = '_util'
)
begin
    create table _util.SOShipmentDeletions(
    ShipmentNbr varchar(15),
    ShipDate date,
    DeletedBy varchar(200),
    DeletedDatetime datetime,
    primary key(ShipmentNbr))
end