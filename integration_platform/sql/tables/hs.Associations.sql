
if not exists(
    select *
    from sys.schemas s
    where s.name = 'hs'
)
begin
    exec('create schema hs');
end
if not exists(
    select * 
    from sys.tables t 
    inner join sys.schemas s on t.schema_id = s.schema_id
    where t.name = 'Associations' and s.name = 'hs'
)
begin
    create table hs.Associations(
    Type varchar(35) not null,
    Parent bigint not null,
    Child bigint not null,
    InsertedDT datetime,
    LastChecked datetime,
    primary key (Type, Parent, Child))

end