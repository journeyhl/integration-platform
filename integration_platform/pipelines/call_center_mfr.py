from . import Pipeline
from integration_platform.transform.call_center_mfr import Transform
import polars as pl

class CallCenterMFR(Pipeline):
    def __init__(self, function: str):
        super().__init__('mfr', function)
        self.transformer = Transform(self)


    def extract(self):
        inventory_summary_product = self.centralstore.query_to_dataframe(self.centralstore.queries.MFR_InventorySummary_Product)
        phone_rev_staging = self.centralstore.query_to_dataframe(self.centralstore.queries.MFR_PhoneRevStaging)
        adphone_priority_dates = self.centralstore.query_to_dataframe(self.centralstore.queries.MFR_AdPhonePriorityDates)
        adversion_product = self.centralstore.query_to_dataframe(self.centralstore.queries.MFR_AdVersionProduct)
        call_counts = self.centralstore.query_to_dataframe(self.centralstore.queries.MFR_CallCounts)
        
        ad_detail_version = self.centralstore.query_to_dataframe(self.centralstore.queries.MFR_AdDetailAdVersion)
        data_extract = {
            'InventorySummary_Product': inventory_summary_product,
            'PhoneRevPreStaging': phone_rev_staging,
            'AdPhonePriorityDates': adphone_priority_dates,
            'AdVersionProduct': adversion_product,
            'CallCounts': call_counts,
            'AdDetailVersion': ad_detail_version
        }
        return data_extract

    def transform(self, data_extract):
        data_transformed = self.transformer.landing(data_extract)
        return data_transformed
    
    def load(self, data_transformed):
        data_loaded = data_transformed
        return data_loaded
    
    def log_results(self, data_loaded):
        pass