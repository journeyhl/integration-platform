with TopLevel as(
select concat(s.name, '.', t.name) Qualified
	 , s.name sName
	 , t.name tName
from sys.schemas s
inner join sys.tables t on s.schema_id = t.schema_id
)
select *
from TopLevel
--where Qualified like '%five9%'

