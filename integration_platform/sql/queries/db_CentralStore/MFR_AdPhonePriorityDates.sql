with AdPhonePriority as(
select p.*
     , row_number() over (partition by p.TFN order by p.StartDate) Priority
	 , case when d.AdCode is not null then 1 else 0 end MatchingAdCodeDate
from AdPhone p
left join AdDetails d on p.AdCode = d.AdCode and p.StartDate = d.StartDate
where p.TFN is not null 
and p.TFN != '' and p.TFN not like '#%' 
and left(p.TFN, 9) != 'NotRouted'
and left(p.TFN, 3) != 'OoD'
)
select p.*
	 , case when Priority = 1 and (select StartDate from AdPhonePriority a where a.TFN = p.TFN and a.Priority = 2)  is not null then (select dateadd(DAY, -1, StartDate) from AdPhonePriority a where a.TFN = p.TFN and a.Priority = 2)
	 		when Priority = 2 and (select StartDate from AdPhonePriority a where a.TFN = p.TFN and a.Priority = 3)  is not null then (select dateadd(DAY, -1, StartDate) from AdPhonePriority a where a.TFN = p.TFN and a.Priority = 3)
	 		when Priority = 3 and (select StartDate from AdPhonePriority a where a.TFN = p.TFN and a.Priority = 4)  is not null then (select dateadd(DAY, -1, StartDate) from AdPhonePriority a where a.TFN = p.TFN and a.Priority = 4)
	 		when Priority = 4 and (select StartDate from AdPhonePriority a where a.TFN = p.TFN and a.Priority = 5)  is not null then (select dateadd(DAY, -1, StartDate) from AdPhonePriority a where a.TFN = p.TFN and a.Priority = 5)
	 		when Priority = 5 and (select StartDate from AdPhonePriority a where a.TFN = p.TFN and a.Priority = 6)  is not null then (select dateadd(DAY, -1, StartDate) from AdPhonePriority a where a.TFN = p.TFN and a.Priority = 6)
	 		when Priority = 6 and (select StartDate from AdPhonePriority a where a.TFN = p.TFN and a.Priority = 7)  is not null then (select dateadd(DAY, -1, StartDate) from AdPhonePriority a where a.TFN = p.TFN and a.Priority = 7)
	 		when Priority = 7 and (select StartDate from AdPhonePriority a where a.TFN = p.TFN and a.Priority = 8)  is not null then (select dateadd(DAY, -1, StartDate) from AdPhonePriority a where a.TFN = p.TFN and a.Priority = 8)
	 		when Priority = 8 and (select StartDate from AdPhonePriority a where a.TFN = p.TFN and a.Priority = 9)  is not null then (select dateadd(DAY, -1, StartDate) from AdPhonePriority a where a.TFN = p.TFN and a.Priority = 9)
	 		when Priority = 9 and (select StartDate from AdPhonePriority a where a.TFN = p.TFN and a.Priority = 10) is not null then (select dateadd(DAY, -1, StartDate) from AdPhonePriority a where a.TFN = p.TFN and a.Priority = 10)
	 	else '20991231' 
	   end EndDate
from AdPhonePriority p