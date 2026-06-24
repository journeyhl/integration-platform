with AdVersionProduct as(

select distinct v.AdVersionID,
case when Product = 'PSC' then 'Perfect Sleep Chair'
	 when Product in('SL', 'SL Glide', 'So Lite Glide', 'SoLite Glide') then 'SoLite Glide'
	 when Product in('SL Scooter', 'So Lite Scooter', 'SoLite Scooter', 'Scootle') then 'SoLite Scooter'
	 when Product in('SL WheelChair', 'So Lite Wheelchair', 'SoLite Wheelchair', '') then 'SoLite Wheelchair'
	 when Product in('Zinger', 'Zinger Power Chair', 'ZingerZoomer') then 'Zinger'
	 when Product in('Zoomer', 'Zoomer Power Chair') then 'Zoomer'
	 when Product in('Upbed Shop') then 'UpBed'
	 when Product in('Upbed Shop') then 'UpBed'
	 when Product in('Upbed Shop') then 'UpBed'
	--  when Product in('Various') then 'Multiple Products'
	 when Product in('Various') then 'Other'
else Product end MFRProduct
	 , v.Product
	 , v.PrimaryVersionName
	 , v.SecondaryVersionName
from AdVersionDetails v)

select distinct d.AdCode
	, d.PrimaryAdName
	, d.Category
	, v.AdVersionID
	, v.MFRProduct
	, v.Product
	, d.StartDate
	, d.SecondaryAdName
	, v.PrimaryVersionName
	, v.SecondaryVersionName
from AdDetails d
left join AdVersionProduct v on d.AdVersionID = v.AdVersionID