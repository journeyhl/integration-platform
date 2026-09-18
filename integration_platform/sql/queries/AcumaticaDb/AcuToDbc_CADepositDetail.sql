select dd.TranType TranType
	 , dd.RefNbr RefNbr
	 , dd.LineNbr LineNbr
	 , dd.DetailType DetailType
	 , dd.OrigModule OrigModule
	 , dd.OrigDocType OrigDocType
	 , dd.OrigRefNbr OrigRefNbr
	 , dd.AccountID AccountID
	 , dd.CashAccountID CashAccountID
	 , cash.CashAccountCD
	 , cash.Descr CashAccountDescr
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
	 , dd.CreatedByID CreatedByID
	 , dd.CreatedByScreenID CreatedByScreenID
	 , dd.CreatedDateTime CreatedDateTime
	 , dd.LastModifiedByID LastModifiedByID
	 , dd.LastModifiedByScreenID LastModifiedByScreenID
	 , dd.LastModifiedDateTime LastModifiedDateTime
	 , dd.tstamp tstamp
from CADepositDetail dd
left join CashAccount cash on dd.CompanyID = cash.CompanyID and dd.CashAccountID = cash.CashAccountID
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