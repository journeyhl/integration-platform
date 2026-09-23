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
    where t.name = 'CADeposit' and s.name = 'acu'
)
begin
    create table acu.CADeposit(
    TranType char(3) not null,
    Type varchar(55),
    RefNbr varchar(15) not null,
    ExtRefNbr varchar(40),
    CashAcctID int,
    CashAcctCD varchar(10),
    CashAcctDescr varchar(60),
    TranDate date,
    DrCr char(1),
    TranDesc varchar(256),
    TranPeriodID char(6),
    FinPeriodID char(6),
    Hold bit,
    Voided bit,
    Status varchar(35),
    StatusCD char(1),
    Released bit,
    TranAmt decimal(18,2),
    TranID bigint,
    Cleared bit,
    ClearDate date,
    LineCntr int,
    LineCntrCharge int,
    ExtraCashTotal decimal(18,2),
    ChargeTotal decimal(18,2),
    DetailTotal decimal(18,2),
    ControlAmt decimal(18,2),
    ChargesSeparate bit,
    ExtraCashAccountID int,
    CashTranID bigint,
    ChargeTranID bigint,
    Created_Username varchar(355),
    Created_Name varchar(255),
    Created_ScreenID char(8),
    Created_Datetime datetime,
    LastMod_Username varchar(355),
    LastMod_Name varchar(255),
    LastMod_ScreenID char(8),
    LastMod_Datetime datetime,
    NoteID uniqueidentifier,
    InsertedDT datetime,
    LastChecked datetime,
    primary key(TranType, RefNbr))
end