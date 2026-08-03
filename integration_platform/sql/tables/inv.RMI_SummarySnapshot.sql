
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
    where t.name = 'RMI_SummarySnapshot' and s.name = 'inv'
)
begin
	create table inv.RMI_SummarySnapshot(
	InventoryCD varchar(40) not null,
	Qty int,
	Timestamp datetime not null,
	primary key(InventoryCD, Timestamp))
end