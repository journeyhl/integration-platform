with TopLevel as(
select sh.ShipmentNbr
     , shl.LineNbr ShipLineNbr
     , jsh.Status
     , s.OrderNbr
     , l.LineNbr OrderLineNbr
     , cast(s.OrderDate as date) OrderDate
	 , rtrim(i.InventoryCD) InventoryCD
     , cast(l.OrderQty as int) OrderQTY
     , cast(shl.ShippedQty as int) ShipQTY
     , cast(sh.ShipDate as date) ShipDate
     , rtrim(b.AcctCD) CustomerID
     , sc.FullName
     , sc.Email
     , sa.AddressLine1
     , sa.AddressLine2
     , sa.City
     , sa.[State]
     , sa.CountryID Country
     , sa.PostalCode Zip
     , rtrim(si.SiteCD) WarehouseID
     , sh.PackageCount
     , cast(l.CuryLineAmt as decimal (18,2)) SOLinePrice
     , cast(sh.FreightCost as decimal (18,2)) FreightCost
     , cast(k_wh.ValueNumeric as int) SenttoWH
     , cast(k_dt.ValueString as datetime) SentToWHDatetime
	 , dateadd(hour, -4, sh.LastModifiedDateTime) LastModifiedDT
     , ltrim(rtrim(p.TrackNumber)) Tracking
     , dateadd(hour, -4, p.CreatedDateTime) TrackingCreatedDate
     , coalesce(sc.Phone1, sc.Phone2) CustomerPhone
     , sc.Attention
     , rtrim(s.ShipVia) ShipVia
     , k_c.ValueString Carrier
     , k_cc.ValueString CourierCode
     , k_cn.ValueString CourierName
     , dateadd(hour, -4, sh.ConfirmedDateTime) ConfirmedDatetime
     , dateadd(hour, -4, sh.CreatedDateTime) CreatedDatetime

     , p.[Description] PackageDescr
     , case when left(ltrim(rtrim(p.TrackNumber)), 1) = '9' 
                then 'usps'
            when left(ltrim(rtrim(p.TrackNumber)), 1) = '8' or left(ltrim(rtrim(p.TrackNumber)), 2) in('38', '39', '87')
                then 'fedex'
            when left(ltrim(rtrim(p.TrackNumber)), 2) = '1Z'
                then 'ups'
        else null end CarrierAlt
	 , replace(uc.Username, 'journeyhl.com\', '')	CreatedBy
	 , replace(um.Username, 'journeyhl.com\', '')	LastModifiedBy
    
from SOOrder s
inner join SOLine l on s.CompanyID = l.CompanyID and s.OrderNbr = l.OrderNbr and s.OrderType = l.OrderType and s.CustomerID = l.CustomerID
left join SOContact sc on s.CompanyID = sc.CompanyID and s.CustomerID = sc.CustomerID and s.ShipContactID = sc.ContactID /*Shipping contact*/
left join SOAddress sa on s.CompanyID = sa.CompanyID and s.ShipAddressID = sa.AddressID and s.CustomerID = sa.CustomerID /*Shipping address*/
inner join SOShipLine shl on s.CompanyID = shl.CompanyID and s.OrderType = shl.OrigOrderType and s.OrderNbr = shl.OrigOrderNbr and l.LineNbr = shl.OrigLineNbr and l.InventoryID = shl.InventoryID
inner join SOShipment sh on s.CompanyID = sh.CompanyID and shl.ShipmentNbr = sh.ShipmentNbr and shl.ShipmentType = sh.ShipmentType
inner join SOShipLineSplit spl on s.CompanyID = spl.CompanyID and sh.ShipmentNbr = spl.ShipmentNbr and shl.LineNbr = spl.LineNbr
left join SOShipLineSplitPackage splp on s.CompanyID = splp.CompanyID and sh.ShipmentNbr = splp.ShipmentNbr and shl.LineNbr = splp.ShipmentLineNbr and spl.SplitLineNbr = splp.ShipmentSplitLineNbr
left join SOPackageDetail p on s.CompanyID = p.CompanyID and sh.ShipmentNbr = p.ShipmentNbr and splp.PackageLineNbr = p.LineNbr
inner join BAccount b on s.CustomerID = b.BAccountID and s.CompanyID = b.CompanyID 
inner join Customer c on b.BAccountID = c.BAccountID and s.CompanyID = c.CompanyID
left join INSite si on s.CompanyID = si.CompanyID and l.SiteID = si.SiteID
inner join InventoryItem i on s.CompanyID = i.CompanyID and l.InventoryID = i.InventoryID
left join INSite shi on s.CompanyID = shi.CompanyID and shl.SiteID = shi.SiteID /*Warehouse joined on SOShipLine*/
left join Users uc on s.CompanyID = uc.CompanyID and sh.CreatedByID = uc.PKID
left join Users um on s.CompanyID = um.CompanyID and sh.LastModifiedByID = um.PKID
left join SOShipmentKvExt k_wh on sh.CompanyID = k_wh.CompanyID and sh.NoteID = k_wh.RecordID and k_wh.FieldName = 'AttributeSHP2WH'
left join SOShipmentKvExt k_dt on sh.CompanyID = k_dt.CompanyID and sh.NoteID = k_dt.RecordID and k_dt.FieldName = 'AttributeSHP2WHDT'
left join SOShipmentKvExt k_lk on sh.CompanyID = k_lk.CompanyID and sh.NoteID = k_lk.RecordID and k_lk.FieldName = 'AttributeLINK3PL'
left join SOShipmentKvExt k_c on sh.CompanyID = k_c.CompanyID and sh.NoteID = k_c.RecordID and k_c.FieldName = 'AttributeCARRIER'
left join SOShipmentKvExt k_cc on sh.CompanyID = k_cc.CompanyID and sh.NoteID = k_cc.RecordID and k_cc.FieldName = 'AttributeCOURCODE'
left join SOShipmentKvExt k_cn on sh.CompanyID = k_cn.CompanyID and sh.NoteID = k_cn.RecordID and k_cn.FieldName = 'AttributeCOURNAME'
left join JJStatusLookup jsh on sh.Status = jsh.CStatus and jsh.Tbl = 'SOShipment'
where s.CompanyID = 2 
and dateadd(hour, -4, sh.LastModifiedDateTime) >=  dateadd(hour, -1, getdate())
-- and dateadd(hour, -4, sh.LastModifiedDateTime) >=  dateadd(day, -120, getdate())
-- and dateadd(hour, -4, s.LastModifiedDateTime) >=  dateadd(day, -1, getdate())
-- and s.OrderNbr = 'PH145626'
-- and s.LastModifiedDateTime >= cast(getdate()-30 as date)
-- order by LastModifiedDT desc


/*
Updated Query to only pull sales orders from the last two hours.
s.LastModifiedDateTime
*/
)
select t.ShipmentNbr
     , t.ShipLineNbr
     , t.Status
     , t.OrderNbr
     , t.OrderLineNbr
     , t.OrderDate
     , t.InventoryCD
     , t.OrderQTY
     , t.ShipQTY
     , t.ShipDate
     , t.CustomerID
     , t.FullName AccountName
     , t.Email
     , t.AddressLine1
     , t.AddressLine2
     , t.City
     , t.State
     , t.Country
     , t.Zip
     , t.WarehouseID
     , t.PackageCount
     , t.SOLinePrice
     , t.FreightCost
     , t.SenttoWH
    --InsertedDatetime
     , t.LastModifiedDT
     , t.Tracking
     , t.TrackingCreatedDate
     , t.CustomerPhone
     , t.Attention
     , t.ShipVia
     , coalesce(t.Carrier, t.CarrierAlt) Carrier
     , t.CourierCode
     , t.CourierName
     , t.ConfirmedDatetime
     , t.CreatedDatetime     
     , t.SentToWHDatetime 
     , t.PackageDescr
     , t.CreatedBy
     , t.LastModifiedBy
from TopLevel t
order by LastModifiedDT desc