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
	where t.name = 'JHL_B2BCollectionsSummary_Snapshot' and s.name = 'analytics'
)
begin
	create table analytics.JHL_B2BCollectionsSummary_Snapshot(
	CustomerID varchar(15) not null,
	CustomerName varchar(255),
	SalespersonID varchar(20),
	TermsID varchar(12),
	CustomerStatus varchar(25),
	State varchar(20),
	Email varchar(255),
	Phone varchar(15),
	CurrentBalance decimal(18,2),
	Balance_1_30d decimal(18,2),
	Balance_31_60d decimal(18,2),
	Balance_61_90d decimal(18,2),
	Balance_90d decimal(18,2),
	TotalBalance decimal(18,2),
	Timestamp datetime not null,
	primary key(CustomerID, Timestamp))
end