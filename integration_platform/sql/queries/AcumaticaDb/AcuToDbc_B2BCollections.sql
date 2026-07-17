with TopLevel as(
select rtrim(b.AcctCD) CustomerID
	 , b.AcctName CustomerName
	 , r.RefNbr
	 , r.OrigRefNbr
	 , cast(r.DocDate as date) DocDate
	 , cast(r.DueDate as date) DueDate
	 , jr.Status DocStatus
	 , datediff(DAY, r.duedate, getdate()) DaysOverdue
	 , cast(i.CuryUnpaidBalance as decimal(18,2)) CuryUnpaidBalance
	 , cast(getdate() as date) Today
	 , c.TermsID
	 , rtrim(sp.SalespersonCD) SalespersonID
	 , sp.Descr Salesperson
	 , a.State
	 , a.City
	 , jc.Status CustomerStatus
	 , coalesce(co.Phone1, co.Phone2, co.Phone3) Phone
	 , co.Phone1 Phone1
	 , co.Phone2 Phone2
	 , co.Phone3 Phone3
	 , co.Email Email
	 , coalesce(ac.Phone1, ac.Phone2, ac.Phone3) InvoicePhone_Coalesce
	 , ac.Phone1 InvoicePhone1
	 , ac.Phone2 InvoicePhone2
	 , ac.Phone3 InvoicePhone3
	 , ac.Email InvoiceEmail
	 , c.SendStatementByEmail
from BAccount b
inner join Customer c on b.CompanyID = c.CompanyID and b.BAccountID = c.BAccountID
inner join ARRegister r on b.CompanyID = r.CompanyID and b.BAccountID = r.CustomerID
inner join ARInvoice i on b.CompanyID = i.CompanyID and r.DocType = i.DocType and r.RefNbr = i.RefNbr
inner join ARContact ac on b.CompanyID = ac.CompanyID and b.BAccountID = ac.CustomerID and i.BillContactID = ac.ContactID
inner join Contact co on b.CompanyID = co.CompanyID and b.BAccountID = co.BAccountID and c.DefBillContactID = co.ContactID
inner join Address a on b.CompanyID = a.CompanyID and b.BAccountID = a.BAccountID and b.DefAddressID = a.AddressID
inner join JJStatusLookup jr on r.Status = jr.CStatus and jr.Tbl = 'ARRegister'
inner join JJStatusLookup jc on b.Status = jc.CStatus and jc.Tbl = 'BAccount'
left join CustSalesPeople csp on b.CompanyID = csp.CompanyID and b.BAccountID = csp.BAccountID
left join SalesPerson sp on b.CompanyID = sp.CompanyID and csp.SalesPersonID = sp.SalespersonID
where b.CompanyID = 2
and c.CustomerClassID = 'B2B'
and c.SendStatementByEmail = 1
and jr.Status = 'Open'
)
select t.CustomerID
	 , t.CustomerName
	 , t.RefNbr
	 , t.OrigRefNbr
	 , t.DocDate
	 , t.DueDate
	 , t.DocStatus
	 , t.DaysOverdue
	 , case when t.DueDate >= Today  then cast(t.CuryUnpaidBalance as decimal(18,2)) else 0 end CurrentBalance
	 , case when t.DaysOverdue > 0  and t.DaysOverdue <= 30 then t.CuryUnpaidBalance else 0 end Balance_1_30d
	 , case when t.DaysOverdue > 30 and t.DaysOverdue <= 60 then t.CuryUnpaidBalance else 0 end Balance_31_60d
	 , case when t.DaysOverdue > 60 and t.DaysOverdue <= 90 then t.CuryUnpaidBalance else 0 end Balance_61_90d
	 , case when t.DaysOverdue > 90 then t.CuryUnpaidBalance else 0 end Balance_90d
	 , t.CuryUnpaidBalance TotalBalance
	 , t.SalespersonID
	 , t.TermsID
	 , t.CustomerStatus
	 , t.State
	 , t.Phone
	 , t.Email
	 , t.SendStatementByEmail
	 , t.InvoicePhone1
	 , t.InvoiceEmail
	 , t.Phone1
	 , t.Phone2
	 , t.Phone3
	 , t.InvoicePhone_Coalesce
	 , t.InvoicePhone2
	 , t.InvoicePhone3
from TopLevel t
order by duedate desc
