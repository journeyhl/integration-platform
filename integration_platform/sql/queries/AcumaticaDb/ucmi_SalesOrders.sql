

select cast(s.OrderDate as date) Date
	   , s.OrderType
	   , s.OrderNbr
	   , case when l.LineNbr is null then 0 else l.LineNbr end OrderLineNbr
       , rtrim(i.InventoryCD) InventoryCD
       , rtrim(i.Descr) Descr
       , cast(l.OrderQty as int) as Qty
	   , cast(l.LineAmt  as decimal(18,2))	LinePrice
	   , cast(l.DiscAmt  as decimal(18,2))	LineDiscount
	   , cast(l.ExtPrice as decimal(18,2)) LineFullPrice
	   , js.Status OrderStatus
	   , sh.ShipmentNbr ShipNbr
	   , shl.LineNbr ShipLineNbr
	   , jsh.Status ShipStatus
	   , cast(shl.ShippedQty as int) ShipQty
	   , rtrim(o.AcctCD) SalespersonCD_D2C
	   , o.AcctName Salesperson_D2C	   
	   , rtrim(sp.SalespersonCD) SalespersonCD_B2B
	   , sp.Descr Salesperson_B2B

	   , rtrim(b.AcctCD) CustomerID
	   , b.AcctName CustomerName
	   , c.CustomerClassID
	   , s.OrigOrderNbr

	   , left(ba.AddressLine1, 255) BillAddressLine1
	   , case when ba.AddressLine2 = '' then null else left(ba.AddressLine2, 255) end BillAddressLine2
	   , left(ba.City, 100)		 BillCity
	   , left(ba.State, 2)		 BillState
	   , left(ba.PostalCode, 20)	 BillPostalCode
	   , left(ba.CountryID, 20)	 BillCountry
	   , left(bc.Phone1, 15)		 BillPhone
	   , case when bc.Phone2 = '' then null else left(bc.Phone2, 15) end BillPhone2
	   , left(bc.Email, 100)		 BillEmail
	   , left(sa.AddressLine1, 255) ShipAddressLine1
	   , case when sa.AddressLine2 = '' then null else left(sa.AddressLine2, 255) end ShipAddressLine2
	   , left(sa.City, 100)		 ShipCity
	   , left(sa.State, 2)		 ShipState
	   , left(sa.PostalCode, 20)	 ShipPostalCode
	   , left(sa.CountryID, 20)	 ShipCountry
	   , left(sc.Phone1, 15)		 ShipPhone
	   , case when sc.Phone2 = '' then null else left(sc.Phone2, 15) end ShipPhone2
	   , left(sc.Email, 100)		 ShipEmail
	   
	   , s.CreatedDateTime
	   , uc.Username CreatedByUser
	   , uc.FullName CreatedByName
	   , s.LastModifiedDateTime
	   , um.Username LastModifiedByUser
	   , um.FullName LastModifiedByName

	   , b.BAccountID
	   , ba.AddressID BillAddressID
	   , sa.AddressID ShipAddressID
	   , bc.ContactID BillContactID
	   , sc.ContactID ShipContactID
	   , o.BAccountID SalespersonID_D2C
	   , sp.SalespersonID SalespersonID_B2B


from SOOrder s 
inner join BAccount b on s.CustomerID = b.BAccountID and s.CompanyID = b.CompanyID 
inner join Customer c on b.BAccountID = c.BAccountID and s.CompanyID = c.CompanyID
inner join SOAddress ba on s.CompanyID = ba.CompanyID and s.BillAddressID = ba.AddressID and s.CustomerID = ba.CustomerID
inner join SOAddress sa on s.CompanyID = sa.CompanyID and s.ShipAddressID = sa.AddressID and s.CustomerID = sa.CustomerID
inner join SOContact bc on s.CompanyID = bc.CompanyID and s.CustomerID = bc.CustomerID and s.BillContactID = bc.ContactID
inner join SOContact sc on s.CompanyID = sc.CompanyID and s.CustomerID = sc.CustomerID and s.ShipContactID = sc.ContactID
left join SOLine l on s.CompanyID = l.CompanyID and s.OrderNbr = l.OrderNbr and s.OrderType = l.OrderType and s.CustomerID = l.CustomerID
left join InventoryItem i on s.CompanyID = i.CompanyID and l.InventoryID = i.InventoryID
left join SOShipLine shl on s.CompanyID = shl.CompanyID and l.OrderNbr = shl.OrigOrderNbr and l.OrderType = shl.OrigOrderType and l.LineNbr = shl.OrigLineNbr and s.CustomerID = shl.CustomerID
left join SOShipment sh on s.CompanyID = sh.CompanyID and shl.ShipmentNbr = sh.ShipmentNbr and s.CustomerID = sh.CustomerID
left join CustSalesPeople csp on s.CompanyID = csp.CompanyID and s.CustomerID = csp.BAccountID
left join SalesPerson sp on s.CompanyID = sp.CompanyID and csp.SalesPersonID = sp.SalespersonID
left join BAccount o on s.CompanyID = o.CompanyID and s.OwnerID = o.DefContactID 
left join JJStatusLookup js on s.Status = js.CStatus and js.Tbl = 'SOOrder'
left join JJStatusLookup jsh on sh.Status = jsh.CStatus and jsh.Tbl = 'SOShipment'

left join Users uc on s.CompanyID = uc.CompanyID and s.CreatedByID = uc.PKID
left join Users um on s.CompanyID = um.CompanyID and s.LastModifiedByID = um.PKID
where s.CompanyID = 2 
and s.OrderType not in('CM', 'RC', 'QT', 'WA', 'RO', 'RA')
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
order by Date desc


