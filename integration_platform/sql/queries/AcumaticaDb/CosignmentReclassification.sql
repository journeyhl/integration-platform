
select b.Module
	 , jbt.Status BatchType
	 , jb.Status JournalStatus
	 , b.BatchNbr
	 , gt.LineNbr
	 , rtrim(a.AccountCD) AccountCD
	 , a.Description Account
	 , concat(left(rtrim(sa.SubCD), 3), '-', left(right(rtrim(sa.SubCD), 5), 3), '-', right(rtrim(sa.SubCD), 2)) FmtSubCD
	 , gt.RefNbr InvRefNbr
	 , cast(gt.TranDate as date) TranDate
	 , cast(gt.Qty as int) Qty
	 , cast(gt.DebitAmt as decimal(18,2)) DebitAmt
	 , cast(gt.CreditAmt as decimal(18,2)) CreditAmt
	 , rtrim(i.InventoryCD) InventoryCD
	 , gt.TranType
	 , cast(it.Qty as int) InvRef_Qty
	 , cast(it.UnitPrice as decimal(18,2)) InvRef_UnitPrice
	 , cast(it.UnitCost as decimal(18,2)) InvRef_UnitCost
	 , cast(it.TranAmt as decimal(18,2)) InvRef_TranTotalPrice
	 , cast(it.TranCost as decimal(18,2)) InvRef_TranTotalCost
	 , it.SOOrderType InvRef_OrderType
	 , it.SOOrderNbr InvRef_OrderNbr
	 , it.SOOrderLineNbr InvRef_OrderLineNbr
	 , it.SOShipmentNbr InvRef_ShipmentNbr
	 , it.SOShipmentLineNbr InvRef_ShipmentLineNbr
	 , i.Descr ItemDescr
	 , sa.Description SubAccount
	 , rtrim(sa.SubCD) SubCD
	 , gt.ReclassBatchModule
	 , gt.ReclassBatchNbr
	 --, *
from Batch b
inner join GLTran gt on b.CompanyID = gt.CompanyID and b.BranchID = gt.BranchID and b.Module = gt.Module and b.BatchNbr = gt.BatchNbr
inner join Account a on b.CompanyID = a.CompanyID and gt.AccountID = a.AccountID
inner join Sub sa on b.CompanyID = sa.CompanyID and gt.SubID = sa.SubID
inner join InventoryItem i on b.CompanyID = i.CompanyID and gt.InventoryID = i.InventoryID
inner join INRegister ir on b.CompanyID = ir.CompanyID and gt.RefNbr = ir.RefNbr 
inner join INTran it on b.CompanyID = it.CompanyID and ir.RefNbr = it.RefNbr and i.InventoryID = it.InventoryID and it.DocType = 'I' and it.TranType = 'INV'
inner join SOOrder s on b.CompanyID = s.CompanyID and it.SOOrderType = s.OrderType and it.SOOrderNbr = s.OrderNbr
inner join SOShipment sh on b.CompanyID = sh.CompanyID and it.SOShipmentNbr = sh.ShipmentNbr
inner join JJStatusLookup jbt on b.BatchType = jbt.CStatus and jbt.Tbl = 'Batch.Type'
inner join JJStatusLookup jb on b.BatchType = jb.CStatus and jb.Tbl = 'Batch'
where gt.CompanyID = 2 
and b.Module = 'IN'
--and b.BatchNbr = 'IN187088'
and s.OrderType = 'CO'
and it.UnitPrice = .01
and a.AccountCD = '5000'
and gt.ReclassBatchNbr is null

order by b.CreatedDateTime desc