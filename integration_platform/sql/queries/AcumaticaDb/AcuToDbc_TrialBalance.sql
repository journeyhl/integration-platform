with TopLevel as(
select a.AccountCD
	 , a.Type TypeID
	 , case when a.Type = 'A' then 'Asset' 
			when a.Type = 'L' then 'Liability' 
			when a.Type = 'I' then 'Income'
			when a.type = 'E' then 'Expense'
		else null end Type
	 , s.SubCD
	 , concat(left(s.SubCD, 3),  '-', left(right(s.SubCD, 5), 3), '-', right(s.SubCD, 2)) Sub
	 , a.Description
	 , g.FinPeriodID
	 , concat(right(g.FinPeriodID, 2), '-', left(g.FinPeriodID, 4)) FinPeriod
	 , cast(g.CuryFinBegBalance as decimal(18,2)) BeginningBalance
	 , cast(g.CuryFinPtdDebit as decimal(18,2)) Debit
	 , cast(g.CuryFinPtdCredit as decimal(18,2)) Credit
	 , cast(g.CuryFinBegBalance + g.CuryFinPtdDebit  - g.CuryFinPtdCredit as decimal(18,2)) EndingBalance
	 , cast(f.StartDate as date) StartDate
	 , cast(f.EndDate as date) EndDate
from GLHistory g
inner join Account a on g.CompanyID = a.CompanyID and g.AccountID = a.AccountID
inner join Sub s on g.CompanyID = s.CompanyID and g.SubID = s.SubID
inner join FinPeriod f on g.CompanyID = f.CompanyID and g.FinPeriodID = f.FinPeriodID and f.OrganizationID = 2
where g.CompanyID = 2
and (g.CuryFinBegBalance != 0 or g.CuryFinYtdBalance != 0)

)
select t.AccountCD
	 , t.Type
	 , t.Sub
	 , t.Description
	 , t.FinPeriod
	 , t.BeginningBalance
	 , t.Debit
	 , t.Credit
	 , t.EndingBalance
	 , t.StartDate
	 , t.EndDate
	 , t.TypeID
	 , t.SubCD
	 , t.FinPeriodID
from TopLevel t
order by StartDate
