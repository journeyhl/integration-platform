# acu_to_dbc_quotes
Gets all QT type Sales Orders from AcumaticaDb that were modified within the last day and loads them to **acu.Quotes**

## Schedule
- ### :00, :30

## Execution Behavior
Executes single pipeline, **UpdateAfterShip**

## Pipelines

### UpdateAfterShip
#### `UpdateAfterShip` Pipeline Documentation — [pipelines/aftership_update.py](../../pipelines/aftership_update.py)
```mermaid here
```

## Queries
### AcumaticaDb
 - #### [AcuToDbc_Quotes.sql](../../sql/queries/AcumaticaDb/AcuToDbc_Quotes.sql)