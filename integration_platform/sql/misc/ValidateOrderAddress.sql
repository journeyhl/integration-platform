
select s.OrderDate
	 , s.OrderNbr
	 , CONCAT('update SOAddress set isValidated = 1 where AddressID in(', sh.AddressID, ', ', b.AddressID, ') and companyid = 2') UpdateStatement
	 , sh.AddressLine1
	 , sh.City
	 , sh.PostalCode
	 , sh.State
	 , sh.IsValidated
	 , b.AddressLine1 billLine1
	 , b.City billCity
	 , b.PostalCode billZip
	 , b.State billState
	 , b.IsValidated billValidated
	 , case when s.Status = 'C' then 'Completed'		when s.Status = 'N' then 'Open'
			when s.Status = 'L' then 'Canceled'			when s.Status = 'B' then 'Back Order'
			when s.Status = 'H' then 'On Hold'			when s.Status = 'S' then 'Shipping'
			when s.Status = 'A' then 'Awaiting Payment'	when s.Status = 'X' then 'Risk Hold'	
			when s.Status = 'P' then 'Pending Approval'	else null end [Order Status]
	 , sh.AddressID ShipAddressID
	 , CONCAT('https://erp.journeyhl.com/(W(32))/Main?CompanyID=JHL&ScreenId=SO302000&ShipmentNbr=', o.ShipmentNbr)
	 , c.FullName
from SOOrder s inner join
		SOAddress sh on s.ShipAddressID = sh.AddressID and s.CustomerID = sh.CustomerID and s.CompanyID = sh.CompanyID inner join
		SOAddress b on s.BillAddressID = b.AddressID and s.CustomerID = b.CustomerID and s.CompanyID = b.CompanyID left join
		SOOrderShipment o on s.OrderNbr = o.OrderNbr and s.CompanyID = o.CompanyID and s.ShipAddressID = o.ShipAddressID
left join SOContact c on s.CompanyID = c.CompanyID and s.ContactID = c.ContactID and s.CustomerID = c.CustomerID
where s.CompanyID = 2
and s.OrderType != 'QT' and s.Status not in('L', 'C')
and s.OrderNbr in('', '','', '', '')
