/*Pulls Chart of Account data from AcumaticaDb*/
select a.AccountID AcctID
	 , rtrim(a.AccountCD) AcctCD
	 , a.AccountingType
	 , rtrim(a.Type) TypeCD
	 , case when a.Type = 'A' then 'Asset'
			when a.Type = 'L' then 'Liability'
			when a.Type = 'E' then 'Expense'
			when a.Type = 'I' then 'Income'
		else null end Type
	 , a.AccountClassID AcctClassID
	 , a.Description
	 , a.Active
	 , a.COAOrder
	 , a.PostOption
	 , a.DirectPost
	 , a.AllowManualEntry
	 , a.RequireUnits
	 , a.NoSubDetail
	 , a.isCashAccount
	 , a.ControlAccountModule
	 , a.DeletedDatabaseRecord
     , coalesce(replace(uc.Email, '@journeyhl.com', ''), replace(uc.username, 'journeyhl.com\', '')) Created_Username
     , uc.FullName Created_Name
     , a.CreatedByScreenID Created_ScreenID
     , a.CreatedDateTime Created_Datetime
     , coalesce(replace(um.Email, '@journeyhl.com', ''), replace(um.username, 'journeyhl.com\', '')) LastMod_Username
     , um.FullName LastMod_Name
     , a.LastModifiedByScreenID LastMod_ScreenID
     , a.LastModifiedDateTime LastMod_Datetime
	 , a.NoteID
from Account a
left join Users uc on a.CompanyID = uc.CompanyID and a.CreatedByID = uc.PKID
left join Users um on a.CompanyID = um.CompanyID and a.LastModifiedByID = um.PKID
where a.CompanyID = 2
