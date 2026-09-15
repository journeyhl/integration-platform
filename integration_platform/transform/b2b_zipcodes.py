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
        extract_cast = self._cast_dtypes_(data_extract=extract_renamed)
        # self.pipeline.default_loader.add_to_list()
        return extract_cast



    def _rename_(self, data_extract: pl.DataFrame):
        extract_renamed = data_extract.rename({k: v for k, v in self.rename_columns.items() if k in data_extract.columns})
        bp = 'here'
        return extract_renamed

    def _cast_dtypes_(self, data_extract: pl.DataFrame):
        '''Align dataframe dtypes with `_dev.B2BZipCodes` column types.

        Population/Density/CountyFIPS come off the extract as strings/ints that don't
        match the int/decimal(18,1)/varchar(6) columns, and LastChecked carries a
        tz-aware datetime that SQL's plain `datetime` column can't hold.
        '''
        extract_cast = data_extract.with_columns(
            pl.col('Population').cast(pl.Int64),
            pl.col('Density').cast(pl.Float64),
            pl.col('CountyFIPS').cast(pl.String),
            pl.col('LastChecked').dt.replace_time_zone(None),
        )
        return extract_cast