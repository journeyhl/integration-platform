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
    where t.name = 'CashAccount' and s.name = 'acu'
)
begin
	create table acu.CashAccount(
	CashAcctID int not null,
	CashAcctCD varchar(10) not null,
	Descr varchar(60),
	Active bit,
	AcctID int,
	AcctCD varchar(10),
	AcctDescr varchar(60),
	SubID int,
	ExtRefNbr varchar(40),
	ClearingAccount bit,
	UseForCorpCard bit,
	ReceiptTranDaysBefore int,
	ReceiptTranDaysAfter int,
	DisbursementTranDaysBefore int,
	DisbursementTranDaysAfter int,
	AllowMatchingCreditMemo bit,
	RefNbrCompareWeight decimal(18,2),
	EmptyRefNbrMatching decimal(18,2),
	DateCompareWeight decimal(18,2),
	PayeeCompareWeight decimal(18,2),
	DateMeanOffset decimal(18,2),
	DateSigma decimal(18,2),
	CuryDiffThreshold decimal(18,2),
	AmountWeight decimal(18,2),
	SkipVoided bit,
	MatchSettingsPerAccount bit,
	MatchThreshold decimal(18,2),
	RelativeMatchThreshold decimal(18,2),
	InvoiceFilterByDate bit,
	DaysBeforeInvoiceDiscountDate int,
	DaysBeforeInvoiceDueDate int,
	DaysAfterInvoiceDueDate int,
	InvoiceFilterByCashAccount bit,
	InvoiceRefNbrCompareWeight decimal(18,2),
	InvoiceDateCompareWeight decimal(18,2),
	InvoicePayeeCompareWeight decimal(18,2),
	AveragePaymentDelay decimal(18,2),
	InvoiceDateSigma decimal(18,2),
	Reconcile bit,
	ReferenceID int,
	ReconNumberingID varchar(10),
	Signature varchar(255),
	SignatureDescr varchar(60),
	StatementImportTypeName varchar(255),
	RestrictVisibilityWithBranch bit,
	MatchToBatch bit,
	AllowMatchingDebitAdjustment bit,
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
	primary key(CashAcctID, CashAcctCD))
end