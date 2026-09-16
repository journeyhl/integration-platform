with TopLevel as(
select rtrim(b.AcctCD) CustomerID
	 , c.CustomerClassID CustomerClass
	 , coalesce(ltrim(rtrim(cb2b.DisplayName)), ltrim(rtrim(b.AcctName))) ContactName
	 , ltrim(rtrim(b.AcctName)) AccountName
	 , a.AddressLine1
	 , case when a.AddressLine2 = '' then null else a.AddressLine2 end AddressLine2
	 , a.City
	 , a.State
	 , left(a.PostalCode, 5) Zip
	 , a.PostalCode FullZip
	 , a.CountryID Country
	 , case when c.CustomerClassID = 'B2B' and cb2b.Phone1 is not null then cb2b.Phone1
			else coalesce(cb2b.Phone1, cb2b.Phone2) end Phone
	 , cb2b.EMail EMail
	 , c.TermsID Terms
	 , rtrim(sp.SalespersonCD) SalesPersonID
	 , sp.Descr SalesPersonName
	 , coalesce(cb2b.Phone2, cb2b.Phone3) Phone2
	 , dateadd(hour, -4, b.CreatedDateTime) CreatedOn
	 , uc.FullName CreatedBy
	 , dateadd(hour, -4, b.LastModifiedDateTime) LastModifiedDT
	 , uc.Username CreatedByUser
	 , um.Username LastModifiedByUser
	 , um.FullName LastModifiedByName
	 , b.BAccountID AccountID
	 , cb2b.ContactID ContactID
	 , b.AcctReferenceNbr CUSTEDP
	 , chs.Value HubspotLink
from BAccount b
inner join Customer c on b.CompanyID = c.CompanyID and b.BAccountID = c.BAccountID
left join Contact cb2b on b.CompanyID = cb2b.CompanyID and b.PrimaryContactID = cb2b.ContactID and b.BAccountID = cb2b.BAccountID
inner join Address a on b.CompanyID = a.CompanyID and b.DefAddressID = a.AddressID and b.BAccountID = a.BAccountID
left join CustSalesPeople csp on b.CompanyID = csp.CompanyID and b.BAccountID = csp.BAccountID
left join SalesPerson sp on b.CompanyID = sp.CompanyID and csp.SalesPersonID = sp.SalespersonID
left join Users uc on b.CompanyID = uc.CompanyID and b.CreatedByID = uc.PKID
left join Users um on b.CompanyID = um.CompanyID and b.LastModifiedByID = um.PKID
left join CSAnswers chs on b.CompanyID = chs.CompanyID and b.NoteID = chs.RefNoteID and chs.AttributeID = 'HUBSPOTID'
where b.CompanyID = 2
and c.CustomerClassID = 'B2B'
)
select *
from TopLevel
order by LastModifiedDT desc
