
from integration_platform.pipelines.base import Pipeline
from datetime import datetime
from zoneinfo import ZoneInfo
import polars as pl
from integration_platform.connectors.sql import SQLConnector, AcumaticaDbQueries
from typing import Literal
class ModularAcuToDbc(Pipeline):
    def __init__(self, function, table_name: Literal['acu.BackordersPointInTime', 'acu.Account', 'acu.ARAdjust', 'acu.ARRegister', 'acu.ARTran', 'acu.CADeposit', 'acu.CADepositCharge', 'acu.CADepositDetail', 'acu.CashAccount', 'acu.CATran', 'acu.InventorySummary', 'acu.PhoneRevByMonth', 'acu.Quotes', 'acu.SalesOrders', 'acu.Shipments', 'acu.Sub', 'acu.TrialBalance']):
        super().__init__(pipeline_name=f'ModularAcuToDbc', function=function)
        self.acudb: SQLConnector[AcumaticaDbQueries] = SQLConnector(pipeline=self, database_name='AcumaticaDb')
        self.table_name = table_name
        self._set_mapping_()
        self.query = self.map[table_name]

    def extract(self) -> pl.DataFrame:
        data_extract = self.acudb.query_to_dataframe(query=self.query)
        return data_extract
    

    def transform(self, data_extract: pl.DataFrame) -> list:
        data_transformed = data_extract.to_dicts()
        return data_transformed
    

    def load(self, data_transformed):
        total = len(data_transformed)
        now =  datetime.now(ZoneInfo('America/New_York'))
        data_transformed = self.default_loader.add_to_list(data_transformed, {'InsertedDT': now})
        self.logger.info(f'{total} rows to merge into {self.table_name}')
        if total > 0:
            self.centralstore.merge_table_paginated(table_name=self.table_name, data=data_transformed, page_size=100)
        bp = 'here'
        return data_transformed


    def log_results(self, data_loaded):
        pass

    def rerun(self, table_name: Literal['acu.BackordersPointInTime', 'acu.Account', 'acu.ARAdjust', 'acu.ARRegister', 'acu.ARTran', 'acu.CADeposit', 'acu.CADepositCharge', 'acu.CADepositDetail', 'acu.CashAccount', 'acu.CATran', 'acu.InventorySummary', 'acu.PhoneRevByMonth', 'acu.Quotes', 'acu.SalesOrders', 'acu.Shipments', 'acu.Sub', 'acu.TrialBalance']):
        ''':class:`~integration_platform.pipelines.acu_to_dbc.ModularAcuToDbc`.:meth:`~integration_platform.pipelines.acu_to_dbc.ModularAcuToDbc.rerun`
        ---
        
        Reconfigures pipeline to be used with a different table than that of which it was initialized with, then executes pipeline
        
        Parameters
        ---
        :param (*Literal*) `table_name`: string value of one of the tables that has been configured for use in ModularAcuToDbc pipe
        
        <hr>
        
        Sets
        ---
        - #### self.:meth:`~integration_platform.pipelines.acu_to_dbc.ModularAcuToDbc.query`
        - #### self.:meth:`~integration_platform.pipelines.acu_to_dbc.ModularAcuToDbc.table_name`
        
        <hr>
        
        ## Downstream Calls (Methods/Functions called)
        
         ### :class:`~integration_platform.pipelines.base.Pipeline`.:meth:`~integration_platform.pipelines.base.Pipeline._init_logging_`
        
          - Reinitializes logs for next pipeline execution
        
         ### :class:`~integration_platform.pipelines.acu_to_dbc.ModularAcuToDbc`.:meth:`~integration_platform.pipelines.base.Pipeline.run`
        
          - Executes pipeline via base/super class
        '''
        super()._init_logging_()
        self.query = self.map[table_name]
        self.table_name = table_name
        self.run()

    def _set_mapping_(self):
        ''':class:`~integration_platform.pipelines.acu_to_dbc.ModularAcuToDbc`.:meth:`~integration_platform.pipelines.acu_to_dbc.ModularAcuToDbc._set_mapping_`
        ---
        
        Called at Pipeline initialization. Sets self.:attr:`~integration_platform.pipelines.acu_to_dbc.ModularAcuToDbc.map`, which is used to bind each table to its respective extraction query
        
        <hr>
        
        Sets
        ---
        - #### self.:attr:`~integration_platform.pipelines.acu_to_dbc.ModularAcuToDbc.map`
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.pipelines.acu_to_dbc.ModularAcuToDbc`.:meth:`~integration_platform.pipelines.acu_to_dbc.ModularAcuToDbc.__init__`
        '''        
        self.map = {
            'acu.BackordersPointInTime': self.acudb.queries.AcuToDbc_BackordersPointInTime,
            'acu.Account': self.acudb.queries.AcuToDbc_Account,
            'acu.ARAdjust': self.acudb.queries.AcuToDbc_ARAdjust,
            'acu.ARRegister': self.acudb.queries.AcuToDbc_ARRegister,
            'acu.ARTran': self.acudb.queries.AcuToDbc_ARTran,
            'acu.CADeposit': self.acudb.queries.AcuToDbc_CADeposit,
            'acu.CADepositCharge': self.acudb.queries.AcuToDbc_CADepositCharge,
            'acu.CADepositDetail': self.acudb.queries.AcuToDbc_CADepositDetail,
            'acu.CashAccount': self.acudb.queries.AcuToDbc_CashAccount,
            'acu.CATran': self.acudb.queries.AcuToDbc_CATran,
            'acu.InventorySummary': self.acudb.queries.AcuToDbc_InventorySummary,
            'acu.PhoneRevByMonth': self.acudb.queries.AcuToDbc_PhoneRevByMonth,
            'acu.Quotes': self.acudb.queries.AcuToDbc_Quotes,
            'acu.SalesOrders': self.acudb.queries.AcuToDbc_SalesOrders,
            'acu.Shipments': self.acudb.queries.AcuToDbc_Shipments,
            'acu.Sub': self.acudb.queries.AcuToDbc_Sub,
            'acu.TrialBalance': self.acudb.queries.AcuToDbc_TrialBalance,
        }
