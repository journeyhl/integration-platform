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
    where t.name = 'JHL_AdPhone' and s.name = 'analytics'
)
begin
    create table analytics.JHL_AdPhone(
	AdCode varchar(10) NOT NULL,
	TFN varchar(15) NOT NULL,
	StartDate date NOT NULL,
	Priority int NULL,
	MatchingAdCodeDate int NULL,
	EndDate date NULL,
	Category varchar(55) NULL,
	PrimaryAdName varchar(255) NULL,
	SecondaryAdName varchar(255) NULL,
	Product varchar(65) NULL,
	AdVersionID varchar(35) NULL,
	PrimaryVersionName varchar(255) NULL,
	SecondaryVersionName varchar(255) NULL,
	InsertedDT datetime NULL,
	LastChecked datetime NULL,
    primary key(AdCode,	TFN, StartDate))

end