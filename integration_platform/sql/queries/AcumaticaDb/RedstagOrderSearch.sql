select s.ShipmentNbr
	 , sl.LineNbr ShipmentLineNbr
	 , 'DEFAULT BOX' BoxID
	 , spl.SplitLineNbr
	 , i.InventoryID
	 , RTRIM(i.InventoryCD) InventoryCD
     , rtrim(b.AcctCD) AcctCD
	 , cast(sl.ShippedQty as int) ShipQty
	 , cast(sl.OrigOrderQty as int) OrderQty
	 , p.TrackNumber Tracking
	 , si.SiteCD
	, concat(s.ShipmentNbr, '-', RTRIM(i.InventoryCD)) ShipItem,
case when s.Status = 'C' then 'Completed'
	 when s.Status = 'N' then 'Open'
	 when s.Status = 'I' then 'Invoiced'
	 when s.Status = 'F' then 'Confirmed'
else null end ShipStatus
     , splp.PackageLineNbr
     , case when splp.PackageLineNbr is not null then 'Has Package' else 'No Package' end Package
	 , cast(k_wh.ValueNumeric as int) SentToWH
	 , case when k_dt.ValueString is not null then cast(k_dt.ValueString as datetime) else null end SentToWHDatetime
from SOShipment s
inner join SOShipLine sl on s.CompanyID = sl.CompanyID and s.ShipmentNbr = sl.ShipmentNbr  
inner join SOShipLineSplit spl on s.CompanyID = spl.CompanyID and s.ShipmentNbr = spl.ShipmentNbr  and sl.LineNbr = spl.LineNbr
inner join InventoryItem i on s.CompanyID = i.CompanyID and sl.InventoryID = i.InventoryID and spl.InventoryID = i.InventoryID 
inner join INSite si on s.CompanyID = si.CompanyID and s.SiteID = si.SiteID
left join SOShipLineSplitPackage splp on s.CompanyID = splp.CompanyID and s.ShipmentNbr = splp.ShipmentNbr
        and spl.SplitLineNbr = splp.ShipmentSplitLineNbr and splp.ShipmentLineNbr = sl.LineNbr
left join SOPackageDetail p on s.CompanyID = p.CompanyID and s.ShipmentNbr = p.ShipmentNbr and splp.PackageLineNbr = p.LineNbr
inner join BAccount b on s.CompanyID = b.CompanyID and s.CustomerID = b.BAccountID
left join SOShipmentKvExt k_wh on s.CompanyID = k_wh.CompanyID and s.NoteID = k_wh.RecordID and k_wh.FieldName = 'AttributeSHP2WH'
left join SOShipmentKvExt k_dt on s.CompanyID = k_dt.CompanyID and s.NoteID = k_dt.RecordID and k_dt.FieldName = 'AttributeSHP2WHDT'
where s.CompanyID = 2 
and left(SiteCD, 7) = 'REDSTAG'
and s.Status in('N')
and p.TrackNumber is null
and cast(k_wh.ValueNumeric as int) = 1
order by SentToWHDatetime, ShipmentNbr, ShipmentLineNbr



