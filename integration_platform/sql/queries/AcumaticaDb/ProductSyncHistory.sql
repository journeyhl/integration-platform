select b.SyncID
	 , b.ConnectorType
	 , b.EntityType
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
left join BCSyncDetail d on b.CompanyID = d.CompanyID and b.SyncID = d.SyncID
inner join JJStatusLookup j on b.Status = j.CStatus and j.Tbl = 'BCSyncStatus'
left join InventoryItem i on b.CompanyID = i.CompanyID and b.LocalID = i.NoteID 
where b.CompanyID = 2 and b.EntityType in('IN', 'NS', 'PA', 'VP')
order by LastOperationTS desc
