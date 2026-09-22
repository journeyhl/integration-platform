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
    where t.name = 'ARAdjust' and s.name = 'acu'
)
begin
    create table acu.ARAdjust(
    CustomerID varchar(30),
    AdjdDocType char(3) not null,
    AdjdType varchar(255),
    AdjdRefNbr varchar(15) not null,
    AdjgDocType char(3) not null,
    AdjgType varchar(255),
    AdjgRefNbr varchar(15) not null,
    AdjNbr int not null,
    AdjdOrderType char(2),
    AdjdOrderNbr varchar(15),
    AdjBatchNbr varchar(15),
    AdjgDocDate date,
    AdjdDocDate date,
    AdjgAmt decimal(18,2),
    AdjgDiscAmt decimal(18,2),
    AdjgPPDAmt decimal(18,2),
    AdjgWOAmt decimal(18,2),
    AdjdAmt decimal(18,2),
    AdjdOrigAmt decimal(18,2),
    AdjdDiscAmt decimal(18,2),
    AdjdPPDAmt decimal(18,2),
    AdjdWOAmt decimal(18,2),
    AdjAmt decimal(18,2),
    AdjDiscAmt decimal(18,2),
    AdjPPDAmt decimal(18,2),
    AdjWOAmt decimal(18,2),
    RGOLAmt decimal(18,2),
    WriteOffReasonCode varchar(60),
    Released bit,
    Hold bit,
    AdjdARAcct int,
    AdjdARAcctDescr varchar(60),
    AdjdARSub int,
    StatementDate date,
    AdjgFinPeriodID char(6),
    AdjdFinPeriodID char(6),
    AdjgTranPeriodID char(6),
    AdjdTranPeriodID char(6),
    Voided bit,
    VoidAdjNbr int,
    PendingPPD bit,
    AdjdHasPPDTaxes bit,
    TaxInvoiceNbr varchar(15),
    IsMigratedRecord bit,
    IsInitialApplication bit,
    Recalculatable bit,
    IsCCPayment bit,
    PaymentPendingProcessing bit,
    PaymentReleased bit,
    IsCCAuthorized bit,
    IsCCCaptured bit,
    PaymentCaptureFailed bit,
    Created_username varchar(355),
    Created_Name varchar(255),
    Created_ScreenID char(8),
    Created_Datetime datetime,
    LastMod_username varchar(355),
    LastMod_Name varchar(255),
    LastMod_ScreenID char(8),
    LastMod_Datetime datetime,
    NoteID uniqueidentifier,
    NoteID_Invoice uniqueidentifier,
    NoteID_Payment uniqueidentifier,
    NoteID_Memo uniqueidentifier,
    InsertedDT datetime,
    LastChecked datetime,
    primary key (AdjdDocType, AdjdRefNbr, AdjgDocType, AdjgRefNbr)
    )
end

