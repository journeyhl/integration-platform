if not exists(
    select *
    from sys.schemas s
    where s.name = 'ucmiraw'
)
begin
    exec('create schema ucmiraw');
end
if not exists(
    select * 
    from sys.tables t 
    inner join sys.schemas s on t.schema_id = s.schema_id
    where t.name = 'Customers_Acu' and s.name = 'ucmiraw'
)
begin
	create table ucmiraw.Customers_Acu(
		CustomerID varchar(10) not null,
		Customer varchar(255),
		ContactName varchar(255),
		CustomerClassID varchar(5),
		AddressLine1 varchar(255),
		AddressLine2 varchar(255),
		City varchar(155),
		State varchar(15),
		PostalCode varchar(15),
		CountryID varchar(3),
		Phone varchar(12),
		Email varchar(255),
		SalespersonCD varchar(30),
		Salesperson varchar(155),
		Terms varchar(10),
		CreatedDateTime datetime,
		CreatedByUser varchar(95),
		CreatedByName varchar(95),
		LastModifiedDateTime datetime,
		LastModifiedByUser varchar(95),
		LastModifiedByName varchar(95),
		BAccountID bigint,
		AddressID bigint,
		ContactID_B2B bigint,
		ContactID_D2C bigint,
		HubspotLink varchar(255),
		InsertedDT datetime,
		LastChecked datetime,
		primary key(CustomerID))
end
