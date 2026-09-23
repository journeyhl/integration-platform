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
    where t.name = 'CADepositDetail' and s.name = 'acu'
)
begin
    create table acu.CADepositDetail(
    TranType char(3) not null,
    Type varchar(55),
    RefNbr varchar(15) not null,
    LineNbr int not null,
    DetailType char(3),
    OrigModule char(2),
    OrigDocType char(3),
    OrigRefNbr varchar(15),
    AccountID int,
    CashAcctID int,
    CashAcctCD varchar(10),
    CashAcctDescr varchar(60),
    SubID int,
    PaymentMethodID varchar(10),
    DrCr char(1),
    TranDesc varchar(256),
    Released bit,
    OrigAmt decimal(18,2),
    OrigDrCr char(1),
    TranAmt decimal(18,2),
    ChargeEntryTypeID varchar(10),
    TranID bigint,
    Created_Username varchar(355),
    Created_Name varchar(255),
    Created_ScreenID char(8),
    Created_Datetime datetime,
    LastMod_Username varchar(355),
    LastMod_Name varchar(255),
    LastMod_ScreenID char(8),
    LastMod_Datetime datetime,
    InsertedDT datetime,
    LastChecked datetime,
    primary key(TranType, RefNbr, LineNbr))
end