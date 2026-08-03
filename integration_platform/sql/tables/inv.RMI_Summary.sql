
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
    where t.name = 'RMI_Summary' and s.name = 'inv'
)
begin
    create table inv.RMI_Summary(
    InventoryCD varchar(40) not null,
    Qty int,
    InsertedDT datetime,
    LastChecked datetime,
    primary key(InventoryCD))
end