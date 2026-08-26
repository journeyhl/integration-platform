with TopLevel as(

select cast(s.ShipDate as date) ShipDate
	 , s.ShipmentNbr
	 , j.Status AcuStatus
	 , cast(k.ValueNumeric as int) SentToWH
	 , sl.OrigOrderNbr 
	 , sl.OrigOrderType
	 , s.ShipVia
	 , sl.LineNbr LineNumber
	 , cast(sl.ShippedQty as int) ShippedQty
	 , rtrim(i.InventoryCD) InventoryCD
	 , l.ShipVia a
     , concat(sl.OrigOrderNbr, '-', l.LineNbr) PO
	 , case when i.InventoryCD = '27222' then 'RT' else 'AA' end rlmActionCode
	 , case when i.InventoryCD = '27222' then 'RT' else 'DL' end rlmOrderType
	 , case when i.InventoryCD != '27222' and l.ShipVia in('WHITEGLOVE399', 'WHITEGLOVE450', 'WHITEGLOVE499', 'WHITEGLOVESHP') then 'WD'
	 		when i.InventoryCD = '27222' then 'HA'
			else 'HL' end rlmDeliveryType
--=IIf(([SOLine.ShipVia] = 'WHITEGLOVE399' or [SOLine.ShipVia] = 'WHITEGLOVE450' or [SOLine.ShipVia] = 'WHITEGLOVE499' or [SOLine.ShipVia] = 'WHITEGLOVESHP') and [SOLine.InventoryID] <> '612', 'WD', IIf([SOLine.InventoryID] = '612', 'HA', 'HL'))

	 , 'JHLCM' OriginShipperCode
	 , i.Descr ItemDescr
	 , ic.Descr ItemClassDescr
	 , case when s.ShipVia is null or s.ShipVia = 'GROUND' then 'FDXG'
		when s.ShipVia = '2DAY' then 'FED2' else null end ShipCode
	 , 'Fedex' ShipPriority
	 , rtrim(c.AcctCD) CustomerID
	 , left(sc.FullName, 35) ShipToName
	 , left(c.AcctName, 35) CompanyName
	 , coalesce(sc.email, 'cs@journeyhl.com') ShipToEmailContact
	 , coalesce(sc.Phone1, sc.Phone2) ShipToPhone
	 , sa.AddressLine1 ShipToAddress1
	 , sa.AddressLine2 ShipToAddress2
	 , sa.City ShipToCity
	 , sa.State ShipToState
	 , sa.PostalCode ShipToZip
	 , sa.CountryID ShipToCountry
	, case when i.InventoryCD in('01025','08371','01102','08824','08505','08305','08307','08369','08939','08835','08306') 
				then 'cheapest_GROUND'
			when s.ShipVia in ('GROUND', 'PSC150THRES', 'WHITEGLOVE399', 'WHITEGLOVE450', 'WHITEGLOVE499') and i.Descr like '%battery%' 
	  			then 'cheapest_UPS'
			when s.ShipVia in ('GROUND', 'PSC150THRES', 'WHITEGLOVE399', 'WHITEGLOVE450', 'WHITEGLOVE499')
				then 'cheapest_ALL'
			when s.ShipVia = '2DAY'
				then 'cheapest_TWO_DAY'
			when s.ShipVia = 'LTL'
				then 'external_ltl'
	  else 'cheapest_ALL' end rsShipVia
	, s.CustomerOrderNbr
	 , kr.ValueString RyderID
	
	

from SOShipment s
inner join SOShipLine sl on s.CompanyID = sl.CompanyID and s.ShipmentType = sl.ShipmentType and s.ShipmentNbr = sl.ShipmentNbr
inner join SOShipLineSplit shl on s.CompanyID = shl.CompanyID and s.ShipmentNbr = shl.ShipmentNbr and sl.LineNbr = shl.LineNbr
inner join SOLine l on s.CompanyID = l.CompanyID and shl.OrigOrderType = l.OrderType and shl.OrigOrderNbr = l.OrderNbr and shl.OrigLineNbr = l.LineNbr
-- inner join solinesplit
inner join SOContact sc on s.CompanyID = sc.CompanyID and s.ShipContactID = sc.ContactID and s.CustomerID = sc.CustomerID
inner join SOAddress sa on s.CompanyID = sa.CompanyID and s.ShipAddressID = sa.AddressID and s.CustomerID = sa.CustomerID
inner join BAccount c on s.CompanyID = c.CompanyID and s.CustomerID = c.BAccountID
inner join InventoryItem i on s.CompanyID = i.CompanyID and sl.InventoryID = i.InventoryID
inner join INItemClass ic on s.CompanyID = ic.CompanyID and i.ItemClassID = ic.ItemClassID
inner join INSite isi on s.CompanyID = isi.CompanyID and s.SiteID = isi.SiteID
left join SOShipmentKvExt k on s.CompanyID = k.CompanyID and s.NoteID = k.RecordID and k.FieldName = 'AttributeSHP2WH'
left join SOShipmentKvExt kr on s.CompanyID = kr.CompanyID and s.NoteID = kr.RecordID and kr.FieldName = 'AttributeRYDERAPIID'
left join SOShipmentKvExt krc on s.CompanyID = krc.CompanyID and s.NoteID = krc.RecordID and krc.FieldName = 'AttributeRYDERCHECK'
left join SOShipmentKvExt kre on s.CompanyID = kre.CompanyID and s.NoteID = kre.RecordID and kre.FieldName = 'AttributeRYDERERROR'
left join JJStatusLookup j on s.Status = j.CStatus and j.Tbl = 'SOShipment'
where s.CompanyID = 2 
and SiteCD = 'RLM NEJ HB' and sl.OrigOrderType != 'RC'
and s.Status not in('C', 'L', 'F', 'I')
-- and k.ValueNumeric = 0 --Uncomment this line
-- s.ShipmentNbr = '077252' and sl.LineNbr = 1		--This line is to send one offs
-- and s.ShipmentNbr != '083252'
)
select *
from TopLevel
order by ShipmentNbr, LineNumber