select distinct c.CustomerID
	 , c.AccountName
	 , s.OrderNumber OrderNbr
	 , i.ItemClassDesc
	 , coalesce(ic.ItemClass, 'Parts') PartProdAccFee
	 , s.DatePlaced
	 , row_number() over(partition by s.CustomerID order by DatePlaced, OrderNumber) OrdersAsc
	 , row_number() over(partition by s.CustomerID order by DatePlaced desc, OrderNumber desc) OrdersDesc
	 , row_number() over(partition by s.CustomerID, coalesce(ic.ItemClass, 'Parts') order by DatePlaced, OrderNumber) OrderProdAsc
	 , row_number() over(partition by s.CustomerID, coalesce(ic.ItemClass, 'Parts') order by DatePlaced desc, OrderNumber desc) OrderProdDesc
	 , c.CreatedOn
	 , c.Phone
from acu.Customers c
left join acu.SalesOrders s on c.CustomerID = s.CustomerID
left join acu.InventorySummary i on s.InventoryCD = i.InventoryCD
left join acu.ItemClassification ic on i.InventoryCD = ic.InventoryCD
where c.CustomerClass = 'B2B' 
order by CustomerID, PartProdAccFee desc, OrdersDesc, OrderProdDesc