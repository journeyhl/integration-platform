
select b.DefAddressID
     , b.AcctCD
     , a.AddressLine1
     , a.City
     , a.State
     , a.CountryID
     , a.IsValidated
     , b.BAccountID
     , a.AddressID
     , concat('update Address set IsValidated = 1 where CompanyID = 2 and BAccountID = ', b.BAccountID, ' and AddressID = ', a.AddressID) UpdateStatement
from BAccount b inner join
		Address a on b.DefAddressID = a.AddressID and b.CompanyID = a.CompanyID
where b.CompanyID = 2 and AcctCD = ''
