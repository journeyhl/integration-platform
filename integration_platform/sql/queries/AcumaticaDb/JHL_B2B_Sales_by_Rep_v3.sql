
with 
customer_attributes as(
	select rtrim(b.AcctCD) AcctCD
		 , c.RefNoteID
		 , c.AttributeID
		 , c.Value
	from CSAnswers c
	inner join BAccount b on c.CompanyID = b.CompanyID and c.RefNoteID = b.NoteID
	where c.CompanyID = 2 and c.AttributeID in(
	'COHORT',
	'ANCHORDATE',
	'ANCHORTYPE',
	'LASTPRODDT',
	'LASTPADT',
	'MONTHSPA',
	'MONTHSPROD')
)
, item_attributes as(
	select rtrim(i.InventoryCD) InventoryCD
		 , c.RefNoteID
		 , c.AttributeID
		 , c.Value
	from CSAnswers c
	inner join InventoryItem i on c.CompanyID = i.CompanyID and c.RefNoteID = i.NoteID
	where c.CompanyID = 2 and c.AttributeID in(
	'ITEM',
	'PRODFAMILY',
	'PRODGROUP',
	'PRODPART')
)
, main as(
	select cast(s.OrderDate as date) OrderDate
		 , s.OrderType
		 , s.OrderNbr
		 , l.LineNbr
		 , rtrim(b.AcctCD) AcctCD
		 , b.AcctName
		 , i.InventoryCD
		 , i.Descr
		 , j.Status
		 , cast(l.OrderQty as int) OrderQty
		 , l.ShipVia
		 , cast(l.ExtPrice as decimal(18,2)) LinePrice
		 , cast(l.DiscAmt as decimal(18,2)) LineDisc
		 , cast(l.LineAmt as decimal(18,2)) LineTotal
		 , cast(case when l.ExtCost = 0 then l.OrderQty * coalesce(ic.LastCost, 0) else l.ExtCost end as decimal(18,2)) LineCost
		 , cast(case when l.ExtCost = 0 then l.ExtPrice - (l.OrderQty * coalesce(ic.LastCost, 0)) else l.ExtPrice - l.ExtCost end as decimal(18,2)) LineGM_Price
		 , cast(case when l.ExtCost = 0 then l.LineAmt - (l.OrderQty * coalesce(ic.LastCost, 0)) else l.LineAmt - l.ExtCost end as decimal(18,2)) LineGM_Amt
	from SOOrder s 
	inner join SOLine l on s.CompanyID = l.CompanyID and s.OrderType = l.OrderType and s.OrderNbr = l.OrderNbr
	inner join InventoryItem i on s.CompanyID = i.CompanyID and l.InventoryID = i.InventoryID
	left join INItemCost ic on s.CompanyID = ic.CompanyID and i.InventoryID = ic.InventoryID
	inner join INItemClass inc on s.CompanyID = inc.CompanyID and i.ItemClassID = inc.ItemClassID
	inner join BAccount b on s.CompanyID = b.CompanyID and s.CustomerID = b.BAccountID
	inner join Customer c on s.CompanyID = c.CompanyID and s.CustomerID = c.BAccountID
	left join CustSalesPeople csp on s.CompanyID = csp.CompanyID and c.BAccountID = csp.BAccountID
	left join SalesPerson sp on s.CompanyID = sp.CompanyID and csp.SalesPersonID = sp.SalespersonID
	inner join SOAddress sa on s.CompanyID = sa.CompanyID and s.ShipAddressID = sa.AddressID and s.CustomerID = sa.CustomerID
	inner join SOAddress ba on s.CompanyID = ba.CompanyID and s.BillAddressID = ba.AddressID and s.CustomerID = ba.CustomerID
	inner join JJStatusLookup j on s.Status = j.CStatus and j.Tbl = 'SOOrder'
	where s.CompanyID = 2 and s.OrderType not in('QT', 'RA', 'RC') and c.CustomerClassID = 'B2B' 
)
select m.*
	 , ac.Value Cohort
	 , aat.Value ClockStartStatus
	 , aad.Value ClockStartDate
	 , apd.Value LastProductDate
	 , apad.Value LastPADate
	 , amp.Value MoSinceProductOrder
	 , ampa.Value MoSincePAOrder
	 , ii.Value Item
	 , ipf.Value ProductFamily
	 , ipg.Value ProductGroup
	 , ipp.Value ProductPartAccFee
from main m
left join customer_attributes ac on m.AcctCD = ac.AcctCD and ac.AttributeID = 'COHORT'
left join customer_attributes aat on m.AcctCD = aat.AcctCD and aat.AttributeID = 'ANCHORTYPE'
left join customer_attributes aad on m.AcctCD = aad.AcctCD and aad.AttributeID = 'ANCHORDATE'
left join customer_attributes apd on m.AcctCD = apd.AcctCD and apd.AttributeID = 'LASTPRODDT'
left join customer_attributes apad on m.AcctCD = apad.AcctCD and apad.AttributeID = 'LASTPADT'
left join customer_attributes amp on m.AcctCD = amp.AcctCD and amp.AttributeID = 'MONTHSPROD'
left join customer_attributes ampa on m.AcctCD = ampa.AcctCD and ampa.AttributeID = 'MONTHSPA'
left join item_attributes ii on m.InventoryCD = ii.InventoryCD and ii.AttributeID = 'ITEM'
left join item_attributes ipf on m.InventoryCD = ipf.InventoryCD and ipf.AttributeID = 'PRODFAMILY'
left join item_attributes ipg on m.InventoryCD = ipg.InventoryCD and ipg.AttributeID = 'PRODGROUP'
left join item_attributes ipp on m.InventoryCD = ipp.InventoryCD and ipp.AttributeID = 'PRODPART'
