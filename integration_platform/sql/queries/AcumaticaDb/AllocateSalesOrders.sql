
with TopLevel as(
select s.OrderType
	 , s.OrderNbr
	 , l.LineNbr
	 , rtrim(i.InventoryCD) InventoryCD
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
from SOOrder s
inner join SOLine l on s.CompanyID = l.CompanyID and s.OrderNbr = l.OrderNbr and s.OrderType = l.OrderType and s.CustomerID = l.CustomerID
inner join SOLineSplit sp on s.CompanyID = sp.CompanyID and s.OrderType = sp.OrderType and s.OrderNbr = sp.OrderNbr and l.InventoryID = sp.InventoryID and l.LineNbr = sp.LineNbr
inner join InventoryItem i on s.CompanyID = i.CompanyID and l.InventoryID = i.InventoryID
inner join INSite si on s.CompanyID = si.CompanyID and l.SiteID = si.SiteID
inner join JJStatusLookup j on s.Status = j.CStatus and j.Tbl = 'SOOrder'
where s.CompanyID = 2
and s.OrderType = 'WB'
and si.SiteCD = 'RMI'
and s.Status not in ('L')
--and s.Status = 'H'
and l.POCreate = 0
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
select *
from SecondLevel s
where param_Action is not null