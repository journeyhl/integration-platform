
select distinct rtrim(i.InventoryCD) InventoryCD
	 , i.Descr Description
	 , (select value from CSAnswers c where i.CompanyID = c.CompanyID and i.NoteID = c.RefNoteID and c.AttributeID = 'DEPTH') Depth
	 , (select value from CSAnswers c where i.CompanyID = c.CompanyID and i.NoteID = c.RefNoteID and c.AttributeID = 'LENGTH') Length
	 , (select value from CSAnswers c where i.CompanyID = c.CompanyID and i.NoteID = c.RefNoteID and c.AttributeID = 'WIDTH') Width
	 , cast(i.BaseVolume as decimal(18,2)) Volume
	 , cast(i.BaseWeight as decimal(18,2)) Weight
	 , cast(i.BasePrice as decimal(18,2)) Price
	 , cast(its.LastCost as decimal(18,2)) Cost
	 , (select value from CSAnswers c where i.CompanyID = c.CompanyID and i.NoteID = c.RefNoteID and c.AttributeID = 'OLDSKU') oldSKU
	 , rtrim(v.AcctCD) VendorID
	 , case when i.ItemType = 'F' then 'Finished Good' when i.ItemType = 'M' then 'Component Part' when i.ItemType = 'A' then 'Subassembly' else 'N/A' end ItemType
	 , rtrim(ic.ItemClassCD) ItemClass
	 , i.PostClassID PostingClass
	 , i.TaxCategoryID TaxCategory
	 , rtrim(ins.SiteCD) DefaultWH
	 , ir.ReplenishmentClassID ReplenishmentClass
	 , cast(ir.MinQty as decimal(18,2)) RC_Min
	 , cast(ir.MaxQty as decimal(18,2)) RC_Max
	 , ix1.AlternateID VendorPartNumber
	 , ix2.AlternateID UPC
	 , ic.Descr ItemClassDesc
	 , dateadd(hour, -4, i.LastModifiedDateTime) LastModifiedDT
     , count(ix1.AlternateID) over(partition by InventoryCD) Distinct_VendorPartNumbers




	 , (select value from CSAnswers c where i.CompanyID = c.CompanyID and i.NoteID = c.RefNoteID and c.AttributeID = 'EDPNO') EDPNO
from InventoryItem i
inner join INItemClass ic on i.CompanyID = ic.CompanyID and i.ItemClassID = ic.ItemClassID
inner join InventoryItemCurySettings iics on i.CompanyID = iics.CompanyID and i.InventoryID = iics.InventoryID
left join INItemStats its on i.CompanyID = its.CompanyID and i.InventoryID = its.InventoryID and (i.DfltSiteID = its.SiteID or its.SiteID is null)
left join INItemRep ir on i.CompanyID = ir.CompanyID and i.InventoryID = ir.InventoryID
left join INItemXRef ix1 on i.CompanyID = ix1.CompanyID and i.InventoryID = ix1.InventoryID and ix1.AlternateType = '0VPN' and i.InventoryCD != ix1.AlternateID
left join INItemXRef ix2 on i.CompanyID = ix2.CompanyID and i.InventoryID = ix2.InventoryID and ix2.AlternateType = 'GIN'
left join BAccount v on i.CompanyID = v.CompanyID and i.PreferredVendorID = v.BAccountID
left join INSite ins on i.CompanyID = ins.CompanyID and i.DfltSiteID = ins.SiteID
where i.CompanyID = 2
and i.IsTemplate = 0 and (ix2.BAccountID != 18242 or ix2.BAccountID is null)