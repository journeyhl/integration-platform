with TopLevel as(
    select distinct c.CustomerClass
	 , c.CustomerID
	 , c.AccountName
	 , s.OrderNumber OrderNbr
	 , i.ItemClassDesc
	--  , coalesce(ic.ItemClass, 'Parts') PartProdAccFee
     , case when ic.ItemClass is null and OrderNumber is null then 'No Orders' 
            when ic.ItemClass is null and OrderNumber is not null then 'Parts/Accessories' 
            when ic.ItemClass in ('Parts', 'Accessory', 'Fee') then 'Parts/Accessories' else ic.ItemClass end PartProdAccFee
	 , s.DatePlaced
     , datediff(day, s.DatePlaced, cast(dateadd(hour, -4, getdate()) as date)) DaysAgo
	 , row_number() over(partition by c.CustomerID order by DatePlaced, OrderNumber) OrdersAsc
	 , row_number() over(partition by c.CustomerID order by DatePlaced desc, OrderNumber desc) OrdersDesc
	 , c.CreatedOn
	 , c.Phone
	 , c.Email
from acu.Customers c
left join acu.SalesOrders s on c.CustomerID = s.CustomerID
left join acu.InventorySummary i on s.InventoryCD = i.InventoryCD
left join acu.ItemClassification ic on i.InventoryCD = ic.InventoryCD
)
select *
	 , row_number() over(partition by t.CustomerID, PartProdAccFee order by DatePlaced, OrderNbr) OrderProdAsc
	 , row_number() over(partition by t.CustomerID, PartProdAccFee order by DatePlaced desc, OrderNbr desc) OrderProdDesc
from TopLevel t
order by CustomerID, OrdersDesc