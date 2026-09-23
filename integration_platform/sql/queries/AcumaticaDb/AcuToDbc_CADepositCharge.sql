/**/
select dc.TranType TranType
	 , jt.Status Type
	 , dc.RefNbr RefNbr
	 , dc.LineNbr LineNbr
	 , dc.EntryTypeID EntryTypeID
	 , dc.DepositAcctID DepositAcctID
	 , dc.PaymentMethodID PaymentMethodID
	 , dc.AccountID AcctID
	 , rtrim(a.AccountCD) AcctCD
	 , a.Description AcctDescr
	 , dc.SubID SubID
	 , rtrim(s.SubCD) SubCD
	 , s.Description SubDescr
	 , dc.DrCr DrCr
	 , cast(dc.ChargeRate as decimal(18,2)) ChargeRate
	 , cast(dc.ChargeableAmt as decimal(18,2)) ChargeableAmt
	 , cast(dc.ChargeAmt as decimal(18,2)) ChargeAmt
     , coalesce(replace(uc.Email, '@journeyhl.com', ''), replace(uc.username, 'journeyhl.com\', '')) Created_Username
     , uc.FullName Created_Name
     , dc.CreatedByScreenID Created_ScreenID
     , dc.CreatedDateTime Created_Datetime
     , coalesce(replace(um.Email, '@journeyhl.com', ''), replace(um.username, 'journeyhl.com\', '')) LastMod_Username
     , um.FullName LastMod_Name
     , dc.LastModifiedByScreenID LastMod_ScreenID
     , dc.LastModifiedDateTime LastMod_Datetime
from CADepositCharge dc
left join Account a on dc.CompanyID = a.CompanyID and dc.AccountID = a.AccountID
left join Sub s on dc.CompanyID = s.CompanyID and dc.SubID = s.SubID
left join Users uc on dc.CompanyID = uc.CompanyID and dc.CreatedByID = uc.PKID
left join Users um on dc.CompanyID = um.CompanyID and dc.LastModifiedByID = um.PKID
left join JJStatusLookup jt on dc.TranType = jt.CStatus and jt.Tbl = 'CADeposit.TranType'
where dc.CompanyID = 2
