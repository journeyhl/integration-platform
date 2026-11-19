
select distinct d.AdCode, PrimaryAdName, Category, p.TFN, d.DateCreated
from AdDetails d
left join AdPhone p on d.AdCode = p.AdCode and d.StartDate = p.StartDate
order by DateCreated desc