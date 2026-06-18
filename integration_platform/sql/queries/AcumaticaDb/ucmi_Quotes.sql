

select cast(s.OrderDate as date) Date
	   , s.OrderType
	   , s.OrderNbr
	   , l.LineNbr OrderLineNbr
       , rtrim(i.InventoryCD) InventoryCD
       , rtrim(i.Descr) Descr
       , cast(l.OrderQty as int) as Qty
	   , cast(l.LineAmt  as decimal(18,2))	LinePrice
	   , cast(l.DiscAmt  as decimal(18,2))	LineDiscount
	   , cast(l.ExtPrice as decimal(18,2)) LineFullPrice
	   , js.Status OrderStatus

	   , rtrim(o.AcctCD) SalespersonCD_D2C
	   , o.AcctName Salesperson_D2C	   
	   , rtrim(sp.SalespersonCD) SalespersonCD_B2B
	   , sp.Descr Salesperson_B2B

	   , rtrim(b.AcctCD) CustomerID
	   , b.AcctName CustomerName
	   , c.CustomerClassID

	   , ba.AddressLine1 BillAddressLine1
	   , case when ba.AddressLine2 = '' then null else ba.AddressLine2 end BillAddressLine2
	   , ba.City		 BillCity
	   , ba.State		 BillState
	   , ba.PostalCode	 BillPostalCode
	   , ba.CountryID	 BillCountry
	   , bc.Phone1		 BillPhone
	   , case when bc.Phone2 = '' then null else bc.Phone2 end BillPhone2
	   , bc.Email		 BillEmail
	   , sa.AddressLine1 ShipAddressLine1
	   , case when sa.AddressLine2 = '' then null else sa.AddressLine2 end ShipAddressLine2
	   , sa.City		 ShipCity
	   , sa.State		 ShipState
	   , sa.PostalCode	 ShipPostalCode
	   , sa.CountryID	 ShipCountry
	   , sc.Phone1		 ShipPhone
	   , case when sc.Phone2 = '' then null else sc.Phone2 end ShipPhone2
	   , sc.Email		 ShipEmail
	   
	   , b.CreatedDateTime
	   , uc.Username CreatedByUser
	   , uc.FullName CreatedByName
	   , b.LastModifiedDateTime
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
left join SOAddress ba on s.CompanyID = ba.CompanyID and s.BillAddressID = ba.AddressID and s.CustomerID = ba.CustomerID
left join SOAddress sa on s.CompanyID = sa.CompanyID and s.ShipAddressID = sa.AddressID and s.CustomerID = sa.CustomerID
left join SOContact bc on s.CompanyID = bc.CompanyID and s.CustomerID = bc.CustomerID and s.BillContactID = bc.ContactID
left join SOContact sc on s.CompanyID = sc.CompanyID and s.CustomerID = sc.CustomerID and s.ShipContactID = sc.ContactID
left join SOLine l on s.CompanyID = l.CompanyID and s.OrderNbr = l.OrderNbr and s.OrderType = l.OrderType and s.CustomerID = l.CustomerID
left join InventoryItem i on s.CompanyID = i.CompanyID and l.InventoryID = i.InventoryID


left join CustSalesPeople csp on s.CompanyID = csp.CompanyID and s.CustomerID = csp.BAccountID
left join SalesPerson sp on s.CompanyID = sp.CompanyID and csp.SalesPersonID = sp.SalespersonID
left join BAccount o on s.CompanyID = o.CompanyID and s.OwnerID = o.DefContactID 
inner join JJStatusLookup js on s.Status = js.CStatus and js.Tbl = 'SOOrder'

left join Users uc on s.CompanyID = uc.CompanyID and s.CreatedByID = uc.PKID
left join Users um on s.CompanyID = um.CompanyID and s.LastModifiedByID = um.PKID
where s.CompanyID = 2 
and s.OrderType = 'QT'
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


