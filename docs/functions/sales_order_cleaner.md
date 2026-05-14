# sales_order_cleaner
Gets all QT type Sales Orders from AcumaticaDb that were modified within the last day and loads them to **acu.Quotes**

## Schedule
- ### :00, :30

## Execution Behavior
Executes single pipeline, **SalesOrderCleaner**

## Pipelines

### SalesOrderCleaner
#### `SalesOrderCleaner` Pipeline Documentation — [pipelines/sales_order_cleaner.py](../../pipelines/sales_order_cleaner.py)
```mermaid here
```

## Queries
### AcumaticaDb
 - #### [AcuToDbc_Quotes.sql](../../sql/queries/AcumaticaDb/AcuToDbc_Quotes.sql)