from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pipelines import HubspotCompanyRevenue
import logging
import polars as pl
class Transform:
    def __init__(self, pipeline: HubspotCompanyRevenue):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.transform')
        self.phone_available = []
        self.no_phone = []
        self.email_available = []
        self.email_only = []
        self.no_search = []
        self.prefix = ''
        pass
    
    def transform(self, data_extract: dict):
        hubspot_extract = data_extract['hubspot_extract']
        revenue_extract: pl.DataFrame = data_extract['revenue_extract']
        bp = 'here'
        total = len(hubspot_extract)
        for i, company in enumerate(hubspot_extract):
            self.prefix = f'{i+1}/{total}: {company['name']}'
            company['phone'] = self._parse_phone_or_email(company=company, p_or_e='phone')
            company['email'] = self._parse_phone_or_email(company=company, p_or_e='email')
            if company['phone'] == None and company['email'] == None:
                self.no_search.append(company)
            bp = 'here'
        
        df_hubspot = pl.DataFrame(hubspot_extract, infer_schema_length=None)
        context = pl.SQLContext(
            phone_match = revenue_extract.join(df_hubspot, on='phone', how='inner'),
            phone2_match = revenue_extract.join(df_hubspot, left_on='phone2', right_on='phone', how='inner'),
            email_match = revenue_extract.join(df_hubspot, on='email', how='inner'),
        )
        joined = context.execute(
            query='''
            with unioned as(
select distinct *
from phone_match
union
select distinct *
from phone2_match
union
select distinct *
from email_match) select * from unioned
'''
        )
        joined = joined.collect().to_dicts()
        bp = 'here'
        total = len(joined)
        for i, company in enumerate(joined):
            self.prefix = f'{i+1}/{total}: {company['name']}'
            property_payload = {
                'properties':{
                    'company_revenue': float(company['TotalRevenue']),
                    'total_orders': company['Orders'],
                    'total_units': company['Units'],
                    'revenue_per_order': float(company['RevPerOrder']),
                    'units_per_order': company['UnitsPerOrder'],
                    'acucustomerid': company['CustomerID']
                }
            }
            self.pipeline.hubspot.update_company(company=company, property_payload=property_payload)
            bp = 'here'
        bp = 'here'


    def _parse_phone_or_email(self, company: dict, p_or_e: str):
        self.logger.info(f'{self.prefix}, parsing {p_or_e}')
        if p_or_e == 'phone':
            phone = company[p_or_e].replace('-', ''
                ).replace('(', ''
                ).replace(')', ''
                ).replace(' ', ''
                ).replace('+1', ''
                ).replace('.', ''
                ) if company[p_or_e] != None else None
            if phone == None and company['pc_phone'] != None:
                phone = company[f'pc_{p_or_e}'].replace('-', '').replace('(', '').replace(')', '').replace(' ', '').replace('+1', '') if company[f'pc_{p_or_e}'] != None else None
            if phone == None:
                self.no_phone.append(company)
                return
            self.phone_available.append(company)
            return phone
        elif p_or_e == 'email':
            email = company[p_or_e].strip() if company[p_or_e] != None else None
            if email == None and company['pc_email'] != None: 
                email = company[f'pc_{p_or_e}'].strip() if company[f'pc_{p_or_e}'] != None else None
            if email == None: 
                return
            self.email_available.append(company)
            if company['phone'] == None:
                self.email_only.append(company)
            return email
        



