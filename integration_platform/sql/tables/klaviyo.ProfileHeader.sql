
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
    where t.name = 'ProfileHeader' and s.name = 'klaviyo'
)
begin
create table klaviyo.ProfileHeader(
ID varchar(26) not null primary key,
PhoneNumber varchar(10),
Email varchar(255),
FirstName varchar(255),
LastName varchar(255),
Name varchar(355),
Organization varchar(55),
Locale varchar(5),
RawPhoneNumber varchar(35),
Title varchar(35),
ExternalID varchar(95),
Created datetime,
Updated datetime,
JoinedGroupAt datetime,
LastEventDate datetime,
InsertedDT datetime,
LastChecked datetime,
)
end