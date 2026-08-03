
if not exists(
    select *
    from sys.schemas s
    where s.name = 'inv'
)
begin
    exec('create schema inv');
end
if not exists(
    select * 
    from sys.tables t 
    inner join sys.schemas s on t.schema_id = s.schema_id
    where t.name = 'RMI_DetailSnapshot' and s.name = 'inv'
)
begin
	create table inv.RMI_DetailSnapshot(
	Location varchar(65) not null,
	InventoryCD varchar(40) not null,
	Qty int,
    Serials nvarchar(max),
	Timestamp datetime not null,
	primary key(Location, InventoryCD, Timestamp))
end