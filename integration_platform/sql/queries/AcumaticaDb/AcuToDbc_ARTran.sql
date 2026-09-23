select a.TranType
	 , case when a.TranType = 'CRM' then 'Credit Memo' when a.TranType = 'DRM' then 'Debit Memo' when a.TranType = 'INV' then 'Invoice' else null end Type
	 , a.RefNbr
	 , a.LineNbr
	 , a.SortOrder
	 , a.AccountID AcctID
	 , rtrim(aa.AccountCD) AcctCD
	 , a.SubID
	 , a.AccrueCost
	 , a.CostBasis
	 , cast(a.TranAmt as decimal(18,2)) TranAmt
	 , cast(a.CashDiscBal as decimal(18,2)) CashDiscBal
	 , cast(a.OrigRetainageAmt as decimal(18,2)) OrigRetainageAmt
	 , cast(a.RetainageBal as decimal(18,2)) RetainageBal
	 , cast(a.OrigTranAmt as decimal(18,2)) OrigTranAmt
	 , cast(a.TranBal as decimal(18,2)) TranBal
	 , cast(a.TaxableAmt as decimal(18,2)) TaxableAmt
	 , cast(a.TaxAmt as decimal(18,2)) TaxAmt
	 , cast(a.OrigTaxableAmt as decimal(18,2)) OrigTaxableAmt
	 , cast(a.OrigTaxAmt as decimal(18,2)) OrigTaxAmt
	 , cast(a.RetainedTaxableAmt as decimal(18,2)) RetainedTaxableAmt
	 , cast(a.RetainedTaxAmt as decimal(18,2)) RetainedTaxAmt
	 , cast(a.Qty as int) Qty
	 , cast(a.BaseQty as int) BaseQty
	 , cast(a.AccruedCost as decimal(18,2)) AccruedCost
	 , cast(a.TranCost as decimal(18,2)) TranCost
	 , cast(a.TranCostOrig as decimal(18,2)) TranCostOrig
	 , a.IsTranCostFinal
	 , cast(a.ExtPrice as decimal(18,2)) ExtPrice
	 , cast(a.LineAmt as decimal(18,2)) LineAmt
	 , a.DiscountsAppliedToLine
	 , a.OrigLineNbr
	 , cast(a.OrigGroupDiscountRate as decimal(18,2)) OrigGroupDiscountRate
	 , cast(a.OrigDocumentDiscountRate as decimal(18,2)) OrigDocumentDiscountRate
	 , cast(a.GroupDiscountRate as decimal(18,2)) GroupDiscountRate
	 , cast(a.DocumentDiscountRate as decimal(18,2)) DocumentDiscountRate
	 , a.TranClass
	 , a.DrCr
	 , cast(a.TranDate as date) TranDate
	 , cast(a.OrigInvoiceDate as date) OrigInvoiceDate
	 , a.TranDesc
	 , a.Released
	 , a.InventoryID
	 , a.SiteID
	 , a.ReasonCode
	 , a.LineType
	 , a.TaxCategoryID
	 , a.AvalaraCustomerUsageType
	 , cast(a.UnitPrice as decimal(18,2)) UnitPrice
	 , a.SalesPersonID
	 , rtrim(sp.SalespersonCD) SalespersonCD
	 , a.EmployeeID
	 , cast(a.CommnPct as decimal(18,2)) CommnPct
	 , cast(a.CommnAmt as decimal(18,2)) CommnAmt
	 , a.Commissionable
	 , a.FinPeriodID
	 , a.TranPeriodID
	 , rtrim(b.AcctCD) CustomerID
	 , a.SOOrderType
	 , a.SOOrderNbr
	 , a.SOOrderLineNbr
	 , a.SOOrderLineOperation
	 , a.SOOrderSortOrder
	 , a.SOShipmentType
	 , a.SOShipmentNbr
	 , a.SOShipmentLineNbr
	 , a.DiscountID
	 , a.DiscountSequenceID
	 , cast(a.DiscPct as decimal(18,2)) DiscPct 
	 , cast(a.DiscAmt as decimal(18,2)) DiscAmt 
	 , a.ManualPrice
	 , a.AutomaticDiscountsDisabled
	 , a.ManualDisc
	 , a.DisableAutomaticTaxCalculation
	 , a.SkipLineDiscounts
	 , a.OrigDocType
	 , a.OrigRefNbr
	 , a.LocationID
	 , a.OrigInvoiceType
	 , a.OrigInvoiceNbr
	 , a.OrigInvoiceLineNbr
	 , a.InvtDocType
	 , a.InvtRefNbr
	 , a.IsStockItem
	 , a.IsCancellation
	 , a.Canceled
	 , a.SubstitutionRequired
	 , a.SOOrderLineSign
	 , a.InvtReleased
	 , a.SOShipmentLineGroupNbr
     , coalesce(replace(uc.Email, '@journeyhl.com', ''), replace(uc.username, 'journeyhl.com\', '')) Created_Username
     , uc.FullName Created_Name
     , a.CreatedByScreenID Created_ScreenID
     , a.CreatedDateTime Created_Datetime
     , coalesce(replace(um.Email, '@journeyhl.com', ''), replace(um.username, 'journeyhl.com\', '')) LastMod_Username
     , um.FullName LastMod_Name
     , a.LastModifiedByScreenID LastMod_ScreenID
     , a.LastModifiedDateTime LastMod_Datetime
	 , a.NoteID
from ARTran a
left join Users uc on a.CompanyID = uc.CompanyID and a.CreatedByID = uc.PKID
left join Users um on a.CompanyID = um.CompanyID and a.LastModifiedByID = um.PKID
left join BAccount b on a.CompanyID = b.CompanyID and a.CustomerID = b.BAccountID
left join Account aa on a.CompanyID = aa.CompanyID and a.AccountID = aa.AccountID
left join SalesPerson sp on a.CompanyID = sp.CompanyID and a.SalesPersonID = sp.SalespersonID
where a.CompanyID = 2

