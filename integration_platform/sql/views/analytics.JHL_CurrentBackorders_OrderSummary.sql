create view analytics.JHL_CurrentBackorders_OrderSummary
as
with TopLevel as(
	select datediff(day, dateadd(hour, -4, getdate()), DatePlaced) DaysOnBackorder
		 , row_number() over(partition by OrderNumber, LineNbr, Date order by Timestamp desc) PITdesc
		 , *
	from acu.BackordersPointInTime
	where date = cast(getdate() as date)
	and ShipmentNbr is null and Completed != 1
)
, SecondLevel as(
	select  *
		 , case when DaysOnBackorder <= -30 then 'TRUE' else 'FALSE' end OlderThanMonth
		 , case when CustomerID in(
		 'C0094735', 'C0095766', 'C0094286', 'C0095499', 
		 'C0095736', 'C0096269', 'C0038129', 'C0095097', 'C0094930', 
		 'C0095569', 'C0093876', 'C0095432', 'C0094175', 'C0094046', 'C0095618', 'C0078584', 'C0095499', 'C0092556', 'C0095463', 'C0095370', 'C0094489', 'C0094286', 'C0092722', 'C0094480', 'C0038129', 'C0095320', 'C0093923', 'C0094175', 'C0093638', 'C0091408', 'C0044970', 'C0095136', 'C0094864', 'C0094175', 'C0094517', 'C0094691', 'C0094046', 'C0093923', 'C0092672', 'C0093638', 'C0092722', 'C0044970', 'C0094286', 'C0093923', 'C0094480', 'C0089560', 'C0092976', 'C0092976', 'C0091408', 'C0093903', 'C0094517', 'C0074349', 'C0092722', 'C0092615', 'C0092446', 'C0092672', 'C0093638', 'C0074349', 'C0091408', 'C0091475', 'C0092479', 'C0090976', 'C0092615', 'C0092272', 'C0089560', 'C0091441', 'C0092553', 'C0092060', 'C0091475', 'C0091626', 'C0092479', 'C0090850', 'C0090967', 'C0090976', 'C0088363', 'C0088363', 'C0091475', 'C0091475', 'C0091441', 'C0092446', 'C0092060', 'C0092672', 'C0092514', 'C0092657', 'C0092420', 'C0089484', 'C0092670', 'C0091995', 'C0090850', 'C0091847', 'C0090601', 'C0091768', 'C0091191', 'C0088411', 'C0089558', 'C0066642', 'C0090881', 'C0088883', 'C0090779', 'C0090105', 'C0088913', 'C0089607', 'C0088883', 'C0088411', 'C0088280', 'C0090041', 'C0089065', 'C0087931', 'C0086450', 'C0088548', 'C0089260', 'C0072085', 'C0089750', 'C0089167', 'C0008106', 'C0088883', 'C0089414', 'C0089364', 'C0087934', 'C0088473', 'C0086799', 'C0089529', 'C0089065', 'C0088837', 'C0088881', 'C0086799', 'C0029712', 'C0086799', 'C0086799', 'C0088109', 'C0088411', 'C0089166', 'C0089166', 'C0086450', 'C0086387', 'C0088584', 'C0088584', 'C0089364', 'C0088109', 'C0089036', 'C0089166', 'C0089166', 'C0087743', 'C0086799', 'C0086799', 'C0085596', 'C0087169', 'C0087396', 'C0088518', 'C0087743', 'C0085492', 'C0087637', 'C0087576', 'C0086509', 'C0086719', 'C0087109', 'C0008580', 
		 'C0008580', 'C0086552', 'C0086387', 'C0087169', 
		 'C0083562', 'C0083562', 'C0073987'
		) then 'TRUE' else 'FALSE' end Chargeback
	from TopLevel
	where PITdesc = 1 --and DaysOnBackorder <= -30
)
select DaysOnBackorder
	 , OlderThanMonth
	 , OrderType
	 , OrderNumber
	 , DatePlaced
	 , CustomerID
	 , CustomerName
	 , CustomerClass
	 , sum(Quantity) QtyBackordered
	 , sum(cast(LinePrice as decimal(18,2))) PriceBackordered
	 , sum(cast(DiscountAmt as decimal(18,2))) DiscBackordered
	 , sum(cast(LineAmount as decimal(18,2))) AmtBackordered
	 , sum(cast(LineCost as decimal(18,2))) CostBackordered
	 , sum(cast(FreightTotal as decimal(18,2))) FreightBackordered
	 , Phone
	 , Email
	 , AddressLine1
	 , AddressLine2
	 , City
	 , State
	 , Zip
	 , D2CSalesperson
	 , SalespersonName
	 , SalespersonEmail
	 , B2BSalesperson
	 , CreatedDT
	 , CreatedBy
	 , LastModifiedDT
	 , LastModifiedBy
	 , Chargeback
from SecondLevel
group by DaysOnBackorder
	 , OlderThanMonth
	 , OrderType
	 , OrderNumber
	 , DatePlaced
	 , CustomerID
	 , CustomerName
	 , CustomerClass
	 , Phone
	 , Email
	 , AddressLine1
	 , AddressLine2
	 , City
	 , State
	 , Zip
	 , D2CSalesperson
	 , SalespersonName
	 , SalespersonEmail
	 , B2BSalesperson
	 , CreatedDT
	 , CreatedBy
	 , LastModifiedDT
	 , LastModifiedBy
	 , Chargeback
