
with TopLevel as(
select s.OrderType
  , s.OrderNumber OrderNbr
  , s.DatePlaced
  , s.CustomerID
  , s.CustomerClass
  , s.InventoryCD
  , s.Quantity Qty
  , s.LinePrice LinePrice
  , s.DiscountAmt
  , s.LineAmount Revenue
  , s.Status
  , case when s.OrderType in('DM', 'CO', 'RT') 
           or s.CustomerClass = 'B2B' 
            then 'B2B'
         when s.CustomerClass = 'ECA' or s.OrderType in('EA', 'ZA', 'ZM') 
            then 'Amazon'
         when s.CustomerClass = 'D2C'
            then 'D2C'
         else null 
    end CustTypeBucket
  , case when s.OrderType in('DM', 'CO', 'RT') 
           or s.CustomerClass = 'B2B' 
            then 'Retail'
         when s.OrderType = 'WB' 
            then 'Web'
         when s.OrderType in ('PH', 'RO', 'WA') 
            then 'Phone'
         when s.OrderType in('ZA', 'EA', 'ZM')  
            then 'Amazon'
         when s.OrderType = 'HS' 
            then 'HSN'
         when s.OrderType = 'BF' 
            then 'Bread'
         else null
    end Channel
  , case when (s.Status in('Shipping', 'Back Order', 'Completed') and (s.ShipmentNbr is not null or s.OrderType in ('ZA', 'ZM')))
           or (s.POCreated = 1)
            then 1 
         when s.DatePlaced <= '20250131' and s.Status = 'Completed' 
            then 1
         else 0 
    end Shipped
  , case when s.Status in('Shipping', 'Back Order', 'Completed', 'Open', 'Risk Hold') 
            then 1
         else 0
    end Booked  
  , i.Description AS ItemDescr
  , i.ItemClassDesc AS ItemClassDescr
  , i.PostingClass AS PostingClass
  , i.ItemType AS ItemType
  , s.LineCost
  , case when s.OrderType in('DM', 'CO', 'RT') or s.CustomerClass = 'B2B' then s.B2BSalesperson
   else s.D2CSalesperson end Salesperson
  , s.LineNbr
  , count(s.OrderNumber) over(partition by s.OrderNumber) Lines
  , s.CustomerName
  , s.ShipmentNbr
  , (select sum(LinePrice) from acu.SalesOrders s2 where s2.OrderNumber = s.OrderNumber and (left(s2.InventoryCD, 3) = 'NSG' or s2.InventoryCD = 'EXTWARNTY')) Total_WarrantyRevenue
  , datepart(month, s.DatePlaced) Date_Month
  , datepart(Year, s.DatePlaced) Date_Year
  , concat(datepart(Year, s.DatePlaced), '-', 
    case when datepart(month, s.DatePlaced) < 10 then concat('0', datepart(month, s.DatePlaced)) else concat('', datepart(month, s.DatePlaced)) end) FinPeriod
from acu.SalesOrders s 
inner join acu.InventorySummary i on s.InventoryCD = i.InventoryCD
where s.status not in ('Awaiting Payment', 'Canceled', 'Pending Approval', 'Rejected', 'On Hold')
and s.OrderType not in ('QT','RA','RC', 'CM')
and left(s.InventoryCD, 3) != 'NSG'
and s.InventoryCD != 'EXTWARNTY'
and s.Quantity != 0
)

, SecondLevel as(
select t.OrderType
     , t.OrderNbr
     , t.DatePlaced
     , t.FinPeriod
     , t.CustomerID
     , t.CustomerClass
     , sum(t.Qty) Total_Qty
     , sum(t.LinePrice) Total_LinePrice
     , sum(t.DiscountAmt) Total_Discount
     , sum(t.Revenue) Total_Revenue
     , sum(t.LineCost) Total_LineCost
     , case when t.Total_WarrantyRevenue is null then 0 else t.Total_WarrantyRevenue end Total_WarrantyRevenue
     , t.Status
     , t.CustTypeBucket
     , t.Channel
     , case when t.CustTypeBucket = 'D2C' and t.Channel in('Bread', 'Phone', 'Web')
                then 'D2C'
            when t.CustTypeBucket = 'Amazon'
                then 'Amazon'
            when t.Channel = 'HSN'
                then 'HSN'
            when t.CustTypeBucket = 'B2B' and t.Channel = 'Retail' 
                then 'B2B'
        else null end MetricBucket
     , t.Booked
     , t.Shipped
     , t.Lines
from TopLevel t

group by t.OrderType
       , t.OrderNbr
       , t.DatePlaced
       , t.FinPeriod
       , t.CustomerID
       , t.CustomerClass
       , t.Status
       , t.CustTypeBucket
       , t.Channel
       , t.Total_WarrantyRevenue
       , t.Booked
       , t.Shipped
       , t.Lines
)
, FinalLevel as(
select s.MetricBucket
     , s.DatePlaced
     , s.FinPeriod
     , cast(sum(s.Total_Revenue) as decimal(18,2)) Booked
     , cast(sum(case when s.Shipped = 1 then s.Total_Revenue else 0 end) as decimal(18,2)) Shipped
     , 0 FinPeriodTotal
from SecondLevel s
group by s.MetricBucket, s.FinPeriod, DatePlaced
union
select 'Total' Total
     , s.DatePlaced
     , s.FinPeriod
     , cast(sum(s.Total_Revenue) as decimal(18,2)) Booked
     , cast(sum(case when s.Shipped = 1 then s.Total_Revenue else 0 end) as decimal(18,2)) Shipped
     , 1 FinPeriodTotal
from SecondLevel s
group by s.FinPeriod, DatePlaced
)
select *
from FinalLevel