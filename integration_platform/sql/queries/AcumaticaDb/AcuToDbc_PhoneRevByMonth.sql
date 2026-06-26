
select distinct rtrim(b.AcctCD) AcctCD
	 , case when sc.FullName != sc.Attention and sc.Attention is not null and sc.FullName is null
				then ltrim(sc.Attention) 
			when sc.Attention is not null and sc.FullName is null 
				then ltrim(sc.Attention) 
			when sc.FullName is not null and sc.Attention is null 
				then ltrim(sc.FullName) 
			when sc.FullName is null and sc.Attention is null 
				then b.AcctName
	   else ltrim(sc.FullName) 
	   end Name
	   , sc.Phone1 Phone
	   ,s.OrderNbr
	   , sl.LineNbr
	   , Cast(CAST(s.OrderDate as date) as varchar(40)) OrderDate
	   , j.Status OrderStatus
	   , RTRIM(i.InventoryCD) InventoryCD
	   , Descr
	   , cast(sl.LineAmt as decimal(18,2)) LineAmt
	   , o.AcctName Agent
from SOOrder s 
inner join SOLine sl on s.OrderNbr = sl.OrderNbr and s.CompanyID = sl.CompanyID
inner join InventoryItem i on sl.InventoryID = i.InventoryID and s.CompanyID = i.CompanyID
inner join BAccount b on s.CustomerID = b.BAccountID and s.CompanyID = b.CompanyID
inner join SOContact sc on s.ShipContactID = sc.ContactID and s.CompanyID = sc.CompanyID
inner join BAccount o on s.OwnerID = o.DefContactID and s.CompanyID = o.CompanyID
left join JJStatusLookup j on s.Status = j.CStatus and j.Tbl = 'SOOrder'
where s.CompanyID = 2 and s.OrderType in('PH', 'BF')
and sc.Phone1 is not null 
and i.InventoryCD not like '%NSG-%'
-- and s.Status in('C', 'N', 'B', 'S') --Completed, On Hold, Back Order or Shipping statuses are allowed
and (
s.OrderDate >= getdate()-1
or s.LastModifiedDateTime >= getdate()-7
)