# aftership_to_dbc
Gets all QT type Sales Orders from AcumaticaDb that were modified within the last day and loads them to **acu.Quotes**

## Schedule
- ### :00, :30

## Execution Behavior
Executes single pipeline, **AfterShipToDbc**

## Pipelines

### AfterShipToDbc
#### `AfterShipToDbc` Pipeline Documentation — [pipelines/aftership_to_dbc.py](../../pipelines/aftership_to_dbc.py)
```mermaid here
```

## Queries
### AcumaticaDb
 - #### [AcuToDbc_Quotes.sql](../../sql/queries/AcumaticaDb/AcuToDbc_Quotes.sql)