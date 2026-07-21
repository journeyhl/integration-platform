if not exists(
    select *
    from sys.schemas s
    where s.name = 'acu'
)
begin
    exec('create schema acu');
end
if not exists(
    select * 
    from sys.tables t 
    inner join sys.schemas s on t.schema_id = s.schema_id
    where t.name = 'Customers' and s.name = 'acu'
)
begin
    create table acu.Customers(
    CustomerID varchar(10) not null,
    CustomerClass varchar(5),
    ContactName varchar(1000),
    AccountName varchar(1000),
    AddressLine1 varchar(50),
    AddressLine2 varchar(50),
    City varchar(30),
    State varchar(25),
    Zip varchar(15),
    Country varchar(2),
    Phone varchar(20),
    Email varchar(100),
    Terms varchar(10),
    AccountID int,
    ContactID int,
    CUSTEDP varchar(100),
    SalesPersonID varchar(65),
    SalesPersonName varchar(50),
    CreatedOn datetime,
    CreatedBy varchar(60),
    InsertedDT datetime,
    LastModifiedDT datetime,
    Phone2 varchar(20),
    LastChecked datetime,
    Primary Key(CustomerID))
end