with acuSalesOrders as(

select s.OrderType									OrderType
	 , s.OrderNbr 									OrderNumber
	 , l.LineNbr  									LineNbr 
	 , cast(s.OrderDate as date) 					DatePlaced
	 , rtrim(b.AcctCD) 								CustomerID
	 , b.AcctName 									CustomerName
	 , c.CustomerClassID 							CustomerClass
	 , rtrim(i.InventoryCD) 						InventoryCD
     , rtrim(i.Descr) 								Description
     , cast(l.OrderQty as int) as 					Quantity
	 , cast(l.LineAmt + l.DiscAmt  as decimal(18,2))LinePrice
	 , cast(s.OrderTotal as decimal(18,2)) 			OrderTotal
	 , js.Status 									Status
	 , s.CustomerOrderNbr 							CustOrderNumber
	 , rtrim(o.AcctCD) 								D2CSalesperson
	 , o.AcctName 									SalespersonName
	 , oc.EMail										SalespersonEmail
	 , rtrim(sp.SalespersonCD) 						B2BSalesperson
     , s.LastModifiedDateTime						LastModifiedDT
	 , rtrim(l.DiscountID)							DiscountCode
	 , cast(l.DiscAmt  as decimal(18,2))			DiscountAmt
	 , cast(l.ExtCost as decimal(18,2)) 			LineCost
	 , left(coalesce(sc.Phone1, bc.Phone1), 20)		Phone
	 , coalesce(sc.Email, bc.Email)					Email
	 , coalesce(sa.AddressLine1, ba.AddressLine1)	AddressLine1
	 , case when coalesce(sa.AddressLine2,
       ba.AddressLine2) = ''then null 
       else coalesce(sa.AddressLine2,ba.AddressLine2) end 	AddressLine2
	 , coalesce(sa.City, ba.City)		 				City
	 , coalesce(sa.State, ba.State)		 				State
	 , coalesce(sa.PostalCode, ba.PostalCode)			Zip
	 , coalesce(sa.CountryID, ba.CountryID)	 			Country
	 , cast(l.LineAmt  as decimal(18,2)) 				LineAmount
	 , r.ReplenishmentClassID 							ReplenishmentClass
	 , i.StkItem 										StockItem
	 , rtrim(si.SiteCD) 								OrderLineWH
	 , sh.ShipDate										ShipDate
	 , sh.ShipmentNbr 									ShipmentNbr
	 , jsh.[Status] 									ShipStatus
	 , rtrim(shi.SiteCD)								ShipmentWH
	 , l.Completed										Completed
	 , l.OrigOrderType 									OriginalOrderType
	 , l.OrigOrderNbr 									OriginalOrderNbr
	 , cast(s.CuryFreightAmt as decimal(18,2))			FreightPrice
	 , cast(s.CuryPremiumFreightAmt as decimal(18,2)) 	PremiumFreightPrice
	 , cast(s.CuryFreightTot as decimal(18,2))			FreightTotal
	 , s.CreatedDatetime 								CreatedDT
	 , replace(uc.Username, 'journeyhl.com\', '')		CreatedBy
	 , replace(um.Username, 'journeyhl.com\', '')		LastModifiedBy
	 , l.POCreate										POCreate
	 , l.POCreated										POCreated
	 , case when l.POCreate = 1 then cast(l.POCreateDate as date) else null end POCreateDate
	 , rtrim(sip.SiteCD) POWarehouse
	 , case when l.POCreate = 1 and l.POCreated = 1 then (
															select top 1 OrderNbr 
															from POOrder p 
															where s.CompanyID = p.CompanyID 
															and s.OrderType = p.soordertype 
															and s.OrderNbr = p.soordernbr
															-- and p.OrderDate = l.POCreateDate
															order by p.OrderDate desc
														 )
	   else null end PONbr
	 , l.POSource
from SOOrder s
inner join SOLine l on s.CompanyID = l.CompanyID and s.OrderNbr = l.OrderNbr and s.OrderType = l.OrderType and s.CustomerID = l.CustomerID
left join INSite si on s.CompanyID = si.CompanyID and l.SiteID = si.SiteID /*Warehouse joined on SOLine*/
left join INSite sip on s.CompanyID = sip.CompanyID and l.POSiteID = sip.SiteID
inner join InventoryItem i on s.CompanyID = i.CompanyID and l.InventoryID = i.InventoryID
left join INItemRep r on s.CompanyID = r.CompanyID and i.InventoryID = r.InventoryID

/*Shipment tables*/
left join SOShipLine shl on s.CompanyID = shl.CompanyID and s.OrderType = shl.OrigOrderType and s.OrderNbr = shl.OrigOrderNbr and l.LineNbr = shl.OrigLineNbr and l.InventoryID = shl.InventoryID
left join SOShipment sh on s.CompanyID = sh.CompanyID and shl.ShipmentNbr = sh.ShipmentNbr and shl.ShipmentType = sh.ShipmentType
left join INSite shi on s.CompanyID = shi.CompanyID and shl.SiteID = shi.SiteID /*Warehouse joined on SOShipLine*/

/*Customer tables*/
inner join BAccount b on s.CustomerID = b.BAccountID and s.CompanyID = b.CompanyID 
inner join Customer c on b.BAccountID = c.BAccountID and s.CompanyID = c.CompanyID
left join SOContact sc on s.CompanyID = sc.CompanyID and s.CustomerID = sc.CustomerID and s.ShipContactID = sc.ContactID /*Shipping contact*/
left join SOAddress sa on s.CompanyID = sa.CompanyID and s.ShipAddressID = sa.AddressID and s.CustomerID = sa.CustomerID /*Shipping address*/
left join SOContact bc on s.CompanyID = bc.CompanyID and s.CustomerID = bc.CustomerID and s.BillContactID = bc.ContactID /*Billing contact*/
left join SOAddress ba on s.CompanyID = ba.CompanyID and s.BillAddressID = ba.AddressID and s.CustomerID = ba.CustomerID /*Billing address*/

/*Salesperson tables*/
left join BAccount o on s.CompanyID = o.CompanyID and s.OwnerID = o.DefContactID 
left join Contact oc on s.CompanyID = oc.CompanyID and o.DefContactID = oc.ContactID
left join CustSalesPeople csp on s.CompanyID = csp.CompanyID and s.CustomerID = csp.BAccountID
left join SalesPerson sp on s.CompanyID = sp.CompanyID and csp.SalesPersonID = sp.SalespersonID

left join Users uc on s.CompanyID = uc.CompanyID and s.CreatedByID = uc.PKID
left join Users um on s.CompanyID = um.CompanyID and s.LastModifiedByID = um.PKID
inner join JJStatusLookup js on s.Status = js.CStatus and js.Tbl = 'SOOrder'
left join JJStatusLookup jsh on s.Status = jsh.CStatus and jsh.Tbl = 'SOShipment'
where s.CompanyID = 2 
and s.OrderType not in('QT', 'RA', 'RC', 'RR', 'RM')
and dateadd(hour, -4, s.LastModifiedDateTime) >=  dateadd(hour, -3, getdate())



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
--and dateadd(hour, -4, s.LastModifiedDateTime) >=  dateadd(hour, -2, getdate())
-- and s.OrderNbr = 'PH145626'
-- and s.LastModifiedDateTime >= cast(getdate()-30 as date)
-- order by LastModifiedDT desc
)
select OrderType
	 , OrderNumber
	 , LineNbr 
	 , DatePlaced
	 , CustomerID
	 , CustomerName
	 , CustomerClass
	 , InventoryCD
	 , Description
	 , Quantity
	 , LinePrice
	 , OrderTotal
	 , Status
	 , CustOrderNumber
	 , D2CSalesperson
	 , SalespersonName
	 , SalespersonEmail
	 , B2BSalesperson
	 , LastModifiedDT
	 , DiscountCode
	 , DiscountAmt
	 , LineCost
	 , case when len(s.Phone) > 20 and s.OrderType = 'ZA' then null
	 		when len(s.Phone) > 20 then left(s.Phone, 20)
	   		else s.Phone 
	   end Phone
	 , case when len(s.Email) > 255 and s.OrderType = 'ZA' then null
	 		when len(s.Email) > 255 then left(s.Email, 255)
	   		else s.Email 
	   end Email
	 , case when len(s.AddressLine1) > 355 and s.OrderType = 'ZA' then null
	 		when len(s.AddressLine1) > 355 then left(s.AddressLine1, 355)
	   		else s.AddressLine1 
	   end AddressLine1
	 , case when len(s.AddressLine2) > 255 and s.OrderType = 'ZA' then null
	 		when len(s.AddressLine2) > 255 then left(s.AddressLine2, 255)
	   		else s.AddressLine2 
	   end AddressLine2
	 , case when len(s.City) > 255 and s.OrderType = 'ZA' then null
	 		when len(s.City) > 255 then left(s.City, 255)
	   		else s.City 
	   end City
	 , case when len(s.State) > 50 and s.OrderType = 'ZA' then null
	 		when len(s.State) > 50 then left(s.State, 50)
	   		else s.State 
	   end State
	 , case when len(s.Zip) > 30 and s.OrderType = 'ZA' then null
	 		when len(s.Zip) > 30 then left(s.Zip, 30)
	   		else s.Zip 
	   end Zip
	 , case when len(s.Country) > 55 and s.OrderType = 'ZA' then null
	 		when len(s.Country) > 55 then left(s.Country, 55)
	   		else s.Country 
	   end Country
	 , LineAmount
	 , ReplenishmentClass
	 , StockItem
	 , OrderLineWH
	 , ShipDate
	 , ShipmentNbr
	 , ShipStatus
	 , ShipmentWH
	 , Completed
	 , OriginalOrderType
	 , OriginalOrderNbr
	 , FreightPrice
	 , PremiumFreightPrice
	 , FreightTotal
	 , CreatedDT
	 , CreatedBy
	 , LastModifiedBy
	 , POCreate
	 , POCreated
	 , POCreateDate
	 , POWarehouse
	 , PONbr
	 , POSource
from acuSalesOrders s
order by s.LastModifiedDT desc, OrderNumber, LineNbr
/*
Updated Query to only pull sales orders from the last two hours.
s.LastModifiedDateTime
*/
