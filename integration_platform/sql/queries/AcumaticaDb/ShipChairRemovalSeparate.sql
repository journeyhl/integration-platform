
with TopLevel as(
select s.OrderType
	 , cast(s.OrderDate as date) DatePlaced
	 , s.OrderNbr
	 , l.LineNbr 
	 , rtrim(i.InventoryCD) InventoryCD
     , rtrim(i.Descr) Description
	 , r.ReplenishmentClassID ReplenishmentClass
	 , js.Status Status
	 , i.StkItem StockItem
	 , rtrim(si.SiteCD) OrderLineWH
	 , si.SiteID
	 , s.Status AcuStatus
	 , s.ShipSeparately
	 , rtrim(b.AcctCD) AcctCD
from SOOrder s
inner join SOLine l on s.CompanyID = l.CompanyID and s.OrderNbr = l.OrderNbr and s.OrderType = l.OrderType and s.CustomerID = l.CustomerID
left join INSite si on s.CompanyID = si.CompanyID and l.SiteID = si.SiteID /*Warehouse joined on SOLine*/
left join INSite sip on s.CompanyID = sip.CompanyID and l.POSiteID = sip.SiteID
inner join InventoryItem i on s.CompanyID = i.CompanyID and l.InventoryID = i.InventoryID
left join INItemRep r on s.CompanyID = r.CompanyID and i.InventoryID = r.InventoryID
inner join JJStatusLookup js on s.Status = js.CStatus and js.Tbl = 'SOOrder'
inner join BAccount b on s.CustomerID = b.BAccountID and s.CompanyID = b.CompanyID 
where s.CompanyID = 2 and s.OrderType != 'QT'
--and si.SiteID = 80
and s.Status not in('C', 'L', 'S')
)
, SecondLevel as(
select *
	 , (select 1 from TopLevel t2 where t.OrderNbr = t2.OrderNbr and t.LineNbr != t2.LineNbr and t2.InventoryCD = '27222') ChairRemoval
from TopLevel t
where t.OrderLineWH = 'RLM NEJ HB'
and t.InventoryCD != '27222'
)
select *
from SecondLevel
where ChairRemoval is not null 
and ShipSeparately = 1 --ShipSeperately needs to be flipped to 0 as a result of this process.
--and AcuStatus = 'N'