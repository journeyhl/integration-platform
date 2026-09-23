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
    where t.name = 'CATran' and s.name = 'acu'
)
begin
	create table acu.CATran(
	OrigModule char(2) not null,
	OrigTranType char(3) not null,
	Type varchar(255),
	OrigRefNbr varchar(15) not null,
	ExtRefNbr varchar(40),
	CashAcctID int,
	CashAcctCD varchar(10),
	CashAcctDescr varchar(60),
	TranID bigint not null,
	TranDate date,
	DrCr char(1),
	RefID int,
	TranDesc varchar(512),
	Hold bit,
	Released bit,
	Voided bit,
	Reconciled bit,
	ReconDate date,
	ReconNbr varchar(15),
	TranAmt decimal(18,2),
	BatchNbr varchar(15),
	IsPaymentChargeTran bit,
	OrigLineNbr int,
	TranPeriodID char(6),
	FinPeriodID char(6),
	Cleared bit,
	ClearDate date,
	Posted bit,
	VoidedTranID bigint,
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
	primary key(OrigModule, OrigTranType, OrigRefNbr, TranID))
end