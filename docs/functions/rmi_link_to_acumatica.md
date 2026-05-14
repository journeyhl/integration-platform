# rmi_link_to_acumatica
Gets all QT type Sales Orders from AcumaticaDb that were modified within the last day and loads them to **acu.Quotes**

## Schedule
- ### :00, :30

## Execution Behavior
Executes single pipeline, **RMILinkToAcu**

## Pipelines

### RMILinkToAcu
#### `RMILinkToAcu` Pipeline Documentation — [pipelines/rmi_link_to_acu.py](../../pipelines/rmi_link_to_acu.py)
```mermaid here
```

## Queries
### AcumaticaDb
 - #### [AcuToDbc_Quotes.sql](../../sql/queries/AcumaticaDb/AcuToDbc_Quotes.sql)