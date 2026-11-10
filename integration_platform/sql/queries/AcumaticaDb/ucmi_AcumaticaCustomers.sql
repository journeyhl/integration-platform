select  rtrim(b.AcctCD) CustomerID
	 , b.AcctName Customer
	 , case when c.CustomerClassID = 'B2B' then cb2b.DisplayName
			when c.CustomerClassID = 'D2C' and cd2c.DisplayName is not null and cd2c.DisplayName != '' then cd2c.DisplayName 
			when c.CustomerClassID = 'D2C' and (cd2c.DisplayName is null or cd2c.DisplayName = '') then b.AcctName

			else cb2b.DisplayName end ContactName
	 , c.CustomerClassID
	 , a.AddressLine1
	 , case when a.AddressLine2 = '' then null else a.AddressLine2 end AddressLine2
	 , a.City
	 , left(a.State, 2) State
	 , a.PostalCode
	 , a.CountryID
	 , case when c.CustomerClassID = 'B2B' and cb2b.Phone1 is not null then cb2b.Phone1
			when c.CustomerClassID = 'D2C' or (cb2b.Phone1 is null and cd2c.Phone1 is not null) then cd2c.Phone1
			else cb2b.Phone1 end Phone
	 , case when c.CustomerClassID = 'B2B' and cb2b.EMail is not null then cb2b.EMail
			when c.CustomerClassID = 'D2C' or (cb2b.EMail is null and cd2c.EMail is not null) then cd2c.EMail
			else cb2b.EMail end Email
	 , rtrim(sp.SalespersonCD) SalespersonCD
	 , sp.Descr Salesperson
	 , c.TermsID Terms
	 , b.CreatedDateTime
	 , uc.Username CreatedByUser
	 , uc.FullName CreatedByName
	 , b.LastModifiedDateTime
	 , um.Username LastModifiedByUser
	 , um.FullName LastModifiedByName
	 , b.BAccountID
	 , a.AddressID
	 , cb2b.ContactID ContactID_B2B
	 , cd2c.ContactID ContactID_D2C
	 , chs.Value HubspotLink
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
and b.LastModifiedDateTime >= getdate()-2
order by LastModifiedDateTime desc