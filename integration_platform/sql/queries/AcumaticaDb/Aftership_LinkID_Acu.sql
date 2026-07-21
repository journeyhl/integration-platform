with TopLevel as(
select distinct s.OrderType
	 , s.OrderNbr
	 , s.NoteID RecordID
	 , 'AttributeAFTSHIPID' FieldName
	 , k.ValueString AfterShipID
	 , j.Status
     , 2 CompanyID
     , null ValueNumeric
     , null ValueDate
     , null ValueText
from SOOrder s
inner join SOLine l on s.CompanyID = l.CompanyID and s.OrderType = l.OrderType and s.OrderNbr = l.OrderNbr
left join SOShipLine sl on s.CompanyID = sl.CompanyID and l.OrderType = sl.OrigOrderType and l.OrderNbr = sl.OrigOrderNbr and l.LineNbr = sl.OrigLineNbr
left join SOOrderKvEXT k on s.CompanyID = k.CompanyID and s.NoteID = k.RecordID and k.FieldName = 'AttributeAFTSHIPID'
inner join JJStatusLookup j on s.Status = j.CStatus and j.Tbl = 'SOOrder'
where s.CompanyID = 2
and 
	(j.Status not in ('On Hold', 'Canceled', 'Awaiting Payment', 'Risk Hold', 'Open') or sl.ShipmentNbr is not null)
and s.OrderType not in ('ZM', 'ZA', 'QT', 'HS')
)
select *
from TopLevel