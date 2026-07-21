with TopLevel as(
select distinct a.OrderNbr
	 , a.ID ValueString
	 , a.LastUpdateTime
	 , row_number() over(partition by OrderNbr order by ShipmentWeight desc, LastUpdateTime desc) rownum
from acu.AftershipExportv2 a
)
select *
from TopLevel
where rownum < 8
order by OrderNbr, LastUpdateTime
