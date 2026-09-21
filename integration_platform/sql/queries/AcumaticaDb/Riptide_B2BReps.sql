with TopLevel as(
select rtrim(b.AcctCD) CustomerID
	 , c.CustomerClassID CustomerClass
	 , ltrim(rtrim(b.AcctName)) AccountName
	 , rtrim(sp.SalespersonCD) SalesPersonCD
	 , sp.Descr SalesPersonName
	 , left(a.PostalCode, 5) Zip
	 , a.PostalCode FullZip
	 , coalesce(ltrim(rtrim(cb2b.DisplayName)), ltrim(rtrim(b.AcctName))) ContactName
	 , a.AddressLine1
	 , case when a.AddressLine2 = '' then null else a.AddressLine2 end AddressLine2
	 , a.City
	 , a.State
	 , a.CountryID Country
	 , case when c.CustomerClassID = 'B2B' and cb2b.Phone1 is not null then cb2b.Phone1
			else coalesce(cb2b.Phone1, cb2b.Phone2) end Phone
	 , cb2b.EMail EMail
	 , c.TermsID Terms
	 , b.BAccountID BAccountID
     , sp.SalespersonID
from BAccount b
inner join Customer c on b.CompanyID = c.CompanyID and b.BAccountID = c.BAccountID
left join Contact cb2b on b.CompanyID = cb2b.CompanyID and b.PrimaryContactID = cb2b.ContactID and b.BAccountID = cb2b.BAccountID
inner join Address a on b.CompanyID = a.CompanyID and b.DefAddressID = a.AddressID and b.BAccountID = a.BAccountID
left join CustSalesPeople csp on b.CompanyID = csp.CompanyID and b.BAccountID = csp.BAccountID
left join SalesPerson sp on b.CompanyID = sp.CompanyID and csp.SalesPersonID = sp.SalespersonID
left join Users uc on b.CompanyID = uc.CompanyID and b.CreatedByID = uc.PKID
left join Users um on b.CompanyID = um.CompanyID and b.LastModifiedByID = um.PKID
where b.CompanyID = 2
and c.CustomerClassID = 'B2B'
)
select *
from TopLevel
-- order by LastModifiedDT desc
