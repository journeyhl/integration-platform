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
    where t.name = 'CADepositCharge' and s.name = 'acu'
)
begin
	create table acu.CADepositCharge(
	TranType char(3) not null,
	Type varchar(255),
	RefNbr varchar(15) not null,
	LineNbr int not null,
	EntryTypeID varchar(10),
	DepositAcctID int,
	PaymentMethodID varchar(10),
	AcctID int,
	AcctCD varchar(10),
	AcctDescr varchar(60),
	SubID int,
	SubCD varchar(30),
	SubDescr varchar(255),
	DrCr char(1),
	ChargeRate decimal(18,2),
	ChargeableAmt decimal(18,2),
	ChargeAmt decimal(18,2),
	Created_username varchar(355),
	Created_Name varchar(255),
	Created_ScreenID char(8),
	Created_Datetime datetime,
	LastMod_username varchar(355),
	LastMod_Name varchar(255),
	LastMod_ScreenID char(8),
	LastMod_Datetime datetime,
	primary key(TranType, RefNbr, LineNbr))
end