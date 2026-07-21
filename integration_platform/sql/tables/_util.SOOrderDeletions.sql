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
    where t.name = 'SOOrderDeletions' and s.name = '_util'
)
begin
    create table _util.SOOrderDeletions(
    OrderType varchar(2),
    OrderNbr varchar(15),
    DeletedBy varchar(200),
    DeletedDatetime datetime,
    primary key(OrderType, OrderNbr))
end