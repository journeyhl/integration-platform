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
    where t.name = 'Sub' and s.name = 'acu'
)
begin
	create table acu.Sub(
	SubID int not null,
	SubCD varchar(30),
	SubUI varchar(10),
	Active bit,
	Description varchar(255),
	DeletedDatabaseRecord bit,
	Created_Username varchar(355),
	Created_Name varchar(255),
	Created_ScreenID char(8),
	LastMod_Username varchar(355),
	LastMod_Name varchar(255),
	LastMod_ScreenID char(8),
	LastMod_Datetime datetime,
	NoteID uniqueidentifier,
    InsertedDT datetime,
    LastChecked datetime,
	primary key(SubID))
end