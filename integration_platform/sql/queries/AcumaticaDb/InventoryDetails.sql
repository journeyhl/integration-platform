
select rtrim(s.SiteCD) SiteCD
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