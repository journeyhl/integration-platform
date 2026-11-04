select max(cast(AdCode as int)) + 1 AdCode
from AdDetails
where AdCode NOT LIKE '%[A-Za-z]%' and
left(cast(AdCode as int), 1) = '6'