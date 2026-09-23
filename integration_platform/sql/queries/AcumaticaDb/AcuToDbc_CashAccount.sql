/*Pulls details and settings of cash accounts from AcumaticaDb
*/
select c.CashAccountID CashAcctID
	 , rtrim(c.CashAccountCD) CashAcctCD
	 , c.Descr
	 , c.Active
	 , c.AccountID AcctID
	 , rtrim(a.AccountCD) AcctCD
	 , a.Description AcctDescr
	 , c.SubID
	 , c.ExtRefNbr
	 , c.ClearingAccount
	 , c.UseForCorpCard
	 , c.ReceiptTranDaysBefore
	 , c.ReceiptTranDaysAfter
	 , c.DisbursementTranDaysBefore
	 , c.DisbursementTranDaysAfter
	 , c.AllowMatchingCreditMemo
	 , cast(c.RefNbrCompareWeight as decimal(18,2)) RefNbrCompareWeight
	 , cast(c.EmptyRefNbrMatching as decimal(18,2)) EmptyRefNbrMatching
	 , cast(c.DateCompareWeight as decimal(18,2)) DateCompareWeight
	 , cast(c.PayeeCompareWeight as decimal(18,2)) PayeeCompareWeight
	 , cast(c.DateMeanOffset as decimal(18,2)) DateMeanOffset
	 , cast(c.DateSigma as decimal(18,2)) DateSigma
	 , cast(c.CuryDiffThreshold as decimal(18,2)) CuryDiffThreshold
	 , cast(c.AmountWeight as decimal(18,2)) AmountWeight
	 , c.SkipVoided
	 , c.MatchSettingsPerAccount
	 , cast(c.MatchThreshold as decimal(18,2)) MatchThreshold
	 , cast(c.RelativeMatchThreshold as decimal(18,2)) RelativeMatchThreshold
	 , c.InvoiceFilterByDate
	 , c.DaysBeforeInvoiceDiscountDate
	 , c.DaysBeforeInvoiceDueDate
	 , c.DaysAfterInvoiceDueDate
	 , c.InvoiceFilterByCashAccount
	 , cast(c.InvoiceRefNbrCompareWeight as decimal(18,2)) InvoiceRefNbrCompareWeight
	 , cast(c.InvoiceDateCompareWeight as decimal(18,2)) InvoiceDateCompareWeight
	 , cast(c.InvoicePayeeCompareWeight as decimal(18,2)) InvoicePayeeCompareWeight
	 , cast(c.AveragePaymentDelay as decimal(18,2)) AveragePaymentDelay
	 , cast(c.InvoiceDateSigma as decimal(18,2)) InvoiceDateSigma
	 , c.Reconcile
	 , c.ReferenceID
	 , c.ReconNumberingID
	 , c.Signature
	 , c.SignatureDescr
	 , c.StatementImportTypeName
	 , c.RestrictVisibilityWithBranch
	 , c.MatchToBatch
	 , c.AllowMatchingDebitAdjustment
     , coalesce(replace(uc.Email, '@journeyhl.com', ''), replace(uc.username, 'journeyhl.com\', '')) Created_Username
     , uc.FullName Created_Name
     , c.CreatedByScreenID Created_ScreenID
     , c.CreatedDateTime Created_Datetime
     , coalesce(replace(um.Email, '@journeyhl.com', ''), replace(um.username, 'journeyhl.com\', '')) LastMod_Username
     , um.FullName LastMod_Name
     , c.LastModifiedByScreenID LastMod_ScreenID
     , c.LastModifiedDateTime LastMod_Datetime
	 , c.NoteID
from CashAccount c
left join Account a on c.CompanyID = a.CompanyID and c.AccountID = a.AccountID
left join Sub s on c.CompanyID = s.CompanyID and c.SubID = s.SubID
left join Users uc on c.CompanyID = uc.CompanyID and c.CreatedByID = uc.PKID
left join Users um on c.CompanyID = um.CompanyID and c.LastModifiedByID = um.PKID
where c.CompanyID = 2
