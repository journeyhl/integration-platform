
select distinct r.RMANumber
     , r.RMAID
     , concat('https://jhl.returnsmanagement.com/rma/LineItems.asp?rmaid=', r.RMAID) Link3PL
     , r.RMAType
     , r.RMATypeName
from rmi_RMAStatus r
where r.RMAType not in('3', '4')
