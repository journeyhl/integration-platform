with TopLevel as(

select distinct c.CustomerID
	 , c.AccountName
	 , s.OrderNumber OrderNbr
	 , i.ItemClassDesc
	 , case when i.ItemClassDesc like '%Product%' or i.ItemClassDesc like '% Kits' or i.ItemClassDesc = 'UPwalker' then 'Products'
			when i.ItemClassDesc like '%Part%' or i.ItemClassDesc = 'Misc. Other' then 'Parts'
			when i.ItemClassDesc in('Sleep & Comfort', 'Warranties') then 'Parts'
			else null
	   end Item
	 , s.DatePlaced
	 , row_number() over(partition by s.CustomerID order by DatePlaced, OrderNumber) EarliestFirst
	 , row_number() over(partition by s.CustomerID order by DatePlaced desc, OrderNumber desc) RecentFirst
	 , min(DatePlaced) over(partition by s.CustomerID ) FirstOrder
	 , max(DatePlaced) over(partition by s.CustomerID ) LastOrder
	 , c.CreatedOn
from acu.Customers c
left join acu.SalesOrders s on c.CustomerID = s.CustomerID
left join acu.InventorySummary i on s.InventoryCD = i.InventoryCD
where c.CustomerClass = 'B2B' 

)
select distinct CustomerID
	 , AccountName
	 , FirstOrder
	 , LastOrder
	 , case when (FirstOrder is null and LastOrder is null) 
				then 'New'
	 		when LastOrder <= getdate()-365
				then 'Older than a year'
			when LastOrder <= getdate()-182.5 and LastOrder >= getdate()-365
				then 'Reactivated'
			else 'Existing' 
	   end CustomerType
	 , cast(t.CreatedOn as date) Created
	 , cast(getdate()-365 as date) YearAgo
from TopLevel t
order by LastOrder desc

