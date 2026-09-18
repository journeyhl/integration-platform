select dc.TranType TranType
	 , dc.RefNbr RefNbr
	 , dc.LineNbr LineNbr
	 , dc.EntryTypeID EntryTypeID
	 , dc.DepositAcctID DepositAcctID
	 , dc.PaymentMethodID PaymentMethodID
	 , dc.AccountID AccountID
	 , dc.SubID SubID
	 , dc.DrCr DrCr
	 , cast(dc.ChargeRate as decimal(18,2)) ChargeRate
	 , cast(dc.ChargeableAmt as decimal(18,2)) ChargeableAmt
	 , cast(dc.ChargeAmt as decimal(18,2)) ChargeAmt
	 , dc.CreatedByID CreatedByID
	 , dc.CreatedByScreenID CreatedByScreenID
	 , dc.CreatedDateTime CreatedDateTime
	 , dc.LastModifiedByID LastModifiedByID
	 , dc.LastModifiedByScreenID LastModifiedByScreenID
	 , dc.LastModifiedDateTime LastModifiedDateTime
from CADepositCharge dc
where dc.CompanyID = 2
