
select s.OrderType									OrderType
	 , cast(s.OrderDate as date) 					DatePlaced
	 , s.OrderNbr 									OrderNumber
	 , l.LineNbr  									LineNbr 
	 , rtrim(i.InventoryCD) 						InventoryCD
     , rtrim(i.Descr) 								Description
     , cast(l.OrderQty as int) as 					Quantity
	 , sh.ShipmentNbr								ShipmentNbr
	 , cast(shk.ValueNumeric as int)				rlmSent
	 , shkk.ValueString								rlmID
	 , cast(shkc.ValueNumeric as int)				rlmChecked
	 , shke.ValueString								rlmError
	 , cast(sh.ShipDate as date)					ShipDate
	 , jsh.Status									ShipStatus
	 , js.Status 									Status
	 , l.ShipVia									ShipVia
	 , rtrim(shi.SiteCD)							ShipmentWH
from SOOrder s
inner join SOLine l on s.CompanyID = l.CompanyID and s.OrderNbr = l.OrderNbr and s.OrderType = l.OrderType and s.CustomerID = l.CustomerID
inner join SOShipLine shl on s.CompanyID = shl.CompanyID and s.OrderType = shl.OrigOrderType and s.OrderNbr = shl.OrigOrderNbr and l.LineNbr = shl.OrigLineNbr and l.InventoryID = shl.InventoryID
inner join SOShipment sh on s.CompanyID = sh.CompanyID and shl.ShipmentNbr = sh.ShipmentNbr and shl.ShipmentType = sh.ShipmentType
inner join InventoryItem i on s.CompanyID = i.CompanyID and l.InventoryID = i.InventoryID
left join INItemRep r on s.CompanyID = r.CompanyID and i.InventoryID = r.InventoryID
left join INSite shi on s.CompanyID = shi.CompanyID and shl.SiteID = shi.SiteID 

inner join JJStatusLookup js on s.Status = js.CStatus and js.Tbl = 'SOOrder'
left join JJStatusLookup jsh on sh.Status = jsh.CStatus and jsh.Tbl = 'SOShipment'
left join SOShipmentKvExt shk on s.CompanyID = shk.CompanyID and sh.NoteID = shk.RecordID and shk.FieldName = 'AttributeSHP2WH'
left join SOShipmentKvExt shkk on s.CompanyID = shkk.CompanyID and sh.NoteID = shkk.RecordID and shkk.FieldName = 'AttributeRYDERAPIID'
left join SOShipmentKvExt shke on s.CompanyID = shke.CompanyID and sh.NoteID = shke.RecordID and shke.FieldName = 'AttributeRYDERERROR'
left join SOShipmentKvExt shkc on s.CompanyID = shkc.CompanyID and sh.NoteID = shkc.RecordID and shkc.FieldName = 'AttributeRYDERCHECK'
where s.CompanyID = 2 
and s.OrderType not in('QT', 'RA', 'RC', 'RR', 'RM')
and dateadd(hour, -4, s.LastModifiedDateTime) >=  dateadd(day, -120, getdate())
and shi.SiteCD = 'RLM NEJ HB'
and shk.ValueNumeric = 1

order by sh.CreatedDateTime desc

