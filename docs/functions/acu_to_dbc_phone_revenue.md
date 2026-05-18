# acu_to_dbc_phone_revenue
Gets all Orders created/modified within the last day having an *OrderType* of ***PH*** or ***BF*** and a non null phone number and loads to acu.PhoneRevByMonth in db_CentralStore

## Schedule
- ### :00, :30

## Execution Behavior
Executes single pipeline, **AcuToDbcPhoneRevenue**

## Pipelines

### AcuToDbcPhoneRevenue
#### `AcuToDbcPhoneRevenue` Pipeline Documentation — [pipelines/acu_to_dbc_phone_revenue.py](../../pipelines/acu_to_dbc_phone_revenue.py)
```mermaid
%%{init: {"flowchart": {"wrappingWidth": 400}}}%%
flowchart TD
    A([acu_to_dbc_phone_revenue]) --> B[AcuToDbcPhoneRevenue.__init__]
    B --> B1[inherits Pipeline]

    A--> RUN[Pipeline.run]

    RUN --> EX[extract]
    EX --> D1[(
        <b><i>AcuDb</i></b>
        AcuToDbc_PhoneRevByMonth: Query)]

    RUN --> TR[transform]
    TR --> T1[convert to list of dicts]

    RUN --> LD[load]
    LD --> L1[(
        <b><i>CentralStore</i></b>
        upsert acu.PhoneRevByMonth
    )]

    RUN --> LOGS[(
        <b><i>CentralStore</i></b>
        _util.Logs<br/>insert run logs
    )]
```



## Queries
### AcumaticaDb
 - #### [AcuToDbc_Quotes.sql](../../sql/queries/AcumaticaDb/AcuToDbc_Quotes.sql)