
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
    where t.name = 'raw_SalesSummary' and s.name = 'analytics'
)
begin
    create table analytics.raw_SalesSummary(
    OrderType varchar(3) not null,
    OrderNbr varchar(10) not null,
    DatePlaced date,
    CustomerID varchar(15) not null,
    CustomerClass varchar(3),
    InventoryCD varchar(30),
    Qty int,
    LinePrice float,
    DiscountAmt float,
    Revenue float,
    Status varchar(30),
    CustTypeBucket varchar(6),
    Channel varchar(6),
    Shipped int not null,
    Booked int not null,
    ItemDescr varchar(100),
    ItemClassDescr varchar(100),
    PostingClass varchar(15),
    ItemType varchar(20),
    LineCost float,
    Salesperson varchar(100),
    LineNbr int not null,
    Lines int,
    CustomerName varchar(300),
    ShipmentNbr varchar(255),
    Total_WarrantyRevenue float,
    Date_Month int,
    Date_Year int,
    FinPeriod varchar(26) not null,
    InsertedDT datetime,
    LastChecked datetime,
    Primary key(OrderType, OrderNbr, CustomerID, LineNbr))
end