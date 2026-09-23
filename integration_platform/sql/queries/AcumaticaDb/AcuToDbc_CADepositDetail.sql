select dd.TranType TranType
	 , jt.Status Type
	 , dd.RefNbr RefNbr
	 , dd.LineNbr LineNbr
	 , dd.DetailType DetailType
	 , dd.OrigModule OrigModule
	 , dd.OrigDocType OrigDocType
	 , dd.OrigRefNbr OrigRefNbr
	 , dd.AccountID AccountID
	 , dd.CashAccountID CashAcctID
	 , rtrim(cash.CashAccountCD) CashAcctCD
	 , cash.Descr CashAcctDescr
	 , dd.SubID SubID
	 , dd.PaymentMethodID PaymentMethodID
	 , dd.DrCr DrCr
	 , dd.TranDesc TranDesc
	 , dd.Released Released
	 , cast(dd.OrigAmt as decimal(18,2)) OrigAmt
	 , dd.OrigDrCr OrigDrCr
	 , cast(dd.TranAmt as decimal(18,2)) TranAmt
	 , dd.ChargeEntryTypeID ChargeEntryTypeID
	 , dd.TranID TranID
	 , coalesce(replace(uc.Email, '@journeyhl.com', ''), replace(uc.username, 'journeyhl.com\', '')) Created_Username
	 , uc.FullName Created_Name
	 , dd.CreatedByScreenID Created_ScreenID
	 , dd.CreatedDateTime Created_Datetime
	 , coalesce(replace(um.Email, '@journeyhl.com', ''), replace(um.username, 'journeyhl.com\', '')) LastMod_Username
	 , um.FullName LastMod_Name
	 , dd.LastModifiedByScreenID LastMod_ScreenID
	 , dd.LastModifiedDateTime LastMod_Datetime
from CADepositDetail dd
left join CashAccount cash on dd.CompanyID = cash.CompanyID and dd.CashAccountID = cash.CashAccountID
left join Users uc on dd.CompanyID = uc.CompanyID and dd.CreatedByID = uc.PKID
left join Users um on dd.CompanyID = um.CompanyID and dd.LastModifiedByID = um.PKID
left join JJStatusLookup jt on dd.TranType = jt.CStatus and jt.Tbl = 'CADeposit.TranType'
where dd.CompanyID = 2

/*
select *
from CashAccount a
where a.CompanyID = 2
and a.CashAccountID = 11

select *
from Account a
where a.CompanyID = 2
and a.AccountID = 267
*/