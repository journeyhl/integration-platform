with TopLevel as(
select ar.DocType DocType
	 , jdt.Status Type
	 , ar.RefNbr RefNbr
	 , ar.BatchNbr BatchNbr
	 , rtrim(b.AcctcD) CustomerID
	 , b.AcctName Customer
	 , ar.ARAccountID ARAccountID
	 , rtrim(a.AccountCD) ARAccountCD
	 , a.Description ARAccountDesc
	 , ar.ARSubID
	 , cast(ar.DocDate as date) DocDate
	 , cast(ar.OrigDocDate as date) OrigDocDate
	 , ar.DocDesc DocDesc
	 , cast(ar.OrigDocAmt as decimal(18,2)) OrigDocAmt
	 , cast(ar.DocBal as decimal(18,2)) DocBal
	 , cast(ar.InitDocBal as decimal(18,2)) InitDocBal
	 , cast(ar.DiscBal as decimal(18,2)) DiscBal
	 , cast(ar.DiscTaken as decimal(18,2)) DiscTaken
	 , cast(ar.ChargeAmt as decimal(18,2)) ChargeAmt
	 , j.Status Status
	 , rtrim(ar.Status) StatusCD
	 , cast(ar.DueDate as date) DueDate
	 , cast(ar.StatementDate as date) StatementDate
	 , ar.FinPeriodID FinPeriodID
	 , ar.TranPeriodID TranPeriodID
	 , ar.ClosedTranPeriodID ClosedTranPeriodID
	 , ar.ClosedFinPeriodID ClosedFinPeriodID
	 , cast(ar.ClosedDate as date) ClosedDate
	 , ar.OpenDoc OpenDoc
	 , ar.Released Released
	 , ar.Hold Hold
	 , cast(ar.OrigDiscAmt as decimal(18,2)) OrigDiscAmt
	 , ar.SalesPersonID SalesPersonID
	 , rtrim(sp.SalespersonCD) SalespersonCD
	 , ar.OrigModule OrigModule
	 , ar.OrigDocType OrigDocType
	 , ar.OrigRefNbr OrigRefNbr
	 , case when ar.DisableAutomaticTaxCalculation is null then 0 else ar.DisableAutomaticTaxCalculation end DisableAutomaticTaxCalculation
	 , ar.TaxCalcMode TaxCalcMode
	 , ar.IsTaxValid IsTaxValid
	 , ar.IsTaxSaved IsTaxSaved
	 , ar.IsTaxPosted IsTaxPosted
	 , ar.NonTaxable NonTaxable
	 , ar.LineCntr LineCntr
	 , ar.AdjCntr AdjCntr
	 , ar.Voided Voided
	 , ar.Scheduled Scheduled
	 , ar.PendingProcessing PendingProcessing
	 , ar.HasPPDTaxes HasPPDTaxes
	 , ar.PendingPPD PendingPPD
	 , ar.PaymentsByLinesAllowed PaymentsByLinesAllowed
	 , ar.Approved Approved
	 , ar.Rejected Rejected
	 , ar.DontApprove DontApprove
	 , ar.IsCancellation IsCancellation
	 , ar.IsCorrection IsCorrection
	 , ar.IsUnderCorrection IsUnderCorrection
	 , ar.Canceled Canceled
	 , ar.PendingPayment PendingPayment
	 , ar.DontPrint DontPrint
	 , ar.Printed Printed
	 , ar.DontEmail DontEmail
	 , ar.Emailed Emailed
	 , ar.DeletedDatabaseRecord DeletedDatabaseRecord
	 , ar.IsMigratedRecord IsMigratedRecord
	 , ar.ExternalRef ExternalRef
	 , ar.ApproverID ApproverID
	 , ar.ApproverWorkGroupID ApproverWorkGroupID
     , coalesce(replace(uc.Email, '@journeyhl.com', ''), replace(uc.username, 'journeyhl.com\', '')) Created_Username
     , uc.FullName Created_Name
     , ar.CreatedByScreenID Created_ScreenID
     , ar.CreatedDateTime Created_Datetime
     , coalesce(replace(um.Email, '@journeyhl.com', ''), replace(um.username, 'journeyhl.com\', '')) LastMod_Username
     , um.FullName LastMod_Name
     , ar.LastModifiedByScreenID LastMod_ScreenID
     , ar.LastModifiedDateTime LastMod_Datetime
	 , ar.NoteID NoteID
from ARRegister ar
inner join Users uc on ar.CompanyID = uc.CompanyID and ar.CreatedByID = uc.PKID
inner join Users um on ar.CompanyID = um.CompanyID and ar.LastModifiedByID = um.PKID
inner join BAccount b on ar.CompanyID = b.CompanyID and ar.CustomerID = b.BAccountID
inner join Account a on ar.CompanyID = a.CompanyID and ar.ARAccountID = a.AccountID
inner join JJStatusLookup j on ar.Status = j.CStatus and j.tbl = 'ARRegister'
inner join JJStatusLookup jdt on ar.DocType = jdt.CStatus and jdt.tbl = 'ARRegister.DocType'
left join SalesPerson sp on ar.CompanyID = sp.CompanyID and ar.SalesPersonID = sp.SalespersonID
where ar.CompanyID = 2
and dateadd(hour, -4, ar.LastModifiedDateTime) >= dateadd(day, -1, getdate())
)
select *
from TopLevel