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
    where t.name = 'Account' and s.name = 'acu'
)
begin
	create table acu.Account(
	AcctID int not null,
	AcctCD varchar(10) not null,
	AccountingType char(1),
	TypeCD char(1) not null,
	Type varchar(9),
	AcctClassID varchar(20),
	Description varchar(60),
	Active bit,
	COAOrder smallint,
	PostOption char(1),
	DirectPost bit,
	AllowManualEntry bit,
	RequireUnits bit,
	NoSubDetail bit,
	isCashAccount bit,
	ControlAccountModule char(2),
	DeletedDatabaseRecord bit,
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
	primary key(AcctID, AcctCD, TypeCD))
end