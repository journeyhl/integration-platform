from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.b2b_zipcodes import B2BZipCodes
import logging
import polars as pl
from datetime import datetime

class Transform:
    def __init__(self, pipeline: B2BZipCodes):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.Transform')        
        self.rename_columns = {
            'State_Id': 'StateID',
            'State_Name': 'State',
            'County_Fips': 'CountyFIPS',
            'County_Name': 'CountyName',
            'County_Weights': 'CountyWeights' ,
            'County_Names_All': 'AllCountyNames',
            'County_Fips_All': 'AllCountyFIPS'

        }
        pass

    def landing(self, data_extract: pl.DataFrame):
        extract_renamed = self._rename_(data_extract=data_extract)
        # self.pipeline.default_loader.add_to_list()
        bp = 'here'



    def _rename_(self, data_extract: pl.DataFrame):
        extract_renamed = data_extract.rename({k: v for k, v in self.rename_columns.items() if k in data_extract.columns})
        bp = 'here'
        return extract_renamed