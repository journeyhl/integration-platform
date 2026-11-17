
if not exists(
    select *
    from sys.schemas s
    where s.name = 'klaviyo'
)
begin
    exec('create schema klaviyo');
end
if not exists(
    select * 
    from sys.tables t 
    inner join sys.schemas s on t.schema_id = s.schema_id
    where t.name = 'NewsletterAdditions' and s.name = 'klaviyo'
)
begin
    create table klaviyo.NewsletterAdditions(
    ID varchar(26) not null,
    Timestamp datetime,
    primary key (ID))
end