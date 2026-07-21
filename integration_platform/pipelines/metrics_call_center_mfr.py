from . import Pipeline
from integration_platform.transform.call_center_mfr import Transform
from integration_platform.load.call_center_mfr import Load
import polars as pl

class CallCenterMetrics(Pipeline):
    def __init__(self, function: str):
        super().__init__('call-center-metrics', function)
        self.transformer = Transform(self)
        self.loader = Load(self)

    def extract(self):
        inventory_summary_product = self.centralstore.query_to_dataframe(self.centralstore.queries.MFR_InventorySummary_Product)
        phone_rev_staging = self.centralstore.query_to_dataframe(self.centralstore.queries.MFR_PhoneRevStaging)
        adphone_priority_dates = self.centralstore.query_to_dataframe(self.centralstore.queries.MFR_AdPhonePriorityDates)
        call_counts = self.centralstore.query_to_dataframe(self.centralstore.queries.MFR_CallCounts)
        call_counts2 = self.centralstore.query_to_dataframe(self.centralstore.queries.MFR_CallCounts)
        call_counts3 = self.centralstore.query_to_dataframe(self.centralstore.queries.MFR_CallCounts)
        call_counts4 = self.centralstore.query_to_dataframe(self.centralstore.queries.MFR_CallCounts)
        call_counts5 = self.centralstore.query_to_dataframe(self.centralstore.queries.MFR_CallCounts)
        call_counts6 = self.centralstore.query_to_dataframe(self.centralstore.queries.MFR_CallCounts)
        call_counts7 = self.centralstore.query_to_dataframe(self.centralstore.queries.MFR_CallCounts)
        
        ad_detail_version = self.centralstore.query_to_dataframe(self.centralstore.queries.MFR_AdDetailAdVersion)
        data_extract = {
            'InventorySummary_Product': inventory_summary_product,
            'PhoneRevPreStaging': phone_rev_staging,
            'AdPhonePriorityDates': adphone_priority_dates,
            'CallCounts': call_counts,
            'AdDetailVersion': ad_detail_version
        }
        return data_extract

    def transform(self, data_extract):
        data_transformed = self.transformer.landing(data_extract)
        return data_transformed
    
    def load(self, data_transformed):
        data_loaded = self.loader.landing_loader(data_transformed=data_transformed)
        return data_loaded
    
    def log_results(self, data_loaded):
        pass