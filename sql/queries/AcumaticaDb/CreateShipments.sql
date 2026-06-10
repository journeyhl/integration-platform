

select distinct s.OrderType							OrderType
	 , s.OrderNbr 									OrderNbr
     , (
        select count(distinct sl.SiteID) 
        from SOline sl 
        inner join INSite si2 on s.CompanyID = si2.CompanyID and sl.SiteID = si2.SiteID
        where s.CompanyID = sl.CompanyID and s.OrderNbr = sl.OrderNbr and s.OrderType = sl.OrderType and si2.SiteCD != 'NONSTOCK'
       ) OrderShippableLines
	 , js.Status 									Status
	 , rtrim(si.SiteCD) 							Warehouse
	 , r.ReplenishmentClassID 						ReplenishmentClass
	 , i.StkItem 									StockItem
     , rtrim(b.AcctCD)                              AcctCD
	 
from SOOrder s
inner join SOLine l on s.CompanyID = l.CompanyID and s.OrderNbr = l.OrderNbr and s.OrderType = l.OrderType and s.CustomerID = l.CustomerID
inner join INSite si on s.CompanyID = si.CompanyID and l.SiteID = si.SiteID /*Warehouse joined on SOLine*/
inner join InventoryItem i on s.CompanyID = i.CompanyID and l.InventoryID = i.InventoryID
left join INItemRep r on s.CompanyID = r.CompanyID and i.InventoryID = r.InventoryID
inner join BAccount b on s.CustomerID = b.BAccountID and s.CompanyID = b.CompanyID 

left join Users uc on s.CompanyID = uc.CompanyID and s.CreatedByID = uc.PKID
left join Users um on s.CompanyID = um.CompanyID and s.LastModifiedByID = um.PKID
inner join JJStatusLookup js on s.Status = js.CStatus and js.Tbl = 'SOOrder'
where s.CompanyID = 2 
and s.OrderType not in('QT', 'RA', 'RC', 'RR', 'RM', 'RT')
and js.Status in('Open')
and r.ReplenishmentClassID != 'DROPSHIP' 
and i.InventoryCD != '27222'
and i.StkItem = 1
and l.Completed != 1
and l.POCreate != 1
--and s.OrderNbr in('')
--and s.Status in('')
--and o.AcctName in('')
--and sh.ShipmentNbr in('')
--and sh.Status in('')
--and InventoryCD in('')
--and i.Descr like '%%'
--and b.AcctCD in('')
--and b.AcctName like '%%'
--and c.CustomerClassID in('')
-- and s.OrderNbr = 'PH145626'
order by OrderType, OrderNbr, OrderShippableLines

/*
Updated Query to only pull sales orders from the last two hours.
s.LastModifiedDateTime
*/
