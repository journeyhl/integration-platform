from __future__ import annotations
from typing import TYPE_CHECKING, Literal
if TYPE_CHECKING:
    from integration_platform.pipelines.base import Pipeline
from integration_platform.config.settings import DATABASES, TABLES
from integration_platform.helpers.sql_helper import SQLHelper
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text
from pathlib import Path
import polars as pl
import logging
from dataclasses import dataclass
from typing import Generic, TypeVar
from datetime import datetime
from zoneinfo import ZoneInfo
#region Queries
@dataclass(frozen=True)
class Query:
    name: str
    query: str

class Queries:
    def __init__(self, database_name: str):
        database_name = 'AcumaticaDb' if database_name == 'AcudevDb' else database_name
        queries_dir = Path(__file__).resolve().parent.parent / 'sql' / 'queries' / database_name
        for sql_file in queries_dir.glob('*.sql'):
            setattr(self, sql_file.stem, Query(name=sql_file.stem, query=sql_file.read_text()))

    def __getattr__(self, name: str) -> Query:
        raise AttributeError(f"No query named '{name}'")

class CentralStoreQueries(Queries):
    '''Queries to be executed within db_CentralStore'''

    backfill_PackageCouries: Query
    '''Used for backfilling couriers onto Acumatica packages with RedStag data'''
    ReturnsPendingReciept: Query
    '''Checks **rmi_RMAStatus** for any *Closed* **or** *Receipted* **Returns**'''

    StatusCheckRMI: Query
    '''Pulls each distinct RMANumber from **rmi_ClosedShipments**, **rmi_Receipts**, and **_util.rmi_send_log**

    Looks for:
     - *null* **RMAStatuses** or any rows with a **RMAStatus** not equal to '*CLOSED*' or *blank*
    OR
     - **LastChecked** value *within the last two days* and **RMAStatus** not equal to *'OPEN'*'''
    
    AuditFulfillment: Query
    '''No query yet'''

    PackShipmentRedStag: Query
    '''This query originally drove the RedStag Confirmations celigo flow. 

    Pulls shipments from CentralStore using the **acu.rs_** tables to determine which should be shipped'''

    PackShipmentRMI: Query
    '''Pulls closed Shipments from rmi_ClosedShipments'''

    RedStagEvents: Query
    '''More robust version of PackShipment, also a redundancy. 
    
    Uses the **json.RedStagEvents** table to get all rows where **json_value(*jsonData, '$.topic')*** = ***'shipment:packed'***'''

    NotifyFulfillmentOpsTeam: Query
    '''Pulls all Open Return orders from _util.RMI_Send_Log that are stuck with the Item does not exist error from RMI
    '''
    SalesOrderCleaner: Query
    '''Pulls all Sales Orders from acu.SalesOrders that have rows with different statuses.'''
    Kustomer_FilteredOutOrders : Query
    ''''''
    RMI_Link3PL_RMAStatus: Query
    '''Pulls all distinct Shipments from RMI RMAStatus table in centralstore'''
    HubSpot_RevenueByCustomer: Query
    '''Pulls revenue by Company/Customer from acu.SalesOrders for send to Hubspot'''
    MFR_InventorySummary_Product: Query
    ''''''
    MFR_PhoneRevStaging: Query
    ''''''
    MFR_AdVersionProduct: Query
    ''''''
    MFR_AdPhonePriorityDates: Query
    ''''''
    MFR_CallCounts: Query
    ''''''
    MFR_AdDetailAdVersion: Query
    ''''''
    DarwillAddresses: Query
    ''''''
    raw_SalesSummary: Query
    ''''''    
    int_SalesSummary: Query
    ''''''
    jhl_SalesSummary: Query
    ''''''
    raw_SalesSummaryB2B: Query
    int_SalesSummaryB2B: Query
    Metrics_B2BCustomers: Query
    Metrics_B2BCustomerAge: Query
    Aftership_LinkID: Query
    MFRInsertsExport: Query
    '''Summarized pull from analytics.mfr_with_spend filtered to category = 'Inserts', grouped by ad/version/product/start_date. Exported weekly to the INC_MEDIA SFTP.'''
    B2BCohorts_OrderHistory: Query
    B2BCohorts_GenerateAttributeIDs: Query

class AcumaticaDbQueries(Queries):
    '''Queries to be executed within AcumaticaDb'''
    
    backfill_PackageCouries: Query
    '''Used for backfilling couriers onto Acumatica packages with RedStag data'''
    SendRMIReturns: Query
    '''Pulls all **RC** Sales Orders that are in **Open** status and have a *AttributeRCSHP2WH* value that is **null** or **not equal to 1**

    Where
    ---
    <hr>
    
     **OrderType** = *'RC'* 
        - OrderType is Return

     **Status** = *'N'*
        - Status is Open

     **SiteCD** = *'RMI'*
        - Warehouse is RMI

     **(AttributeRCSHP2WH** != *1* *or* **AttributeRCSHP2WH** *is null***)** 
        - RC Order has not been sent to Warehouse'''
    SendRMIShipments: Query
    '''Pulls Shipments that are ready to be sent to RMI as type Ws

    Where
    ---
    <hr>

     **OrigOrderType** != **'RC'** 
        - Original OrderType != RC

     **Status not in('C', 'L', 'F', 'I')** 
        - Completed, Cancelled, Confirmed, Invoiced

     **AttributeSHP2WH** = **0**
        - Not sent to Warehouse

     **SiteCD** = *'RMI'*
        - Warehouse is RMI'''
    SendRedStagShipments: Query
    '''Pulls Shipments that are ready to be sent to RedStag

    Where
    ---
    <hr>

     **OrigOrderType** != **'RC'** 
        - Original OrderType != RC

     **Status not in('C', 'L', 'F', 'I')** 
        - Completed, Cancelled, Confirmed, Invoiced

     **AttributeSHP2WH** = **0**
        - Not sent to Warehouse

     **left(SiteCD, 7)** = *'RedStag'* (This covers REDSTAGSWT and REDSTAGSLC)
        - Warehouse is RedStag'''
    OpenRCsNoReceipt: Query
    '''Pulls all Open RC Orders that have been sent to RMI and do not have a Shipment(Receipt)

    Where
    ---
    <hr>

     **OrderType** != **'RC'** 
        - OrderType != RC

     **Status in('N')** 
        - Status is Open

     **AttributeSHP2WH** = **1**
        - Order has been sent to the warehouse

     **SiteCD** = *'RMI'*
        - Warehouse is RMI
        
     **ShipmentNbr** *is null*
        - Order does not have a Shipment found when joining on SOLine -> SOShipLine'''
    ShipmentsReadyToConfirm: Query
    '''Pulls all *Open* Shipments that have a Tracking Number and are ready to be confirmed
    
    Where
    ---
    <hr>

     **TrackNumber is not null** 
        - TrackingNumber was able to be joined to Shipment line

     **Status = 'N'** 
        - Status is Open
        
     **left(SiteCD, 7)** = *'REDSTAG'*
        - Warehouse is REDSTAGSWT or REDSTAGSLC'''
    PackShipment: Query
    '''Query from adf that populates acu.rsFulfill

    
    Where
    ---
    <hr>

     **TrackNumber is null** 
        - TrackingNumber was NOT able to be joined to Shipment line

     **Status = 'N'** 
        - Status is Open'''
    ValidateAddresses: Query
    '''Pulls Orders that have unvalidated addresses

    Where
    ---
    <hr>

    **a.IsValidated** *is null* or **a.IsValidated** = **0**
        - Address is not valid
    
    **OrderType** != **'QT'**
         - Order is not a Quote
    
    **Status** not in *('L', 'C', 'S')*'''
    SOOrderDeletions: Query
    '''Pulls records from SOOrder that have been deleted in Acumatica for transfer to db_CentralStore'''
    SOLineDeletions: Query
    '''Pulls records from SOLine that have been deleted in Acumatica for transfer to db_CentralStore'''
    SOShipmentDeletions: Query
    '''Pulls records from SOShipment that have been deleted in Acumatica for transfer to db_CentralStore'''
    SOOrderShipmentDeletions: Query
    '''Pulls records from SOOrderShipment that have been deleted in Acumatica for transfer to db_CentralStore'''
    Kustomer_OrderIngest : Query
    """Pulls top level Order, Line and Customer data to be sent to Kustomer when **'ingest' *or* no params** are passed to :class:`~pipelines.kustomer.SendOrderDetailsToKustomer`.:meth:`~pipelines.kustomer.SendOrderDetailsToKustomer._re_init`"""
    Kustomer_OrderIngestBackfill : Query
    '''Pulls top level Order, Line and Customer data to be sent to Kustomer when **'backfill'** is passed as a param to :class:`~pipelines.kustomer.SendOrderDetailsToKustomer`.:meth:`~pipelines.kustomer.SendOrderDetailsToKustomer._re_init`'''
    Kustomer_ShipmentData : Query
    '''Pulls Shipments associated with the orders found in the Kustomer_OrderIngest (or Backfill) extract'''
    AcuToDbc_Quotes: Query
    '''Pulls Orders of QT Order Type for upsert to acu.Quotes'''
    AcuToDbc_SalesOrders: Query
    '''Pulls Sales Orders for upsert to acu.SalesOrders'''
    AcuToDbc_Shipments: Query
    '''Pulls Shipments for upsert to acu.Shipments'''
    AcuToDbc_Customers: Query
    '''Pulls Customers for upsert to acu.Customers'''
    Aftership_Shipments: Query
    '''Pulls Shipments that have tracking data to be sent to Aftership'''
    RMI_Link3PL: Query
    '''Pulls Shipments that have a null 3PL link value at RMI'''
    AcuToDbc_PhoneRevByMonth: Query
    '''Populates acu.PhoneRevByMonth table in db_CentralStore'''
    RedstagOrderSearch: Query
    '''Pulls Open RedStag shipments'''
    CosignmentReclassification: Query
    '''Pulls Completed Cosignment orders with an inventory ref document'''
    CreateShipments: Query
    '''Pulls Open Shipments that are ready to have a shipment created'''
    AllocateSalesOrders: Query
    '''Pulls Sales Orders that need to have inventory item allocated'''
    AcuToDbc_BackordersPointInTime: Query
    '''Pulls Backordered Item quantities and valuations Upserted to **acu.BackordersPointInTime**'''
    ShipChairRemovalSeparate: Query
    '''Pulls Ryder Orders that are arent already shipped and enforeces Ship Separately for chair removal orders'''
    AllocateSalesOrders_filter_address_validator: Query
    '''Ensures we're only pulling orders that have been allocated or aren't in need of allocation '''
    AcuToDbc_TrialBalance: Query
    '''Query that mirrors JHL Trial Balance GI in Acumatica. Upserted to **acu.BackordersPointInTime**'''
    AcuToDbc_InventorySummary: Query
    '''Query that mirrors JHL Inventory Summary Acumatica GI, '''
    ProductSyncHistory: Query
    '''Pulls all Shopify sync records for any Product/Product availability records'''
    AcuToDbc_B2BCollections: Query
    '''Query that mirrors JHL Trial Balance GI in Acumatica'''
    Aftership_LinkID_Acu: Query
    RyderToDbc: Query
    B2BCohorts_CustomerNoteIDs: Query
    B2BZipcodes_Customers: Query

_QUERY_CLASSES: dict[str, type[Queries]] = {
    'db_CentralStore': CentralStoreQueries,
    'AcumaticaDb': AcumaticaDbQueries,
    'AcudevDb': AcumaticaDbQueries,
}
QT = TypeVar('QT', bound=Queries)
#endregion


#MARK: SQLConnector
class SQLConnector(Generic[QT]):
    queries: QT


    def __init__(self, pipeline, database_name: str):
        ''':class:`~integration_platform.connectors.sql.SQLConnector`.:meth:`~integration_platform.connectors.sql.SQLConnector.__init__`
        ---

        Initializes the SQLConnector for either db_CentralStore or AcumaticaDb

        Parameters
        ---
        :param `pipeline`: Pipeline using the SQLConnector. If just using the Connector without a pipe, send a str
        :param (*str*) `database_name`: Name of database, either 'db_CentralStore' or 'AcumaticaDb'

        <hr>

        Returns
        ---

        <hr>

        Sets
        ---
        >>> self.pipeline = pipeline
        >>> self.logger = logging.getLogger(f'{database_name}')
        >>> if database_name not in DATABASES:
             raise ValueError(f'Unknown db!')
        >>> self.database_name = database_name
        >>> self.config = DATABASES[database_name]
        >>> self.engine = self._create_engine_()
        >>> self.raw_connection = self.engine.raw_connection()
        >>> self.queries = _QUERY_CLASSES.get(database_name, Queries)(database_name)

        **_create_engine_** creates connection string using creds from :data:`~config.settings.DATABASES`

        <hr>

        ## Upstream Calls (Methods/Functions Called by)

         - Used throughout the project — instantiated in the `__init__` of nearly every pipeline class (e.g. `self.acudb = SQLConnector(...)`, `self.centralstore = SQLConnector(...)`)

        ## Downstream Calls (Methods/Functions called)

         ### :class:`~integration_platform.connectors.sql.SQLConnector`.:meth:`~integration_platform.connectors.sql.SQLConnector._create_engine_`

          - Builds the SQLAlchemy engine used to query the database

         ### :class:`~integration_platform.connectors.sql.Queries`.:meth:`~integration_platform.connectors.sql.Queries.__init__`

          - Instantiates the query set (CentralStoreQueries/AcumaticaDbQueries) for the given database_name
        '''
        self.pipeline = pipeline
        if type(pipeline) == str:
            self.logger = logging.getLogger(f'{pipeline}.{database_name}')
        else:
            self.logger = logging.getLogger(f'{pipeline.pipeline_name}.{database_name}')
        if database_name not in DATABASES:
            raise ValueError(f'Unknown db!')
        self.tables = TABLES
        self.database_name = database_name
        self.config = DATABASES[database_name]
        self.engine = self._create_engine_()
        self.raw_connection = self.engine.raw_connection()
        self.queries = _QUERY_CLASSES.get(database_name, Queries)(database_name)  # type: ignore[assignment]
        self.sqlhelper = SQLHelper(sqldb=self)
        pass

    #MARK: _create_engine_
    def _create_engine_(self):
        password = quote_plus(str(self.config['password']))
        connection_string = (
            f"mssql+pymssql://{self.config['username']}:{password}"
            f"@{self.config['server']}/{self.config['database']}"
        )
        return create_engine(connection_string, connect_args={"tds_version": "7.3", "login_timeout": 30})



    
    #MARK: query_db
    def query_db(self, query: str, params=None, log_str=None):
        ''':class:`~integration_platform.connectors.sql.SQLConnector`.:meth:`~integration_platform.connectors.sql.SQLConnector.query_db`
        ---

        Given a string of SQL text, execute and return a polars DataFrame.

        Parameters
        ---
        :param (*str*) `query`: SQL query to execute

           ### ***Optional***
        :param (*dict = None*) `params`: Parameters to pass to query if neccessary
        :param (*dict = None*) `log_str`: String to pass to log output if neccessary. If something is passed as the log string, DO NOT log anything here

        <hr>

        Returns
        ---
        :return `data_extract` (pl.DataFrame): polars DataFrame with results of query

        <hr>

        ## Upstream Calls (Methods/Functions Called by)

         - Used throughout the project — called from pipeline `_extract_` methods and standalone scripts to run ad-hoc SQL against `db_CentralStore`/`AcumaticaDb`
        '''
        execute_options = {'parameters': params} if params else {}
        log_str = log_str if log_str else ''
        data_extract = pl.read_database(query, self.engine, execute_options=execute_options, infer_schema_length=None)
        if log_str == '':
            self.logger.info(f'Extracted {data_extract.height} rows')
        ts_extract = datetime.now(ZoneInfo(('America/New_York')))
        data_extract = data_extract.with_columns(pl.lit(value=ts_extract, dtype=pl.Datetime).alias('LastChecked'))
        return data_extract
    
    #MARK: insert_df
    def insert_df(self, df_data_loaded: pl.DataFrame, table_name: str):
        ''':class:`~integration_platform.connectors.sql.SQLConnector`.:meth:`~integration_platform.connectors.sql.SQLConnector.insert_df`
        ---

        Given a polars dataframe and the name of a table, insert the contents of the DataFrame to that table

        Parameters
        ---
        :param (*pl.DataFrame*) `df_data_loaded`: Data to be loaded into SQL db
        :param (*str*) `table_name`: The name of the table in which the contents of *df_data_loaded* will be inserted

        <hr>

        Returns
        ---

        <hr>

        ## Upstream Calls (Methods/Functions Called by)

         - Used throughout the project — called from pipeline `_load_` methods to append DataFrame contents into `db_CentralStore` tables
        '''
        df_data_loaded.write_database(table_name=table_name, 
                                      connection=self.engine,
                                      if_table_exists='append',
                                      
                                      )
        self.logger.info(f'Wrote {df_data_loaded.height} rows to {table_name}')



    #MARK: checked_upsert
    def checked_upsert(self, table_name: str, data: list):
        ''':class:`~integration_platform.connectors.sql.SQLConnector`.:meth:`~integration_platform.connectors.sql.SQLConnector.checked_upsert`
        ---

        Given a table name and a list of rows (dicts) to insert, performs an upsert to database.

        Parameters
        ---
        :param (*str*) `table_name`: The name of the table to update (schema qualified)

         - **'_util.acu_api_log'** or **'AdDetails'**

          - ***AdDetails** doesn't need the schema since it belongs to the **dbo** schema, but you could pass **'dbo.AdDetails'** if you wanted*

        :param (*list*) `data`: A list of dictionaries that correspond to the values in :data:`~config.settings.TABLES`

            * Each dictionary should be formatted to contain the values that were mapped in the table configuration in :data:`~config.settings.TABLES`

                * Take **_util.SOOrderDeletions** for example. Its definition looks as follows:
                >>> '_util.SOOrderDeletions':{
                    'keys': ['OrderType', 'OrderNbr'],
                    'columns': [
                        'OrderType',
                        'OrderNbr',
                        'DeletedBy',
                        'DeletedDatetime'
                    ],
                    'update_columns':[
                        'DeletedBy',
                        'DeletedDatetime'
                    ]
                },

                * Using these values, we'll create **upsert_string**. Starting with the check first:

                >>> if not exists(
                select 1
                from {table_name}
                where {' = %s and '.join(sql_table['keys'])} = %s
                )

                * Alrighty, replace `{table_name}` with `table_name`, or **_util.SOOrderDeletions** here. Then for each **key** in `keys`, we'll format the *where*

                >>> if not exists(
                select 1
                from _util.SOOrderDeletions
                where OrderType = %s and OrderNbr = %s
                )

                * That pattern continues on for the full execution statement.

        <hr>

        ## Upstream Calls (Methods/Functions Called by)

         - Used throughout the project — called from pipeline `_load_` methods to upsert rows into `db_CentralStore`/`AcumaticaDb` tables

        ## Downstream Calls (Methods/Functions called)

         ### :class:`~integration_platform.connectors.sql.SQLConnector`.:meth:`~integration_platform.connectors.sql.SQLConnector._dict_to_params_
          - Utility function to format table keys, columns and update_columns with their respective values to parameters
        '''
        sql_table = self.tables[table_name]
        upsert_string = f'''
if not exists(
select 1 
from {table_name}
where {' = %s and '.join(sql_table['keys'])} = %s
)
begin
insert into {table_name}({', '.join(sql_table['columns'])}  )
values({', '.join(['%s'] * len(sql_table['columns']))})
end
else
begin
update {table_name} set {' = %s, '.join(col for col in sql_table['update_columns'])} = %s
where {' = %s and '.join(sql_table['keys'])} = %s
end
'''
        try:
            params = [self._dict_to_params_(data_dict, sql_table['keys'] + sql_table['columns'] + sql_table['update_columns'] + sql_table['keys']) for data_dict in data]
            cursor = self.raw_connection.cursor()
            if len(data) > 50: self.logger.info(f'Beginning upsert of {len(data)} rows to {table_name}...')
            cursor.executemany(upsert_string, params)
            self.logger.info(f'{table_name} ╍ Upserted {len(data)} rows')
            self.raw_connection.commit()
        except Exception as e:
            self.logger.error({
                'Table': table_name,
                'err_msg': e
            })
            bp = 'here'



    #MARK: checked_upsert_paginated
    def checked_upsert_paginated(self, table_name: str, data: list, page_size: int = 100):
        ''':class:`~SQLConnector`.:meth:`~checked_upsert_paginated`
        ---

        Given a table name and a list of rows (dicts) to insert, performs a paginated upsert to database.

        #### USE :meth:`~connectors.sql.SQLConnector.checked_upsert` FOR UPSERTS OF LESS THAN 100 ROWS!!

        Parameters
        ---
        :param (*str*) `table_name`: The name of the table to update (schema qualified)

         - **'_util.acu_api_log'** or **'AdDetails'**

          - ***AdDetails** doesn't need the schema since it belongs to the **dbo** schema, but you could pass **'dbo.AdDetails'** if you wanted*

        :param (*list*) `data`: A list of dictionaries that correspond to the values in :data:`~config.settings.TABLES`

            * Each dictionary should be formatted to contain the values that were mapped in the table configuration in :data:`~config.settings.TABLES`

                * Take **_util.SOOrderDeletions** for example. Its definition looks as follows:
                >>> '_util.SOOrderDeletions':{
                    'keys': ['OrderType', 'OrderNbr'],
                    'columns': [
                        'OrderType',
                        'OrderNbr',
                        'DeletedBy',
                        'DeletedDatetime'
                    ],
                    'update_columns':[
                        'DeletedBy',
                        'DeletedDatetime'
                    ]
                },

                * Using these values, we'll create **upsert_string**. Starting with the check first:

                >>> if not exists(
                select 1
                from {table_name}
                where {' = %s and '.join(sql_table['keys'])} = %s
                )

                * Alrighty, replace `{table_name}` with `table_name`, or **_util.SOOrderDeletions** here. Then for each **key** in `keys`, we'll format the *where*

                >>> if not exists(
                select 1
                from _util.SOOrderDeletions
                where OrderType = %s and OrderNbr = %s
                )

                * That pattern continues on for the full execution statement.

           ### ***Optional***
        :param (*int = 100*) `page_size`: Number of rows to upsert per batch

        <hr>

        Returns
        ---

        <hr>

        ## Upstream Calls (Methods/Functions Called by)

         - Used throughout the project — called from pipeline `_load_` methods to upsert large row sets into `db_CentralStore`/`AcumaticaDb` tables in batches

        ## Downstream Calls (Methods/Functions called)

         ### :class:`~integration_platform.connectors.sql.SQLConnector`.:meth:`~integration_platform.connectors.sql.SQLConnector._dict_to_params_`

          - Utility function to format table keys, columns and update_columns with their respective values to parameters
        '''
        sql_table = self.tables[table_name]
        upsert_string = f'''
if not exists(
select 1 
from {table_name}
where {' = %s and '.join(sql_table['keys'])} = %s
)
begin
insert into {table_name}({', '.join(sql_table['columns'])}  )
values({', '.join(['%s'] * len(sql_table['columns']))})
end
else
begin
update {table_name} set {' = %s, '.join(col for col in sql_table['update_columns'])} = %s
where {' = %s and '.join(sql_table['keys'])} = %s
end
'''
        total, page_size, batches, upsert_batch_counter = self._init_pagination_(data=data, page_size=page_size, table_name=table_name, operation='upsert')
        for start in range(0, total, page_size):
            page = data[start:start + page_size]
            try:
                params = [self._dict_to_params_(data_dict, sql_table['keys'] + sql_table['columns'] + sql_table['update_columns'] + sql_table['keys']) for data_dict in page]
                cursor = self.raw_connection.cursor()
                cursor.executemany(upsert_string, params)
                self.raw_connection.commit()
                done = min(start + page_size, total)
                self.logger.info(f'{done}/{total} rows upserted, {len(data) - done} remain. {upsert_batch_counter + 1} Upserts complete{f", {batches - upsert_batch_counter} to go" if batches - upsert_batch_counter != 0 else ""}')
                upsert_batch_counter += 1
            except Exception as e:
                self.logger.error({
                    'Table': table_name,
                    'err_msg': e
                })
                bp = 'here'
        self.logger.info('Upsert sequence complete!')


    #MARK: update_table_paginated
    def update_table_paginated(self, table_name: str, data: list, page_size: int = 100):
        ''':class:`~integration_platform.connectors.sql.SQLConnector`.:meth:`~integration_platform.connectors.sql.SQLConnector.update_table_paginated`
        ---
        
        Similar to the checked upserts, given a table name and a list of dicts, update that table with the data passed
        
        Parameters
        ---
        :param (*str*) `table_name`: Name of SQL table
        :param (*list*) `data`: List of data to update the table with
        
                
           ### ***Optional***
        :param (*int = 100*) `page_size`: Number of rows to update per batch, *defaults to 100*
        
        ## Downstream Calls (Methods/Functions called)
        
         ### :class:`~integration_platform.connectors.sql.SQLConnector`.:meth:`~integration_platform.connectors.sql.SQLConnector._dict_to_params_`
        '''
        sql_table = self.tables[table_name]
        total, page_size, batches, update_batch_counter = self._init_pagination_(data=data, page_size=page_size, table_name=table_name, operation='update')
        sql_cmd = f"update {table_name} set {' = %s, '.join(col for col in sql_table['update_columns'])} = %s where {' = %s and '.join(sql_table['keys'])} = %s"
        cursor = self.raw_connection.cursor()
        for start in range(0, total, page_size):
            page = data[start:start + page_size]
            try:
                params = [self._dict_to_params_(row, sql_table['update_columns'] + sql_table['keys']) for row in page]
                cursor.executemany(sql_cmd, params)
                self.raw_connection.commit()
                done = min(start + page_size, total)
                self.logger.info(f'{done}/{total} rows updated, {len(data) - done} remain. {update_batch_counter + 1} updates complete{f", {batches - update_batch_counter} to go" if batches - update_batch_counter != 0 else ""}')
                update_batch_counter += 1
            except Exception as e:
                self.logger.error({
                    'Table': table_name,
                    'err_msg': e
                })
                bp = 'here'
        self.logger.info('Update sequence complete!')


    #MARK: merge_table_paginated
    def merge_table_paginated(self, table_name: str, data: list[dict], page_size: int = 500):
        sql_table = self.tables[table_name]
        total, page_size, batches, merge_batch_counter = self._init_pagination_(data=data, page_size=page_size, table_name=table_name, operation='merge')
        cursor = self.raw_connection.cursor()
        for start in range(0, total, page_size):
            page = data[start:start + page_size]
            try:
                row_placeholder = f"({', '.join(['%s'] * len(sql_table['columns']))})"
                values_clause = ', '.join([row_placeholder] * len(page))
                merge_str = f'''merge into {table_name} as target
using (values {values_clause}) as source({', '.join(sql_table['columns'])})
on {' and '.join(f'target.{key} = source.{key}' for key in sql_table['keys'])}
when matched then update set {', '.join(f'target.{column} = source.{column}' for column in sql_table['update_columns'])}
when not matched then insert ({', '.join(sql_table['columns'])})
values ({', '.join(f'source.{column}' for column in sql_table['columns'])});
'''
                params = [value for row in page for value in self._dict_to_params_(row, sql_table['columns'])]
                cursor.execute(merge_str, params)
                self.raw_connection.commit()
                done = min(start + page_size, total)
                self.logger.info(f'{done}/{total} rows merged, {len(data) - done} remain. {merge_batch_counter + 1} merges complete{f", {batches - merge_batch_counter} to go" if batches - merge_batch_counter != 0 else ""}')
                merge_batch_counter += 1
            except Exception as e:
                self.logger.error({
                    'Table': table_name,
                    'err_msg': e
                })
                bp = 'here'
        self.logger.info('Merge sequence complete!')




    #MARK: query_to_dataframe
    def query_to_dataframe(self, query: Query):
        ''':class:`~SQLConnector`.:meth:`~query_to_dataframe`
        ---

        Given a **_Query_** (see AcumaticaDbQueries and CentralStoreQueries), execute its query and return a polars dataframe

        Parameters
        ---
        :param (*Query*) `query`: An instance of the Query class, the text of which will be executed and the results output to a polars DataFrame.

        <hr>

        Returns
        ---
        :return `data` (pl.DataFrame): polars DataFrame with results of query

        <hr>

        ## Upstream Calls (Methods/Functions Called by)

         - Used throughout the project — called from pipeline `_extract_` methods to run each `Query` defined on `AcumaticaDbQueries`/`CentralStoreQueries`
        '''
        self.logger.info(f'Running {query.name} query...')
        data = pl.read_database(str(query.query), self.engine, infer_schema_length = None)
        self.logger.info(f'{data.height} rows returned')
        ts_extract = datetime.now(ZoneInfo(('America/New_York')))
        data_extract = data.with_columns(pl.lit(value=ts_extract, dtype=pl.Datetime).alias('LastChecked'))
        return data_extract

    #MARK: raw_execute
    def raw_execute(self, query: str):
        ''':class:`~SQLConnector`.:meth:`~raw_execute`
        ---

        Given an Insert, Update or Delete command, execute on db

        Parameters
        ---
        :param (*str*) `query`: Query to be executed in Database as plain text

        <hr>

        Returns
        ---

        <hr>

        ## Upstream Calls (Methods/Functions Called by)

         - Used throughout the project — called from pipeline `_load_` methods and standalone scripts to run raw delete/update commands against `db_CentralStore`/`AcumaticaDb`
        '''
        cursor = self.raw_connection.cursor()
        self.logger.info(f'Executing query with raw_execute')
        db_msg = cursor.execute(query)
        self.raw_connection.commit()
        if cursor.rowcount:
            self.logger.info(f'{cursor.rowcount} rows {'deleted' if 'delete' in query else 'affected'}')
        bp = 'here'



    def get_file_as_dataframe(self, type: Literal['csv', 'xlsx'], path: str = '') -> pl.DataFrame:
        ''':class:`~integration_platform.connectors.sftp.SFTP`.:meth:`~integration_platform.connectors.sftp.SFTP.get_file_as_dataframe`
        ---
        
        Given a path to a csv or xlsx file on an SFTP server, open the file and return its contents as a Polars DataFrame
        
        Parameters
        ---
        :param (**Literal***['csv', 'xlsx']*) `type`: The filetype of the file found at *path*, must be csv or xlsx
        
                
           ### ***Optional***
        :param (*str = '/apps/five9/reports/CallSegments3.csv'*) `path`: Path that the file is found at, defaults to `/apps/five9/reports/CallSegments3.csv`
        
        Returns
        ---
        :return `df_file` (pl.DataFrame): dataframe of the file contents found at the passed path
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.pipelines.ucmi_hubspot.UCMI_HubspotCustomers`.:meth:`~integration_platform.pipelines.ucmi_hubspot.UCMI_HubspotCustomers.extract`
        
         ### :class:`~integration_platform.pipelines.five9_call_segments.Five9CallSegments`.:meth:`~integration_platform.pipelines.five9_call_segments.Five9CallSegments.extract`
           
         ### :class:`~integration_platform.pipelines.darwill_addresses.DarwillAddresses`.:meth:`~integration_platform.pipelines.darwill_addresses.DarwillAddresses.extract`
        '''
        try:
            with open(path, 'rb') as f:
                file_contents = f.read()
                df_file = pl.read_csv(file_contents, infer_schema_length=0) if type == 'csv' else pl.read_excel(file_contents, infer_schema_length=0)
            self.logger.info(f'Successfully parsed {df_file.height} rows from {path}')
            ts_extract = datetime.now(ZoneInfo(('America/New_York')))
            data_extract = df_file.with_columns(pl.lit(value=ts_extract, dtype=pl.Datetime).alias('LastChecked'))
            return data_extract
        except Exception as e:
            self.logger.error(f"Error! {e} Couldn't parse {path}")
            return pl.DataFrame()



    #MARK: _dict_to_params_
    def _dict_to_params_(self, d: dict, keys: list) -> tuple:
        ''':class:`~integration_platform.connectors.sql.SQLConnector`.:meth:`~integration_platform.connectors.sql.SQLConnector._dict_to_params_`
        ---

        Utility function used to format table keys, columns and update_columns with their respective values to parameters

        Parameters
        ---
        :param (*dict*) `d`: dict containing the data to be inserted to database
        :param (*list*) `keys`: list containing the names of keys, columns and update_columns of table receiving insert

        <hr>

        Returns
        ---
        :return `params` (tuple): values from `d` ordered to match `keys`, for use as SQL execute parameters

        <hr>

        ## Upstream Calls (Methods/Functions Called by)

         ### :class:`~integration_platform.connectors.sql.SQLConnector`.:meth:`~integration_platform.connectors.sql.SQLConnector.checked_upsert`

          - Calls this to format each row's values into positional parameters before executing the upsert

         ### :class:`~integration_platform.connectors.sql.SQLConnector`.:meth:`~integration_platform.connectors.sql.SQLConnector.checked_upsert_paginated`

          - Calls this to format each row's values into positional parameters before executing each paginated batch upsert
        
         ### :class:`~integration_platform.connectors.sql.SQLConnector`.:meth:`~integration_platform.connectors.sql.SQLConnector.update_table_paginated`
        '''
        return tuple(d[k.replace('[', '').replace(']', '')] for k in keys)
    


    #MARK: _init_pagination_
    def _init_pagination_(self, data: list, page_size: int, table_name: str, operation: Literal['upsert', 'update', 'insert', 'merge']):
        ''':class:`~integration_platform.connectors.sql.SQLConnector`.:meth:`~integration_platform.connectors.sql.SQLConnector._init_pagination_`
        ---
        
        Method to replace code that was used across all paginating SQLConnector methods
        
        Parameters
        ---
        :param (*list*) `data`: list of data that will be sent to database
        :param (*int*) `page_size`: How many rows will be sent per batch
        :param (*str*) `table_name`: Name of table to will be effected
        :param (*Literal['upsert', 'update', 'insert', 'merge']*) `operation`: **'upsert'**, **'update'**, **'insert'**, or **'merge'**. Used for log outputs
        
        Returns
        ---
        :return `total` (int): Total number of rows that will be sent to db
        :return `page_size` (int): How many rows to send per command
        :return `batches` (int): How many batches the list of data will be split up into for pagination
        :return `counter` (int): 0
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.connectors.sql.SQLConnector`.:meth:`~integration_platform.connectors.sql.SQLConnector.update_table_paginated`
         ### :class:`~integration_platform.connectors.sql.SQLConnector`.:meth:`~integration_platform.connectors.sql.SQLConnector.checked_upsert_paginated`
         ### :class:`~integration_platform.connectors.sql.SQLConnector`.:meth:`~integration_platform.connectors.sql.SQLConnector.merge_table_paginated`
        '''        
        total = len(data)
        page_size = total if page_size > total else page_size
        batches = int(total/page_size)
        counter = 0
        self.logger.info(f'{total} rows to {operation}')
        self.logger.info(f'Beginning {operation} sequence of {total} rows in {batches + 1} batches to {table_name}...')
        return (total, page_size, batches, counter)