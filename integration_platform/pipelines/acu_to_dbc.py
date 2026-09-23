
from integration_platform.pipelines.base import Pipeline
from datetime import datetime
from zoneinfo import ZoneInfo
import polars as pl
from integration_platform.connectors.sql import SQLConnector, AcumaticaDbQueries
class ModularAcuToDbc(Pipeline):
    def __init__(self, function, table_name: str, env: str = 'prod'):
        super().__init__(pipeline_name='ModularAcuToDbc', function=function, env=env)
        self.acudb: SQLConnector[AcumaticaDbQueries] = SQLConnector(pipeline=self, database_name='AcumaticaDb')
        self.table_name = table_name
        self.query = self._set_mapping_()

    def extract(self) -> pl.DataFrame:
        data_extract = self.acudb.query_to_dataframe(query=self.query)
        return data_extract
    

    def transform(self, data_extract: pl.DataFrame):
        data_transformed = data_extract.to_dicts()
        return data_transformed
    

    def load(self, data_transformed):
        total = len(data_transformed)
        now =  datetime.now(ZoneInfo('America/New_York'))
        data_transformed = self.default_loader.add_to_list(data_transformed, {'InsertedDT': now})
        self.logger.info(f'{total} rows to merge into {self.table_name}')
        self.centralstore.merge_table_paginated(table_name=self.table_name, data=data_transformed, page_size=100)
        bp = 'here'
        return data_transformed


    def log_results(self, data_loaded):
        pass

    def rerun(self, table_name: str):
        self.query = self.map[table_name]
        self.table_name = table_name
        self.run()

    def _set_mapping_(self):
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
        query = self.map[self.table_name]
        return query