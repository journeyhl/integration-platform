
select a.CustomerID
	 , c.AccountName
	 , a.Cohort
	 , a.AnchorDate
	 , a.AnchorType
	 , a.LastProductDate
	 , a.LastPADate
	 , a.MonthsSinceProduct
	 , a.MonthsSincePA
	 , c.SalesPersonID
	 , c.SalesPersonName
	 , newid() CohortNoteID
	 , newid() AnchorDateNoteID
	 , newid() AnchorTypeNoteID
	 , newid()LastProductDateNoteID
	 , newid() LastPADateNoteID
	 , newid() MonthsSinceProductNoteID
	 , newid() MonthsSincePANoteID
from analytics.JHL_B2BCustomerCohorts a
inner join acu.Customers c on a.CustomerID = c.CustomerID