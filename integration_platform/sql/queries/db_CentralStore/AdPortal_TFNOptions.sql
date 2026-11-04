
with base as(
select distinct d.AdCode
	, d.PrimaryAdName OldAd
	, p.AdCode pAdCode
	, v.AdVersionID
	, p.TFN
	, v.Product
	, d.Category
	, p.StartDate
	, ROW_NUMBER() over(partition by TFN order by p.StartDate desc) Number

from AdPhone p
left join AdDetails d on p.AdCode = d.AdCode
left join AdVersionDetails v on d.AdVersionID = v.AdVersionID
where p.TFN not in(
'8884041724',
'8006161583',
'8006161762',
'8042259083',
'8045249889',
'8662563020',
'8668161858',
'8668167973') and p.TFN not like '%NotRouted%'
)
select *
from base b
where b.Number = 1 and b.StartDate <= getdate()-365
and b.TFN != '8884041724'
order by StartDate desc