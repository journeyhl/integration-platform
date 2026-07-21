if not exists(
    select *
    from sys.schemas s
    where s.name = 'analytics'
)
begin
    exec('create schema analytics');
end
if not exists(
    select * 
    from sys.tables t 
    inner join sys.schemas s on t.schema_id = s.schema_id
    where t.name = 'JHL_B2BCollectionsDetail' and s.name = 'analytics'
)
begin
    create table analytics.JHL_B2BCollectionsDetail(
    CustomerID varchar(15) not null,
    CustomerName varchar(255),
    RefNbr varchar(15) not null,
    OrigRefNbr varchar(15),
    DocDate Date,
    DueDate Date,
    DocStatus varchar(25),
    DaysOverdue int,
    CurrentBalance decimal(18,2),
    Balance_1_30d decimal(18,2),
    Balance_31_60d decimal(18,2),
    Balance_61_90d decimal(18,2),
    Balance_90d decimal(18,2),
    TotalBalance decimal(18,2),
    SalespersonID varchar(15),
    TermsID varchar(12),
    CustomerStatus varchar(15),
    State varchar(20),
    Phone varchar(30),
    Email varchar(255),
    SendStatementByEmail bit,
    InvoicePhone1 varchar(30),
    InvoiceEmail varchar(255),
    Phone1 varchar(30),
    Phone2 varchar(30),
    Phone3 varchar(30),
    InvoicePhone_Coalesce varchar(30),
    InvoicePhone2 varchar(30),
    InvoicePhone3 varchar(30),
    InsertedDT Datetime,
    LastChecked Datetime,
    primary key(CustomerID, RefNbr))
end