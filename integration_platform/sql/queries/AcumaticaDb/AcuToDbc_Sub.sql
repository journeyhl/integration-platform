with TopLevel as(
select s.SubID
	 , rtrim(s.SubCD) SubCD
	 , s.Active
	 , s.Description
	 , s.DeletedDatabaseRecord
     , coalesce(replace(uc.Email, '@journeyhl.com', ''), replace(uc.username, 'journeyhl.com\', '')) Created_Username
     , uc.FullName Created_Name
     , s.CreatedByScreenID Created_ScreenID
     , s.CreatedDateTime Created_Datetime
     , coalesce(replace(um.Email, '@journeyhl.com', ''), replace(um.username, 'journeyhl.com\', '')) LastMod_Username
     , um.FullName LastMod_Name
     , s.LastModifiedByScreenID LastMod_ScreenID
     , s.LastModifiedDateTime LastMod_Datetime
	, s.NoteID
from Sub s
left join Users uc on s.CompanyID = uc.CompanyID and s.CreatedByID = uc.PKID
left join Users um on s.CompanyID = um.CompanyID and s.LastModifiedByID = um.PKID
where s.CompanyID = 2
)
select t.SubID
     , t.SubCD
     , concat(left(t.SubCD, 3), '-', left(right(t.SubCD, 5), 2), '-', right(t.SubCD, 3)) SubUI
     , t.Active
     , t.Description
     , t.DeletedDatabaseRecord
     , t.Created_Username
     , t.Created_Name
     , t.Created_ScreenID
     , t.LastMod_Username
     , t.LastMod_Name
     , t.LastMod_ScreenID
     , t.LastMod_Datetime
     , t.NoteID
from TopLevel t