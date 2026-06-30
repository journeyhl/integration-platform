with TopLevel as(
select distinct CustomerID
	 , s.Phone
	 , s.AddressLine1
	 , s.City
	 , s.State
	 , s.Zip
	 , s.CustomerName
	 , s.DatePlaced
	 , ROW_NUMBER() over(partition by CustomerID order by DatePlaced desc) MostRecent_byCustID
	 , ROW_NUMBER() over(partition by CustomerID, Phone order by DatePlaced desc) MostRecent_byPhoneCustID
from acu.salesorders s 
where s.CustomerClass = 'D2C'
and s.Phone is not null
)
select *
from TopLevel t
where t.MostRecent_byCustID = 1 and t.MostRecent_byPhoneCustID = 1
order by CustomerID desc, MostRecent_byCustID 