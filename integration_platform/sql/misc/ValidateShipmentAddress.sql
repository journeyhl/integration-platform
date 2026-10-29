
select s.ShipmentNbr
	 , sh.AddressLine1
	 , sh.City
	 , sh.PostalCode
	 , sh.State
	 , sh.IsValidated
	 , case when s.Status = 'C' then 'Completed'		when s.Status = 'N' then 'Open'
			when s.Status = 'L' then 'Canceled'			when s.Status = 'B' then 'Back Order'
			when s.Status = 'H' then 'On Hold'			when s.Status = 'S' then 'Shipping'
			when s.Status = 'A' then 'Awaiting Payment'	when s.Status = 'X' then 'Risk Hold'	
			when s.Status = 'P' then 'Pending Approval'	else null end [Order Status]
	 , CONCAT('update SOAddress set isValidated = 1 where AddressID in(', sh.AddressID, ') and companyid = 2') UpdateStatement
	 , CONCAT('https://erp.journeyhl.com/(W(32))/Main?CompanyID=JHL&ScreenId=SO302000&ShipmentNbr=', s.ShipmentNbr) URL
from SOShipment s inner join
		SOAddress sh on s.ShipAddressID = sh.AddressID and s.CustomerID = sh.CustomerID and s.CompanyID = sh.CompanyID
where s.CompanyID = 2 and s.Status not in('L', 'C')
and s.ShipmentNbr in(' ', '','', '', '')