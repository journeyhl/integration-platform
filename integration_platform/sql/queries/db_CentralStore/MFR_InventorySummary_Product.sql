
select distinct i.InventoryCD, i.Description,
case when i.Description like '%Air Elite%' then 'Air Elite'
	 when i.Description like '%Adventure%' then 'Adventure'
	 when i.Description like '%Upwalker%' then 'Upwalker'
	 when i.Description like '%Spectrum%' then 'Balanced Spectrum'
	 when i.Description like '%Toilet Lift%' then 'Toilet Lift'
	 when i.Description like '%Journey Air%' then 'Journey Air'
	 when i.Description like 'Luxe%' then 'Luxe Scooter'
	 when i.Description like '%Magnifier%' then 'Magnifier'
	 when i.Description LIKE '%Perfect%' AND i.Description LIKE '%Sleep%' AND i.Description LIKE '%Chair%' THEN 'Perfect Sleep Chair'
	 when i.Description like '%SoLite Glide%' or i.Description like '%So Lite Glide%' then 'SoLite Glide'
	 when i.Description like '%SoLite Wheel%' or i.Description like '%So Lite Wheel%' or i.Description like '%SoLite C1%' or i.Description like '%So Lite C1%' then 'SoLite Wheelchair'
	 when i.Description like '%SoLite Scoot%' or i.Description like '%So Lite Scoot%' or i.Description like '%SoLite S1%' or i.Description like '%So Lite S1%' then 'SoLite Scooter'
	 when i.Description like '%Zinger%' then 'Zinger'
	 when i.Description like '%Zoomer%' then 'Zoomer'
	 when i.Description like '%Upbed Independence%' then 'Upbed Independence'
	 when i.Description like '%Upbed%' and i.Description not like '%Upbed Independence%' then 'Upbed'
	 when i.ItemClass like '%Mobility%' then 'Mobility'
	 when i.Description like '%Bedside Assist Rail%' then 'Bed Rail'
	 when i.Description like '%Journey Adjustable Height Overbed Table%' then 'JMH Adjustable Bed'
     when ItemClassDesc = 'Bath Products' then 'Bath'
	 else 'Other' end Product
    , i.ItemClassDesc 
from acu.InventorySummary i
order by Product