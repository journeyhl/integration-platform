from integration_platform.pipelines import Pipeline
from integration_platform.connectors import HubSpotAPI
from integration_platform.transform.hubspot_company_revenue import Transform
import json


class HubspotCompanyRevenue(Pipeline):
    def __init__(self, function: str, env: str='prod'):
        # function = 'consignment_reclassifications'
        super().__init__(pipeline_name='hubspot-company-revenue', function=function, env=env)
        self.hubspot = HubSpotAPI(self)
        self.transformer = Transform(self)

    def extract(self):
        hubspot_extract = self.hubspot.retrieve_companies(limit=100)        
        data_extract = {
            'hubspot_extract': hubspot_extract,
            'revenue_extract': self.centralstore.query_to_dataframe(self.centralstore.queries.HubSpot_RevenueByCustomer).to_dicts()
        }
        return data_extract

    def transform(self, data_extract):
        data_transformed = self.transformer.transform(data_extract)
        return data_transformed
    
    def load(self, data_transformed):
        self.centralstore.engine = self.centralstore._create_engine()
        self.centralstore.raw_connection = self.centralstore.engine.raw_connection()
        acu_companies = data_transformed['acu_companies']
        unmatched_companies = data_transformed['unmatched_companies']
        self.centralstore.checked_upsert_paginated('hs.AcuCompanies', acu_companies)
        self.centralstore.checked_upsert_paginated('hs.UnmatchedCompanies', unmatched_companies)
        data_loaded = data_transformed
        return data_loaded
    
    def log_results(self, data_loaded):
        pass