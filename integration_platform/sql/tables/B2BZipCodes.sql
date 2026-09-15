
if not exists(
    select *
    from sys.schemas s
    where s.name = '_dev'
)
begin
    exec('create schema _dev');
end
if not exists(
    select * 
    from sys.tables t 
    inner join sys.schemas s on t.schema_id = s.schema_id
    where t.name = 'B2BZipCodes' and s.name = '_dev'
)
begin
create table _dev.B2BZipCodes(
Zip varchar(5) not null,
Lat decimal(18,5),
Lng decimal(18,5),
City varchar(45),
StateID varchar(4),
State varchar(45),
Population int,
Density decimal(18,1),
CountyFIPS varchar(6),
CountyName varchar(30),
CountyWeights varchar(93),
AllCountyNames varchar(63),
AllCountyFIPS varchar(35),
Imprecise bit,
Military bit,
Timezone varchar(30),
Inside varchar(15),
Field varchar(15),
InsertedDT datetime,
LastChecked datetime,
primary key(Zip)
)
end

