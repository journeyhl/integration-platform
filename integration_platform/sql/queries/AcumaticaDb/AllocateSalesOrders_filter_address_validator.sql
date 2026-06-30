
with TopLevel as(
select s.OrderType
	 , s.OrderNbr
	 , l.LineNbr
	 , rtrim(i.InventoryCD) InventoryCD
     , i.Descr
	 , rtrim(si.SiteCD) SiteCD
	 , cast(l.OrderQty as int) QtyOrdered
	 , cast(l.ShippedQty as int) QtyShipped
	 , sp.IsAllocated
	 , j.Status jStatus
	 , s.Status aStatus
	 , cast(s.OrderDate as date) OrderDate
	 , case when l.OrderQty = l.ShippedQty or l.Completed = 1 or s.Status in('C', 'F', 'I')
				then 1
			else 0 
	   end Shipped
     , si.SiteID
from SOOrder s
inner join SOLine l on s.CompanyID = l.CompanyID and s.OrderNbr = l.OrderNbr and s.OrderType = l.OrderType and s.CustomerID = l.CustomerID
inner join SOLineSplit sp on s.CompanyID = sp.CompanyID and s.OrderType = sp.OrderType and s.OrderNbr = sp.OrderNbr and l.InventoryID = sp.InventoryID and l.LineNbr = sp.LineNbr
inner join InventoryItem i on s.CompanyID = i.CompanyID and l.InventoryID = i.InventoryID
inner join INSite si on s.CompanyID = si.CompanyID and l.SiteID = si.SiteID
inner join JJStatusLookup j on s.Status = j.CStatus and j.Tbl = 'SOOrder'
where s.CompanyID = 2
and s.OrderType = 'WB'
and si.SiteCD = 'RMI'
and s.Status not in ('L', 'C', 'S')
--and s.Status = 'H'
and l.POCreate = 0
)
, InventoryLevels as(
select s.SiteCD
	 , s.SiteID
	 , l.LocationID
	 , i.InventoryID
	 , rtrim(l.LocationCD) LocationCD
	 , rtrim(i.InventoryCD) InventoryCD
	 , i.Descr
	 , cast(ls.QtyOnHand as int) QtyOnHand
	 , cast(ls.QtyAvail as int) QtyAvail
	 , cast(ls.QtyHardAvail as int) QtyHardAvail
	 , cast(ls.QtyActual as int) QtyActual
	 , cast(ls.QtySOPrepared as int) QtySOPrepared
	 , cast(ls.QtySOBooked as int) QtySOBooked
	 , cast(ls.QtySOShipped as int) QtySOShipped
	 , cast(ls.QtySOShipping as int) QtySOShipping
	 , cast(ls.QtySODropShip as int) QtySODropShip
	 , cast(ls.QtySOBackOrdered as int) QtySOBackOrdered
	 , cast(ls.QtyPOOrders as int) QtyPOOrders
	 , cast(ls.QtyPOPrepared as int) QtyPOPrepared
	 , cast(ls.QtyPOReceipts as int) QtyPOReceipts
	 , cast(ls.QtyPODropShipOrders as int) QtyPODropShipOrders
	 , cast(ls.QtyPODropShipPrepared as int) QtyPODropShipPrepared
	 , cast(ls.QtyPODropShipReceipts as int) QtyPODropShipReceipts
	 , cast(ls.QtyINIssues as int) QtyINIssues
	 , cast(ls.QtyINReceipts as int) QtyINReceipts
	 , cast(ls.QtyInTransit as int) QtyInTransit
	 , cast(ls.QtyInTransitToSO as int) QtyInTransitToSO

from INLocationStatusByCostCenter ls
inner join INLocation l on ls.CompanyID = l.CompanyID and ls.LocationID = l.LocationID and ls.SiteID = l.SiteID
inner join INSite s on ls.CompanyID = s.CompanyID and ls.SiteID = s.SiteID and l.SiteID = s.SiteID
inner join InventoryItem i on ls.CompanyID = i.CompanyID and ls.InventoryID = i.InventoryID
where ls.CompanyID = 2
and s.SiteCD = 'RMI'
and LocationCD = 'DEFAULT'
)
, SecondLevel as(
select *
	 , case when t.Shipped = 0 and t.IsAllocated = 0 
				then 'Allocate Sales Orders'
			when t.Shipped = 1 and t.IsAllocated = 1
				then 'Deallocate Sales Orders'
			else null
	   end param_Action
from TopLevel t
)
select s.*
     , i.QtyAvail
     , i.QtyActual
     , i.QtyOnHand
from SecondLevel s
left join InventoryLevels i on s.InventoryCD = i.InventoryCD and s.SiteCD = i.SiteCD
where param_Action is not null and s.IsAllocated = 0
order by OrderNbr