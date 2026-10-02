
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
    where t.name = 'Territories' and s.name = 'hs'
)
begin
    create table hs.Territories(
    ObjectID int not null,
    TerritoryName varchar(35),
    TerritoryType varchar(35),
    OwnerID int,
    TeamID int,
    AllAssignedBusinessUnitIDs varchar(35),
    AllOwnerIDs varchar(55),
    AllTeamIDs varchar(55),
    AvatarFilemanagerKey varchar(55),
    CreatedByUserID int,
    CreateDate Date,
    Lastmodifieddate Date,
    MergedObjectIDs varchar(55),
    ObjectSource varchar(6),
    ObjectSourceDetail1 varchar(55),
    ObjectSourceDetail2 varchar(55),
    ObjectSourceDetail3 varchar(55),
    ObjectSourceID varchar(15),
    ObjectSourceLabel varchar(6),
    ObjectSourceUserID int,
    OwningTeams varchar(26),
    PinnedEngagementID varchar(55),
    ReadOnly varchar(55),
    SharedTeamIDs varchar(55),
    SharedUserIDs varchar(55),
    UniqueCreationKey varchar(55),
    UpdatedByUserID Date,
    UserIDsOfAllNotificationFollowers varchar(55),
    UserIDsOfAllNotificationRecipients varchar(8),
    UserIDsOfAllNotificationUnfollowers varchar(55),
    UserIDsOfAllOwners varchar(8),
    WasImported bit,
    OwnerAssigneddate Date,
    InsertedDT datetime,
    LastChecked datetime,
    primary key (ObjectID))
end