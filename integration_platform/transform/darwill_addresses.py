from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.darwill_addresses import DarwillAddresses
import logging
import polars as pl
from datetime import datetime
from zoneinfo import ZoneInfo

class Transform:
    def __init__(self, pipeline: DarwillAddresses):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.Transform')
        self.date_added = datetime.now(ZoneInfo('America/New_York')).date()
        pass
    
    def transform(self, data_extract: pl.DataFrame):
        extract_dicts = data_extract.to_dicts()
        data_extract = data_extract.with_columns(
            pl.col('ANI').alias('UnformattedANI'),
            pl.col('product').alias('Product'),
        ).drop('ANI'
        ).with_columns(
            pl.col('ani_normalized').alias('ANI')
        )
        formatted_extract = data_extract.to_dicts()
        for row in formatted_extract:
            row['CustomerID'] = None
            row['HubspotID'] = None
            row['Product'] = row['product']
            row['SourceFile'] = self.pipeline.most_recent_file['name']
            row['DateAdded'] = self.date_added
            row['Email'] = None
            row.pop('product')
        return formatted_extract
    


    def transform_etl_with_csv(self, db_extract: pl.DataFrame, file_extract: pl.DataFrame, source_file: str):
        files = file_extract.to_dicts()
        null_or_bad_tfns = []
        good_tfns = []
        for row in files:
            row['Zip'] = f'0{row['Zip']}' if row['Zip'] != None and len(row['Zip']) < 5 else row['Zip'][:5] if row['Zip'] != None else None
            row['UnformattedANI'] = row['ANI']
            row['HubspotID'] = None
            row['Product'] = None
            row['SourceFile'] = source_file
            row['ContactName'] = None if row['ContactName'] == None else row['ContactName'].replace('  ', ' ').strip()
            row['DateAdded'] = datetime.now(ZoneInfo('America/New_York')).date()
            row['State'] = None if row['State'] == None else row['State'].strip()[:2]
            if row['ANI'] == None:
                null_or_bad_tfns.append(row)
                continue
            row['ANI'] = row['ANI'].replace(' ', '').replace('  ', '').strip()
            if len(row['ANI']) < 10:
                null_or_bad_tfns.append(row)
                continue
            good_tfns.append(row)

        ready = pl.DataFrame(good_tfns)
        not_ready = pl.DataFrame(null_or_bad_tfns)
        bp = 'here'
        bound_tfns = self.find_good_tfn(db_extract=db_extract, not_ready=not_ready)
        return ready.to_dicts(), bound_tfns.to_dicts()


    def find_good_tfn(self, db_extract: pl.DataFrame, not_ready: pl.DataFrame):
        bound_tfns = not_ready.join(db_extract, on='CustomerID', how='inner')
        bound_tfns = bound_tfns.drop('ANI').with_columns(pl.col('Phone').alias('ANI'))
        return bound_tfns



    # def transform_non_nulls(self):
        
        # null_phones = file_extract.sql('select * from self where ANI is null or length(ANI) < 10')