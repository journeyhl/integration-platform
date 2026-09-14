select distinct s.CompanyID
	 , s.ShipmentNbr
	 , TrackNumber
	--  , ContentTypeDesc
from SOPackageDetail s
inner join soshipment sh on s.CompanyID = sh.CompanyID and s.ShipmentNbr = sh.ShipmentNbr
where s.CompanyID = 2
and s.ContentTypeDesc is null
and s.TrackNumber is not null
and sh.[Status] in ('C', 'F')