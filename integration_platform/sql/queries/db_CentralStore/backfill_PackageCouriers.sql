
with TopLevel as(

	select json_value(jsonData, '$.topic') Topic
		 , json_value(jsonData, '$.message.order_unique_id')  ShipmentNbr_3pl
		 , json_query(jsonData, '$.message.packages') Packages
		 , json_query(jsonData, '$.message.trackers') Trackers
		 , json_query(jsonData, '$.message') msg
         , jsonData
	from json.RedStagEvents
	where json_value(jsonData, '$.topic') in('shipment:packed', 'shipment:shipped')
	--and json_value(jsonData, '$.message.order_unique_id')= '089185'
),
acuShipments as(

	select distinct ShipmentNbr
	from acu.Shipments s

)
, FinalLevel as(
select t.Topic
	 , t.ShipmentNbr_3pl
	 , t.Packages
	 , t.Trackers
	 , json_query(t.Packages, '$[*].items') Items
	 , json_value(t.Packages, '$[*].manifest_courier') Courier
	 , json_query(t.Packages, '$[*].tracking_numbers') TrackingNumbers
	 , t.msg
     , t.jsonData
from TopLevel t
inner join acuShipments a on t.ShipmentNbr_3pl = a.ShipmentNbr
)
select distinct ShipmentNbr_3pl
     , TrackingNumbers
     , Courier
from FinalLevel
where Courier is not null
-- where t.ShipmentNbr_3pl = '080584'