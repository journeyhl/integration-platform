create view _dev.AcuB2BZipCodes
as
select c.CustomerID
	 , c.AccountName
	 , left(c.Zip, 5) Zip
	 , c.SalesPersonID
	 , c.SalesPersonName
	 , c.CustomerClass
	 , concat(c.AddressLine1, case when c.AddressLine2 != '' and c.AddressLine2 is not null then concat(' ', c.AddressLine2) else '' end) AddressLine1
	 , c.City
	 , c.State
	 , c.Zip FullZip
	 , c.Country
	 , c.Phone
	 , c.Email
	 , c.Terms
	 , c.ContactName
	 , c.CreatedOn
	 , cc.Cohort
	 , cc.MonthsSinceProduct
	 , cc.MonthsSincePA
from acu.Customers c
left join analytics.JHL_B2BCustomerCohorts cc on c.CustomerID = cc.CustomerID
where c.CustomerClass = 'B2B'
