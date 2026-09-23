select rtrim(b.AcctCD) CustomerID
	 , a.AdjdDocType
	 , jd.Status AdjdType
	 , a.AdjdRefNbr
	 , a.AdjgDocType
	 , jg.Status AdjgType
	 , a.AdjgRefNbr
	 , a.AdjNbr
	 , a.AdjdOrderType
	 , a.AdjdOrderNbr
	 , a.AdjBatchNbr
	 , cast(a.AdjgDocDate as date) AdjgDocDate
	 , cast(a.AdjdDocDate as date) AdjdDocDate
	 , cast(a.CuryAdjgAmt as decimal(18,2)) CuryAdjgAmt
	 , cast(a.CuryAdjgDiscAmt as decimal(18,2)) CuryAdjgDiscAmt
	 , cast(a.CuryAdjgPPDAmt as decimal(18,2)) CuryAdjgPPDAmt
	 , cast(a.CuryAdjgWOAmt as decimal(18,2)) CuryAdjgWOAmt
	 , cast(a.CuryAdjdAmt as decimal(18,2)) CuryAdjdAmt
	 , cast(a.CuryAdjdOrigAmt as decimal(18,2)) CuryAdjdOrigAmt
	 , cast(a.CuryAdjdDiscAmt as decimal(18,2)) CuryAdjdDiscAmt
	 , cast(a.CuryAdjdPPDAmt as decimal(18,2)) CuryAdjdPPDAmt
	 , cast(a.CuryAdjdWOAmt as decimal(18,2)) CuryAdjdWOAmt
	 , cast(a.AdjAmt as decimal(18,2)) AdjAmt
	 , cast(a.AdjDiscAmt as decimal(18,2)) AdjDiscAmt
	 , cast(a.AdjPPDAmt as decimal(18,2)) AdjPPDAmt
	 , cast(a.AdjWOAmt as decimal(18,2)) AdjWOAmt
	 , cast(a.RGOLAmt as decimal(18,2)) RGOLAmt
	 , a.WriteOffReasonCode
	 , a.Released
	 , a.Hold
	 , a.AdjdARAcct
	 , aa.Description
	 , a.AdjdARSub
	 , cast(a.StatementDate as date) StatementDate
	 , a.AdjgFinPeriodID
	 , a.AdjdFinPeriodID
	 , a.AdjgTranPeriodID
	 , a.AdjdTranPeriodID
	 , a.Voided
	 , a.VoidAdjNbr
	 , a.PendingPPD
	 , a.AdjdHasPPDTaxes
	 , a.TaxInvoiceNbr
	 , a.IsMigratedRecord
	 , a.IsInitialApplication
	 , a.Recalculatable
	 , a.IsCCPayment
	 , a.PaymentPendingProcessing
	 , a.PaymentReleased
	 , a.IsCCAuthorized
	 , a.IsCCCaptured
	 , a.PaymentCaptureFailed
     , coalesce(replace(uc.Email, '@journeyhl.com', ''), replace(uc.username, 'journeyhl.com\', '')) Created_Username
     , uc.FullName Created_Name
     , a.CreatedByScreenID Created_ScreenID
     , a.CreatedDateTime Created_Datetime
     , coalesce(replace(um.Email, '@journeyhl.com', ''), replace(um.username, 'journeyhl.com\', '')) LastMod_Username
     , um.FullName LastMod_Name
     , a.LastModifiedByScreenID LastMod_ScreenID
     , a.LastModifiedDateTime LastMod_Datetime
	 , a.NoteID
	 , a.InvoiceID NoteID_Invoice
	 , a.PaymentID NoteID_Payment
	 , a.MemoID NoteID_Memo
from ARAdjust a
inner join Users uc on a.CompanyID = uc.CompanyID and a.CreatedByID = uc.PKID
inner join Users um on a.CompanyID = um.CompanyID and a.LastModifiedByID = um.PKID
inner join BAccount b on a.CompanyID = b.CompanyID and a.CustomerID = b.BAccountID
left join JJStatusLookup jd on a.AdjdDocType = jd.CStatus and jd.tbl = 'ARRegister.DocType'
left join JJStatusLookup jg on a.AdjgDocType = jg.CStatus and jg.tbl = 'ARRegister.DocType'
left join Account aa on a.CompanyID = aa.CompanyID and a.AdjdARAcct = aa.AccountID
left join Sub sa on a.CompanyID = sa.CompanyID and a.AdjdARSub = sa.SubID
where a.CompanyID = 2