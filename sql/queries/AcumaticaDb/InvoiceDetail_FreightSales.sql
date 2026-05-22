

with TopLevel as(
select distinct concat(right(art.FinPeriodID, 2), '-', left(art.FinPeriodID, 4)) FinPeriodID
	 , ai.DocType
	 , ai.RefNbr
	 , cast(art.TranDate as date) InvoiceDate
	 , null ConfirmedDate
	 , case when a.AccountCD = '4005' then cast(s.FreightAmt as decimal(18,2)) else cast(art.CuryTranAmt as decimal(18,2)) end CuryTranAmt
	 , a.AccountCD
	 , a.Description Account
	 , concat(left(sa.SubCD, 3), '-', left(right(sa.SubCD, 5), 3), '-', right(sa.SubCD, 2)) SubAccountID
	 , sa.Description SubAccount
	 , rtrim(i.InventoryCD) InventoryCD
	 , i.Descr
	 , ir.ReplenishmentClassID
	 , b.AcctCD
	 , b.AcctName
	 , s.OrderType
	 , s.OrderNbr
	 , null ShipmentNbr
	 , null ShipDate
	 , js.Status OrderStatus
	 , null ShipStatus
	 
from SOOrder s
inner join BAccount b on s.CompanyID = b.CompanyID and s.CustomerID = b.BAccountID
left join SOOrderShipment sos on s.CompanyID = sos.CompanyID and s.OrderType = sos.OrderType and s.OrderNbr = sos.OrderNbr
left join ARInvoice ai on s.CompanyID = ai.CompanyID and sos.InvoiceType = ai.DocType and sos.InvoiceNbr = ai.RefNbr
left join ARTran art on s.CompanyID = art.CompanyID  and ai.DocType = art.TranType and ai.RefNbr = art.RefNbr and s.OrderNbr = art.SOOrderNbr

left join InventoryItem i on s.CompanyID = i.CompanyID and art.InventoryID = i.InventoryID and art.InventoryID = i.InventoryID
left join Account a on s.CompanyID = a.CompanyID and art.AccountID = a.AccountID
left join Sub sa on s.CompanyID = sa.CompanyID and art.SubID = sa.SubID
left join INItemRep ir on s.CompanyID = ir.CompanyID and i.InventoryID = ir.InventoryID
left join JJStatusLookup js on s.Status = js.CStatus and js.Tbl = 'SOOrder'
where s.CompanyID = 2 and 
art.RefNbr is not null
and art.SOOrderLineNbr is null
)
select *
from TopLevel
order by InvoiceDate desc, RefNbr
