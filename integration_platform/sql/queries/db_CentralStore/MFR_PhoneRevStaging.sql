
select AcctCD 
     , Name 
     , Phone 
     , OrderNbr 
     , LineNbr 
     , OrderDate 
     , OrderStatus 
     , s.InventoryCD 
     , Descr 
     , LineAmt 
     , Agent 
	 , s.LineAmt Value
	--  , ip.Product
	 , ROW_NUMBER() OVER (PARTITION BY OrderNbr ORDER BY case when s.LineAmt < i.Price then i.Price else s.LineAmt end desc) Priority
from  acu.PhoneRevByMonth s 
inner join acu.InventorySummary i on s.InventoryCD = i.InventoryCD 
-- inner join InventorySummary_Product ip on s.InventoryCD = ip.InventoryCD
where s.OrderStatus not in ('Canceled', 'Awaiting Payment')
and cast(s.OrderDate AS date) >= '2024-01-08'