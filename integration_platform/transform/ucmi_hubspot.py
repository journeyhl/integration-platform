from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.ucmi_hubspot import UCMI_HubspotCustomers
import logging
import polars as pl
from datetime import datetime

class Transform:
    def __init__(self, pipeline: UCMI_HubspotCustomers):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.Transform')
        self._set_mappings_()
        pass

    def landing(self, data_extract: pl.DataFrame):
        bp = 'here'
        df1_rename = data_extract.rename({k: v for k, v in self.rename_columns.items() if k in data_extract.columns})
        df2_drop = df1_rename.drop([c for c in self.drop_columns if c in df1_rename.columns])



    def _set_mappings_(self):
        ''':class:`~integration_platform.pipelines.ucmi_hubspot.UCMI_HubspotCustomers`.:class:`~Transform`.:meth:`~_set_mappings_`
        ---
        
        Sets global variable that will be used at transformation
        
        Sets
        ---
        ### :class:`~integration_platform.transform.ucmi_hubspot.Transform`.:attr:`~rename_columns`

        ### :class:`~integration_platform.transform.ucmi_hubspot.Transform`.:attr:`~drop_columns`

        ### :class:`~integration_platform.transform.ucmi_hubspot.Transform`.:attr:`~junk_strings`

        ### :class:`~integration_platform.transform.ucmi_hubspot.Transform`.:attr:`~honorifics`
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.transform.ucmi_hubspot.Transform`.:meth:`~integration_platform.transform.ucmi_hubspot.Transform.__init__`
        
          - At pipeline (and Transform) initialization, set global variables that we will use in dataframe transformation
        '''        
        self.rename_columns = {
            'Record ID - Contact':          'RecordID',
            'First Name':                   'FirstName',
            'Last Name':                    'LastName',
            'Phone Number':                 'PhoneNumber',
            'Contact owner':                'Contactowner',
            'Last Activity Date':           'LastActivityDate',
            'Marketing contact status':     'Marketingcontactstatus',
            'Create Date':                  'CreateDate',
            'Contact URL (HS)':             'HubspotLink',
            'Acumatica Order Number(s)':    'AcumaticaOrderNumbers',
            'Acumatica Product Name':       'AcumaticaProductName',
            'Billing Address':              'BillingAddress',
            'Billing City':                 'BillingCity',
            'Billing State':                'BillingState',
            'Billing Zip':                  'BillingZip',
            'Last Contacted':               'LastContacted',
            'Last Modified Date':           'LastModifiedDate',
            'Lead Source':                  'LeadSource',
            'Shipping Address':             'ShippingAddress',
            'Shipping City':                'ShippingCity',
            'Shipping State':               'ShippingState',
            'Shipping Zip':                 'ShippingZip',
            'Ecommerce contact':            'EcommerceContact',
            'Source store':                 'SourceStore',
            'Record ID - Company':          'CompanyRecordID_drop',
            'Company name':                 'Companyname',
            'Company owner':                'CompanyOwner',
            'Create Date_1':                'CompanyCreateDate',
            'Phone Number_1':               'CompanyPhone',
            'Last Activity Date_1':         'CompanyLastActivityDate',
            'Country/Region':               'Country',
            'Lead Status':                  'LeadStatus',
            'Added To List On':             'AddedToListOn',
            'CreateDate2':                  'CompanyCreateDate',
            'PhoneNumber3':                 'CompanyPhone',
            'LastActivityDate4':            'CompanyLastActivityDate',
            'ContactURL(HS)':               'HubspotLink',
        }
        self.drop_columns =  [
            'AcumaticaProductName',
            'AddedToListOn',
            'AddressLine1',
            'AddressLine2',
            'Address2',
            'City',
            'Industry',
            'CompanyOwner',
            'CompanyRecordID_drop',
            'First Page Seen',
            'First Referring Site',
            'Last Page Seen',
            'Last Referring Site',
            'Latest Traffic Source',
            'Original Source',
            'Original Source Drill-Down 1',
            'Original Source Drill-Down 2',
            'Latest Traffic Source Drill-Down 1',
            'Latest Traffic Source Drill-Down 2',
            'Time of First Session',
            'Time of Last Session',
            'Time Last Seen',
            'Time First Seen',
            'Marketing emails clicked',
            'Marketing email confirmation status',
            'Last marketing email send date',
            'Marketing emails delivered',
            'Marketing emails opened',
            'Marketing emails replied',
        ]

        self.junk_strings = [
            'is not provided',
            'no last name',
            'not explicitly',
            'not mentioned',
            'without any last name',
            'does not',
            'was not',            
        ]
        self.honorifics = {'mr.', 'mrs.', 'ms.', 'miss', 'dr.', 'prof.', 'rev.', 'sr.', 'jr.'}
        