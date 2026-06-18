

with TopLevel as(
select concat(right(art.FinPeriodID, 2), '-', left(art.FinPeriodID, 4)) FinPeriodID
	 , ai.DocType
	 , ai.RefNbr
	 , cast(art.TranDate as date) InvoiceDate
	 , cast(sh.ConfirmedDateTime as date) ConfirmedDate
	 , cast(art.CuryTranAmt as decimal(18,2)) CuryTranAmt
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
	 , sh.ShipmentNbr
	 , cast(sh.ShipDate as date) ShipDate
	 , js.Status OrderStatus
	 , jsh.Status ShipStatus
	 , art.SOOrderLineSign
	 
from SOOrder s
inner join SOLine sl on s.CompanyID = sl.CompanyID and s.OrderNbr = sl.OrderNbr and s.OrderType = sl.OrderType
inner join BAccount b on s.CompanyID = b.CompanyID and s.CustomerID = b.BAccountID
left join SOShipLine shl on s.CompanyID = shl.CompanyID and s.OrderNbr = shl.OrigOrderNbr and s.OrderType = shl.OrigOrderType and sl.LineNbr = shl.OrigLineNbr
left join SOShipment sh on s.CompanyID = sh.CompanyID and shl.ShipmentNbr = sh.ShipmentNbr and shl.ShipmentType = sh.ShipmentType
left join SOOrderShipment sos on s.CompanyID = sos.CompanyID and s.OrderType = sos.OrderType and s.OrderNbr = sos.OrderNbr and sh.ShipmentNbr = sos.ShipmentNbr
left join ARInvoice ai on s.CompanyID = ai.CompanyID and sos.InvoiceType = ai.DocType and sos.InvoiceNbr = ai.RefNbr
left join ARTran art on s.CompanyID = art.CompanyID  and ai.DocType = art.TranType and ai.RefNbr = art.RefNbr and shl.LineNbr = SOShipmentLineNbr and sl.LineNbr = art.SOOrderLineNbr
left join InventoryItem i on s.CompanyID = i.CompanyID and art.InventoryID = i.InventoryID and art.InventoryID = i.InventoryID
left join Account a on s.CompanyID = a.CompanyID and art.AccountID = a.AccountID
left join Sub sa on s.CompanyID = sa.CompanyID and art.SubID = sa.SubID
left join INItemRep ir on s.CompanyID = ir.CompanyID and i.InventoryID = ir.InventoryID
left join JJStatusLookup jsh on sh.Status = jsh.CStatus and jsh.Tbl = 'SOShipment'
left join JJStatusLookup js on s.Status = js.CStatus and js.Tbl = 'SOOrder'
where s.CompanyID = 2 and 
art.RefNbr is not null
and art.SOOrderLineNbr is not null
)
select *
from TopLevel
order by InvoiceDate desc, RefNbr

