if not exists(
    select *
    from sys.schemas s
    where s.name = 'ucmi'
)
begin
    exec('create schema ucmi');
end
if not exists(
    select * 
    from sys.tables t 
    inner join sys.schemas s on t.schema_id = s.schema_id
    where t.name = 'DarwillHubspotBinding' and s.name = 'ucmi'
)
begin
    create table ucmi.DarwillHubspotBinding(
    CustomerID varchar(30),
    HubspotID bigint,
    ANI varchar(15),
    Product varchar(55),
    ContactName varchar(355),
    AddressLine1 varchar(355),
    AddressLine2 varchar(355),
    City varchar(155),
    State varchar(3),
    Zip varchar(12),
    UnformattedANI varchar(20),
    SourceFile varchar(155),
    DateAdded datetime,
    primary key(ANI))
end