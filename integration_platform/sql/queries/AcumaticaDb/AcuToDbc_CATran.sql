select c.OrigModule
	 , c.OrigTranType
	 , j.Status Type
	 , c.OrigRefNbr
	 , c.ExtRefNbr
     , c.CashAccountID CashAcctID
     , rtrim(cash.CashAccountCD) CashAcctCD
     , cash.Descr CashAcctDescr
	 , c.TranID
	 , cast(c.TranDate as date) TranDate
	 , c.DrCr
	 , c.ReferenceID RefID
	 , c.TranDesc
	 , c.Hold
	 , c.Released
	 , c.Voided
	 , c.Reconciled
	 , cast(c.ReconDate as date) ReconDate
	 , c.ReconNbr
	 , cast(c.TranAmt as decimal(18,2)) TranAmt
	 , c.BatchNbr
	 , c.IsPaymentChargeTran
	 , c.OrigLineNbr
	 , c.TranPeriodID
	 , c.FinPeriodID
	 , c.Cleared
	 , cast(c.ClearDate as date) ClearDate
	 , c.Posted
	 , c.VoidedTranID
     , coalesce(replace(uc.Email, '@journeyhl.com', ''), replace(uc.username, 'journeyhl.com\', '')) Created_Username
     , uc.FullName Created_Name
     , c.CreatedByScreenID Created_ScreenID
     , c.CreatedDateTime Created_Datetime
     , coalesce(replace(um.Email, '@journeyhl.com', ''), replace(um.username, 'journeyhl.com\', '')) LastMod_Username
     , um.FullName LastMod_Name
     , c.LastModifiedByScreenID LastMod_ScreenID
     , c.LastModifiedDateTime LastMod_Datetime
	 , c.NoteID
from CATran c
left join Users uc on c.CompanyID = uc.CompanyID and c.CreatedByID = uc.PKID
left join Users um on c.CompanyID = um.CompanyID and c.LastModifiedByID = um.PKID
left join CashAccount cash on c.CompanyID = cash.CompanyID and c.CashAccountID = cash.CashAccountID
left join JJStatusLookup j on c.OrigTranType = j.CStatus and j.Tbl = 'CATran.OrigTranType'
where c.CompanyID = 2
and dateadd(hour, -4, c.LastModifiedDateTime) >= dateadd(day, -1, getdate())