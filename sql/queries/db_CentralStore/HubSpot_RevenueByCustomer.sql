with TopLevel as(
select s.CustomerID
	 , cast(sum(s.LineAmount) as decimal(18,2)) TotalRevenue
	 , count(distinct OrderNumber) Orders
	 , sum(s.Quantity) Units
from acu.SalesOrders s
group by CustomerID
)
select t.*
	 , cast(TotalRevenue/Orders as decimal(18,2)) RevPerOrder
	 , cast(Units/(Orders * 1.0) as decimal(18,2)) UnitsPerOrder
	 , case when coalesce(c.Phone, c.Phone2) != '' then coalesce(ltrim(rtrim(c.Phone)), ltrim(rtrim(c.Phone2))) else null end phone
	 , case when c.Email = 'noemail@found.com' then null else c.Email end email
	 , case when coalesce(ltrim(rtrim(c.Phone)), ltrim(rtrim(c.Phone2))) != ltrim(rtrim(c.phone2)) then ltrim(rtrim(c.phone2)) else null end phone2
	 , c.AccountName
from TopLevel t
inner join acu.Customers c on t.CustomerID = c.CustomerID
where coalesce(c.Phone, c.Phone2) is not null
and c.CustomerID != 'C0008267'
order by Units desc

--Rev by Ccmpany 

/*
TotalRevenue - revenue
TotalOrders - totalorders
TotalUnits - totalunits
RevenuePerOrder - revenueperorder
UnitsPerOrder - unitsperorder
*/