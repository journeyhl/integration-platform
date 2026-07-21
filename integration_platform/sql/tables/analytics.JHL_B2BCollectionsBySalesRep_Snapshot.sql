if not exists(
	select *
	from sys.schemas s
	where s.name = 'analytics'
)
begin
	exec('create schema analytics');
end
if not exists(
	select * 
	from sys.tables t 
	inner join sys.schemas s on t.schema_id = s.schema_id
	where t.name = 'JHL_B2BCollectionsByStatus_Snapshot' and s.name = 'analytics'
)
begin
	create table analytics.JHL_B2BCollectionsBySalesRep_Snapshot(
	SalespersonID varchar(30) not null,
	CurrentBalance decimal(18,2),
	Balance_1_30d decimal(18,2),
	Balance_31_60d decimal(18,2),
	Balance_61_90d decimal(18,2),
	Balance_90d decimal(18,2),
	TotalBalance decimal(18,2),
	Timestamp datetime not null,
	primary key(SalespersonID, Timestamp))
end

