select distinct ShipmentNbr
	 , TrackNumber
	 , ContentTypeDesc
from SOPackageDetail s
where s.CompanyID = 2