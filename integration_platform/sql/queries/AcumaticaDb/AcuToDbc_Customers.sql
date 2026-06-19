with TopLevel as(
select rtrim(b.AcctCD) CustomerID
	 , c.CustomerClassID CustomerClass
	 , case when c.CustomerClassID = 'B2B' then ltrim(rtrim(cb2b.DisplayName))
			when c.CustomerClassID = 'D2C' and cd2c.DisplayName is not null and cd2c.DisplayName != '' then ltrim(rtrim(cd2c.DisplayName ))
			when c.CustomerClassID = 'D2C' and (cd2c.DisplayName is null or cd2c.DisplayName = '') then ltrim(rtrim(b.AcctName))

			else coalesce(ltrim(rtrim(cb2b.DisplayName)), ltrim(rtrim(b.AcctName))) end ContactName
	 , ltrim(rtrim(b.AcctName)) AccountName
	 , a.AddressLine1
	 , case when a.AddressLine2 = '' then null else a.AddressLine2 end AddressLine2
	 , a.City
	 , a.State
	 , a.PostalCode Zip
	 , a.CountryID Country
	 , case when c.CustomerClassID = 'B2B' and cb2b.Phone1 is not null then cb2b.Phone1
			when c.CustomerClassID = 'D2C' or (cb2b.Phone1 is null and cd2c.Phone1 is not null) then cd2c.Phone1
			else coalesce(cb2b.Phone1, cd2c.Phone1) end Phone
	 , case when c.CustomerClassID = 'B2B' and cb2b.EMail is not null then cb2b.EMail
			when c.CustomerClassID = 'D2C' or (cb2b.EMail is null and cd2c.EMail is not null) then cd2c.EMail
			else coalesce(cb2b.EMail, cd2c.Email) end Email
	 , c.TermsID Terms
	 , b.BAccountID AccountID
	 , case when c.CustomerClassID = 'B2B' then cb2b.ContactID
	 		when c.CustomerClassID = 'D2C' then cd2c.ContactID
			else coalesce(cb2b.ContactID, cd2c.ContactID)
	   end ContactID
	 , b.AcctReferenceNbr CUSTEDP
	 , rtrim(sp.SalespersonCD) SalesPersonID
	 , sp.Descr SalesPersonName
	 , dateadd(hour, -4, b.CreatedDateTime) CreatedOn
	 , uc.FullName CreatedBy
	 , dateadd(hour, -4, b.LastModifiedDateTime) LastModifiedDT
	 , uc.Username CreatedByUser
	 , um.Username LastModifiedByUser
	 , um.FullName LastModifiedByName
	 , chs.Value HubspotLink
	 , case when (cb2b.Phone2 is null or cb2b.Phone2 = '') and (cd2c.Phone2 is null or cd2c.Phone2 = '') then null
            when c.CustomerClassID = 'B2B' and cb2b.Phone2 is not null and cb2b.Phone2 != '' then cb2b.Phone2
			when c.CustomerClassID = 'D2C' or (cb2b.Phone2 is null and cd2c.Phone2 is not null)  then cd2c.Phone2
            
			else coalesce(cb2b.Phone2, cd2c.Phone2) end Phone2
from BAccount b
inner join Customer c on b.CompanyID = c.CompanyID and b.BAccountID = c.BAccountID
left join Contact cb2b on b.CompanyID = cb2b.CompanyID and b.PrimaryContactID = cb2b.ContactID and b.BAccountID = cb2b.BAccountID
left join Contact cd2c on b.CompanyID = cd2c.CompanyID and b.DefContactID = cd2c.ContactID and b.BAccountID = cd2c.BAccountID
inner join Address a on b.CompanyID = a.CompanyID and b.DefAddressID = a.AddressID and b.BAccountID = a.BAccountID
left join CustSalesPeople csp on b.CompanyID = csp.CompanyID and b.BAccountID = csp.BAccountID
left join SalesPerson sp on b.CompanyID = sp.CompanyID and csp.SalesPersonID = sp.SalespersonID
left join Users uc on b.CompanyID = uc.CompanyID and b.CreatedByID = uc.PKID
left join Users um on b.CompanyID = um.CompanyID and b.LastModifiedByID = um.PKID
left join CSAnswers chs on b.CompanyID = chs.CompanyID and b.NoteID = chs.RefNoteID and chs.AttributeID = 'HUBSPOTID'
where b.CompanyID = 2
and dateadd(hour, -4, b.LastModifiedDateTime) >= dateadd(day, -1, getdate())
)
select *
from TopLevel
order by LastModifiedDT desc