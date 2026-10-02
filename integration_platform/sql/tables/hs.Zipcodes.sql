
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
    where t.name = 'Zipcodes' and s.name = 'hs'
)
begin
create table hs.Zipcodes(
ZipCode varchar(10) not null,
CompanyAssociations int,
Territory varchar(35),
Territory1 varchar(35),
TerritoryOwner int,
TerritoryType varchar(35),
City varchar(55),
State varchar(10),
County varchar(55),
DataNotes nvarchar(max),
DataSource varchar(255),
Households65plus100kEst int,
Households65plus100kMoe int,
AllAccessibleTeamIDs varchar(55),
AllAssignedBusinessUnitIDs varchar(55),
AllOwnerIDs varchar(55),
AllTeamIDs varchar(55),
AvatarFilemanagerKey varchar(55),
CreatedByUserID varchar(55),
CreateDate Date,
Lastmodifieddate Date,
MergedObjectIDs varchar(55),
ObjectID varchar(55),
ObjectSource varchar(55),
ObjectSourceDetail1 varchar(20),
ObjectSourceDetail2 varchar(55),
ObjectSourceDetail3 varchar(55),
ObjectSourceID int,
ObjectSourceLabel varchar(55),
ObjectSourceUserID varchar(55),
OwningTeams varchar(55),
PinnedEngagementID varchar(55),
ReadOnly varchar(55),
SharedTeamIDs varchar(55),
SharedUserIDs varchar(55),
UniqueCreationKey varchar(55),
UpdatedByUserID Date,
UserIDsOfAllNotificationFollowers varchar(55),
UserIDsOfAllNotificationRecipients varchar(55),
UserIDsOfAllNotificationUnfollowers varchar(55),
UserIDsOfAllOwners varchar(55),
WasImported bit,
HubspotOwnerAssigneddate Date,
HubspotOwnerID varchar(55),
HubspotTeamID varchar(55),
Income100kCountRank int,
InsideTerritory varchar(35),
LastEnrichedAt varchar(55),
OutsideTerritory varchar(55),
Plus65Rank int,
Population65plusEst int,
Population65plusMoe int,
PopulationTotal int,
InsertedDT datetime,
LastChecked datetime,
primary key(Zipcode))
end
