
if not exists(
    select *
    from sys.schemas s
    where s.name = 'hs'
)
begin
    exec('create schema hs');
end
if not exists(
    select * 
    from sys.tables t 
    inner join sys.schemas s on t.schema_id = s.schema_id
    where t.name = 'Properties' and s.name = 'hs'
)
begin
	create table hs.Properties(
	ObjectType varchar(45) not null,
	otName varchar(45),
	Name varchar(255) not null,
	Label varchar(255),
	GroupName varchar(255),
	Description varchar(max),
	Type varchar(35),
	FieldType varchar(35),
	CreatedUserId int,
	UpdatedUserId int,
	DisplayOrder int,
	Calculated bit,
	Archived bit,
	Hidden bit,
	HubspotDefined bit,
	CreatedAt datetime,
	UpdatedAt datetime,
	InsertedDT datetime,
	LastChecked datetime,
	primary key(ObjectType, Name))

end