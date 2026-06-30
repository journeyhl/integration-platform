import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines import CallCenterMFR
import polars as pl


def list_columns(name: str, df: pl.DataFrame):
    print(f'{name}\n---------')
    print(', '.join(df.columns))
    bp = 'here'







mfr = CallCenterMFR('.debug')
data_extract = mfr.extract()
data_transformed = mfr.transform(data_extract=data_extract)
transformed_dicts = {}
for key, dataframe in data_transformed.items():
    transformed_dicts[key] = dataframe.to_dicts()


tables = pl.SQLContext(
    InventorySummary_Product = data_transformed['InventorySummary_Product'],
    PhoneRevPreStaging = data_transformed['PhoneRevPreStaging'],
    AdPhonePriorityDates = data_transformed['AdPhonePriorityDates'],
    AdVersionProduct = data_transformed['AdVersionProduct'],
    CallCounts = data_transformed['CallCounts'],
    AdDetailVersion = data_transformed['AdDetailVersion'],
    aggregate_call_counts = data_transformed['aggregate_call_counts'],
    phone_revenue_staging = data_transformed['phone_revenue_staging'],
    lineamt_calc = data_transformed['lineamt_calc'],
    phone_revenue = data_transformed['phone_revenue'],
    inter_mfr_matched = data_transformed['inter_mfr_matched'],
    inter_mfr_rownum = data_transformed['inter_mfr_rownum'],
    inter_mfr_allocated = data_transformed['inter_mfr_allocated'],
    acu_mfr_allocated = data_transformed['acu_mfr_allocated'],
    mfr_allocated = data_transformed['mfr_allocated'],
)




# list_columns(name='inter_mfr_allocated', df=data_transformed['inter_mfr_allocated'])

bp = 'here'

inter_mfr_allocated = data_transformed['inter_mfr_allocated']

inter_mfr_allocated.sort(['OrderNbr'])
d_inter_mfr_allocated = inter_mfr_allocated.to_dicts()
bp = 'here'