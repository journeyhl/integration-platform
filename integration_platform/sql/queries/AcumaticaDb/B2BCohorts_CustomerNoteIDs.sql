
select rtrim(b.AcctCD) CustomerID
	 , b.BAccountID
	 , b.AcctName
	 , c.CustomerClassID
	 , b.Status acuStatus
	 , j.Status 
	 , b.NoteID
from BAccount b
inner join Customer c on b.CompanyID = c.CompanyID and b.BAccountID = c.BAccountID
inner join JJStatusLookup j on b.Status = j.CStatus and j.Tbl = 'BAccount'
where b.CompanyID = 2 and c.CustomerClassID = 'B2B'