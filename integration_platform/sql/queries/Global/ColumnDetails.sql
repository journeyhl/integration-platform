select distinct concat(s.name, '.', t.Name) Qualified
	 , c.Name ColName
	 , tt.Name TypeName
	 , c.max_length MaxLength
from sys.schemas s
inner join sys.tables t on s.schema_id = t.schema_id
inner join sys.columns c on t.object_id = c.object_id
inner join sys.types tt on c.system_type_id = tt.system_type_id