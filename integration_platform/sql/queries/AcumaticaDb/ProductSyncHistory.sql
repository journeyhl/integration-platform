select b.SyncID
	 , b.ConnectorType
	 , b.EntityType
	 , je.Status Entity
	 , rtrim(i.InventoryCD) InventoryCD
	 , b.LocalID
	 , b.LocalTS
	 , b.ExternID
	 , b.ExternDescription
	 , b.PendingSync
	 , b.Status acuStatus
	 , j.Status
	 , b.LastOperation
	 , b.LastOperationTS
	 , b.Deleted
	 , b.SyncInProcess
	 , b.AttemptCount
	 , b.NoteID
	 , case when d.SyncID is not null then 1 else 0 end HasSyncDetailRecord
from BCSyncStatus b 
left join BCSyncDetail d on b.CompanyID = d.CompanyID and b.SyncID = d.SyncID and b.LocalID = d.LocalID
inner join JJStatusLookup j on b.Status = j.CStatus and j.Tbl = 'BCSyncStatus'
inner join JJStatusLookup je on b.EntityType = je.CStatus and je.Tbl = 'BCSyncStatus.Entity'
left join InventoryItem i on b.CompanyID = i.CompanyID and b.LocalID = i.NoteID 
where b.CompanyID = 2 and b.EntityType in('IN', 'NS', 'PA', 'VP')
and j.Status = 'Prepared'
order by LastOperationTS desc
