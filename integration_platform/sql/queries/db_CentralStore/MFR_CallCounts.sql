with EmployeeDeptRaw as(
select *
     , row_number() over(partition by e.EmployeeID order by StartDate desc) ord
     , lead(StartDate) over(partition by EmployeeID order by startdate) EndDate
from acu.EmployeeDept e
)
,EmployeeDept as(
select e.EmployeeID
     , e.Name
     , e.Department
     , e.Username
     , e.StartDate
     , case when e.EndDate is null then cast(getdate()+7 as date) else e.EndDate end EndDate
from EmployeeDeptRaw e
)
, TopLevel as(
select cast(Timestamp as date) Date
	 , case when Skill like '%PlusOne%' then 'plusone' else LOWER(e.Name) end Agent
     , e.Department
	 , f.CalledParty
	 , f.CallingParty CustomerPhone_CallingParty
	 , f.DNIS 
	 , f.ANI CustomerPhone_ANI
	 , f.TalkDuration
	 , f.CallDuration
	 , f.HandleDuration
	 , datepart(month, f.Timestamp) Year
	 , datepart(year, f.Timestamp) Month
	 , concat(datepart(Year, f.Timestamp), 
		'-',case when datepart(month, f.Timestamp) < 10 then concat('0', datepart(month, f.Timestamp)) else concat('', datepart(month, f.Timestamp)) end
	   ) FinPeriod
	 , case when Skill like '%SleepChair%' then 'Perfect Sleep Chair'
			when Skill like '%Scooter%' and Skill like '%TV%' then 'Scooter TV'
			when Skill like '%Scooter%' then 'So Lite Scooter'
			when Skill like '%SoLiteWheelchair%' then 'So Lite Wheelchair'
			when Skill like '%Zinger%' and Skill like '%TV%' then 'Zinger TV'
			when Skill like '%Zinger%' then 'Zinger'
			when Skill like '%Zoomer%' and Skill like '%TV%' then 'Zoomer TV'
			when Skill like '%Zoomer%' then 'Zoomer'
			when Skill like '%AirElite%' then 'Air Elite'
			when Skill like '%Air%' then 'Air'
			when Skill like '%Independence%' then 'Upbed Independence'
			when Skill like '%Upbed%' then 'Upbed'
			when Skill like '%Glide%' then 'Glide'
			when Skill like '%Upwalker%' then 'Upwalker'
			when Skill like 'SA-Internet%' then 'Internet'
			when Skill like '%Luxe%' then 'Luxe Scooter'
			when Skill like '%Catalog%' then 'Catalog'
			when Skill like '%Standard%' then 'Standard'
			when Skill like '%MemberPub%' then 'Member Pub'
            when Skill = 'SA-Wow' then 'Wow'
		else 'Other'
	   end SkillProduct
     , Skill RawSkill
	 , case when cast(TalkDuration as time) < '00:01:30' then '0:00 - 1:30 mins'
		    when cast(TalkDuration as time) >= '01:00:00' then '60+  mins'
		    when cast(TalkDuration as time) >= '00:30:00' then '30 - 60 mins'
		    when cast(TalkDuration as time) >= '00:20:00' then '20 - 30 mins'
		    when cast(TalkDuration as time) >= '00:15:00' then '15 - 20 mins'
		    when cast(TalkDuration as time) >= '00:10:00' then '10 - 15 mins'
		    when cast(TalkDuration as time) >= '00:05:00' then '05:00 - 10 mins'
		    when cast(TalkDuration as time) >= '00:03:00' then '03:00 - 5 mins'
		    when cast(TalkDuration as time) >= '00:02:00' then '02:00 - 3 mins'
		    when cast(TalkDuration as time) >= '00:01:30' then '01:30 - 2 mins'
		else null 
	  end TalkDurationStr
	 , case when cast(TalkDuration as time) < '00:01:30' then 1 else 0 end Abandoned
	 , case when cast(TalkDuration as time) < '00:01:30' then 'No' else 'Yes' end [Longer Than 90 Seconds]
	 , datepart(weekday, f.timestamp) DayOfWeek
	 , case when datepart(weekday, f.timestamp) in(2, 3, 4, 5, 6) and datepart(hour, f.timestamp) >= 9 and DATEPART(hour, f.timestamp) <= 19
		then 1
		else 0 
	   end DuringBusinessHours
	 
	 , (cast(right(left(f.TalkDuration, 5), 2) as int) * 60) + 
	   + (cast(left(f.TalkDuration, 2) as int) * 3600)
	   + (cast(right(f.TalkDuration, 2) as int)) 
	   TalkSeconds
	 , (cast(right(left(f.CallDuration, 5), 2) as int) * 60) + 
	   + (cast(left(f.CallDuration, 2) as int) * 3600)
	   + (cast(right(f.CallDuration, 2) as int)) 
	   CallSeconds
	 , (cast(right(left(f.HandleDuration, 5), 2) as int) * 60) + 
	   + (cast(left(f.HandleDuration, 2) as int) * 3600)
	   + (cast(right(f.HandleDuration, 2) as int)) 
	   HandleSeconds
	  , f.AfterCallWorkDuration
	 , (cast(right(left(f.AfterCallWorkDuration, 5), 2) as int) * 60) + 
	   + (cast(left(f.AfterCallWorkDuration, 2) as int) * 3600)
	   + (cast(right(f.AfterCallWorkDuration, 2) as int)) 
	   AfterCallWorkSeconds
     , TimeStamp
	 , SessionID
     , cast(cast(Timestamp as date) as varchar(20)) DStr

from Five9CallSegments f
left join EmployeeDept e on left(f.CalledParty, charindex('@', f.CalledParty) - 1) = replace(e.Username, 'journeyhl.com\', '') and cast(f.Timestamp as date) >= e.StartDate and cast(f.Timestamp as date) < e.EndDate
where CallType = 'Inbound'
-- and TalkDuration is not null
and TalkDuration <> '00:00:00'
and Skill not like '%CS%'
--and Skill not like '%Cust%'
--and Skill not like '%SA-Retail%'
--and Skill not like '%Test%'
--and e.Name is not null
)
--order by Date desc, Timestamp desc
select *
from TopLevel t
