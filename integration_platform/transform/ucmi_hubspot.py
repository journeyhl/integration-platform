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
        df3_zips = self._zip_codes_(df=df2_drop)
        df4_strings = self._clean_string_columns_(df=df3_zips)
        df5_names = self._names_(df=df4_strings)
        df6_phones = self._phones_(df=df5_names)
        df7_filtered = self._drop_test_rows_(df=df6_phones)
        bp = 'here'
        test = df7_filtered.to_dicts()
        return df7_filtered


    def _phones_(self, df: pl.DataFrame) -> pl.DataFrame:
        ''':class:`~Transform`.:meth:`~_phones_`
        ---

        Normalizes PhoneNumber to a 10-digit value and adds it as PhoneNumberFmt, leaving the
        original PhoneNumber column untouched

        Parameters
        ---
        :param (*pl.DataFrame*) `df`: dataframe of hubspot customers

        Returns
        ---
        :return `df` (pl.DataFrame): dataframe with PhoneNumberFmt added

        <hr>

        ## Upstream Calls (Methods/Functions Called by)

         ### :class:`~integration_platform.transform.ucmi_hubspot.Transform`.:meth:`~integration_platform.transform.ucmi_hubspot.Transform.landing`
        '''
        if 'PhoneNumber' not in df.columns:
            return df

        #Strip all non-digit characters (including +)
        _digits = pl.col('PhoneNumber').str.strip_chars().str.replace_all(r'[^\d]', '')

        #11-digit number starting with "1" → strip leading country code → 10-digit
        #10-digit number → keep as-is
        #anything else → null
        df = df.with_columns(
            pl.when(
                (_digits.str.len_chars() == 11) &
                _digits.str.starts_with('1')
            )
            .then(_digits.str.slice(1))
            .when(_digits.str.len_chars() == 10)
            .then(_digits)
            .otherwise(None)
            .alias('PhoneNumberFmt')
        )
        return df



    def _zip_codes_(self, df: pl.DataFrame) -> pl.DataFrame:
        ''':class:`~Transform`.:meth:`~_zip_codes_`
        ---
        
        Format shipping and billing zipcodes
        
        Parameters
        ---
        :param (*pl.DataFrame*) `df`: dataframe of hubspot customers
        
        
        Returns
        ---
        :return `df` (pl.DataFrame): dataframe with formatted zipcode data
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.transform.ucmi_hubspot.Transform`.:meth:`~integration_platform.transform.ucmi_hubspot.Transform.landing`
        '''
        if 'BillingZip' in df.columns:
            df = df.with_columns(
                pl.col('BillingZip')
                .cast(pl.Int64, strict=False)
                .cast(pl.Utf8)
                .str.zfill(5)
                .alias('BillingZip')
            )
            df = df.with_columns(
                pl.when(pl.col('BillingZip') == '00000')
                .then(None)
                .otherwise(pl.col('BillingZip'))
                .alias('BillingZip')
            )
        if 'ShippingZip' in df.columns:
            df = df.with_columns(
                pl.col('ShippingZip')
                .str.extract(r'^(\d{5})', 1)
                .str.zfill(5)
                .alias('ShippingZip')
            )
        return df


    def _clean_string_columns_(self, df: pl.DataFrame) -> pl.DataFrame:
        ''':class:`~Transform`.:meth:`~_clean_string_columns_`
        ---

        Strip surrounding whitespace from every string (Utf8) column, then null out any that are left empty

        Parameters
        ---
        :param (*pl.DataFrame*) `df`: dataframe of hubspot customers

        Returns
        ---
        :return `df` (pl.DataFrame): dataframe with all Utf8 columns whitespace-stripped and empty strings nulled

        <hr>

        ## Upstream Calls (Methods/Functions Called by)

         ### :class:`~integration_platform.transform.ucmi_hubspot.Transform`.:meth:`~integration_platform.transform.ucmi_hubspot.Transform.landing`
        '''
        string_cols = [col for col, dtype in zip(df.columns, df.dtypes) if dtype == pl.Utf8]
        df = df.with_columns([
            pl.col(c).str.strip_chars() for c in string_cols
        ])
        df = df.with_columns([
            pl.when(pl.col(c).str.len_chars() == 0).then(None).otherwise(pl.col(c)).alias(c)
            for c in string_cols
        ])
        return df

    def _names_(self, df: pl.DataFrame) -> pl.DataFrame:
        ''':class:`~Transform`.:meth:`~_names_`
        ---

        Clean FirstName/LastName: null placeholders, handle honorifics, split composite names,
        filter AI-generated junk, and build the combined Name column

        Parameters
        ---
        :param (*pl.DataFrame*) `df`: dataframe of hubspot customers

        Returns
        ---
        :return `df` (pl.DataFrame): dataframe with cleaned FirstName/LastName and a combined Name column

        <hr>

        ## Upstream Calls (Methods/Functions Called by)

         ### :class:`~integration_platform.transform.ucmi_hubspot.Transform`.:meth:`~integration_platform.transform.ucmi_hubspot.Transform.landing`
        '''
        if 'FirstName' in df.columns:
            df = self._null_where_(
                df, 'FirstName',
                (pl.col('FirstName').str.len_chars() == 0) |
                pl.col('FirstName').str.contains(r'(?i)^(no|n\/?a|[.\-]+)$'),
                'nulled placeholders (empty/dots/dashes/N/A/No) for'
            )

            _honorific_mask = pl.col('FirstName').str.to_lowercase().is_in(self.honorifics)
            _n = df.filter(_honorific_mask.fill_null(False)).height
            if _n:
                self.logger.info(f'FirstName: moved {_n} honorifics to LastName')
            df = df.with_columns(
                pl.when(_honorific_mask)
                  .then(None)
                  .otherwise(pl.col('FirstName'))
                  .alias('FirstName'),
                pl.when(_honorific_mask)
                  .then(
                      pl.when(pl.col('LastName').is_not_null() & (pl.col('LastName').str.len_chars() > 0))
                        .then(pl.col('FirstName') + ' ' + pl.col('LastName'))
                        .otherwise(pl.col('FirstName'))
                  )
                  .otherwise(pl.col('LastName'))
                  .alias('LastName'),
            )

            _n = df.filter(
                pl.col('FirstName').is_not_null() &
                pl.col('FirstName').str.contains(' ').fill_null(False) &
                (pl.col('LastName').is_null() | (pl.col('LastName').str.len_chars() == 0))
            ).height
            if _n:
                self.logger.info(f'Names: split composite FirstName for {_n} rows')
            df = df.with_columns(
                pl.col('FirstName').str.split(' ').list.get(0).alias('FirstName'),
                pl.when(pl.col('LastName').is_null() | (pl.col('LastName').str.len_chars() == 0))
                  .then(pl.col('FirstName').str.split(' ').list.slice(1).list.join(' ').replace('', None))
                  .otherwise(pl.col('LastName'))
                  .alias('LastName'),
            )

            df = self._strip_caller_(df, 'FirstName')

        if 'LastName' in df.columns:
            df = self._null_where_(
                df, 'LastName',
                (pl.col('LastName').str.len_chars() == 0) |
                pl.col('LastName').str.contains(r'(?i)^(n\/?a|[.\-]+)$'),
                'nulled placeholders (empty/dots/dashes/N/A) for'
            )

            _junk_filter = pl.lit(False)
            for phrase in self.junk_strings:
                _junk_filter = _junk_filter | pl.col('LastName').str.contains(f'(?i){phrase}')
            df = self._null_where_(df, 'LastName', _junk_filter, 'nulled AI-generated junk phrase values for')

            _n = df.filter(
                pl.col('LastName').str.contains(r'(?i)^the last name.*? is ').fill_null(False)
            ).height
            if _n:
                self.logger.info(f'LastName: stripped AI-generated prefix from {_n} rows')
            df = df.with_columns(
                pl.col('LastName')
                  .str.replace(r'(?i)^the last name.*? is ', '')
                  .str.strip_chars()
                  .alias('LastName')
            )

            df = self._strip_caller_(df, 'LastName', extra_chars=r'[*.:_"]')

            _no_name_tokens = ['no', 'name', 'no name']
            _first_placeholder = (
                pl.col('FirstName').is_null() |
                (pl.col('FirstName').str.len_chars() == 0) |
                pl.col('FirstName').str.to_lowercase().is_in(_no_name_tokens)
            )
            _last_placeholder = (
                pl.col('LastName').is_null() |
                (pl.col('LastName').str.len_chars() == 0) |
                pl.col('LastName').str.to_lowercase().is_in(_no_name_tokens)
            )
            _n = df.filter(_first_placeholder & _last_placeholder).height
            if _n:
                self.logger.info(f'Names: nulled {_n} "no name" placeholder pairs')
            df = df.with_columns(
                pl.when(_first_placeholder & _last_placeholder)
                  .then(None)
                  .otherwise(pl.col('FirstName'))
                  .alias('FirstName'),
                pl.when(_first_placeholder & _last_placeholder)
                  .then(None)
                  .otherwise(pl.col('LastName'))
                  .alias('LastName'),
            )

            df = df.with_columns((pl.col('FirstName') + ' ' + pl.col('LastName')).alias('Name'))

        return df


    def _drop_test_rows_(self, df: pl.DataFrame) -> pl.DataFrame:
        ''':class:`~Transform`.:meth:`~_drop_test_rows_`
        ---

        Drops rows where FirstName or LastName contains the word "test", to filter out test/junk customer rows

        Parameters
        ---
        :param (*pl.DataFrame*) `df`: dataframe of hubspot customers

        Returns
        ---
        :return `df` (pl.DataFrame): dataframe with test/junk customer rows dropped

        <hr>

        ## Upstream Calls (Methods/Functions Called by)

         ### :class:`~integration_platform.transform.ucmi_hubspot.Transform`.:meth:`~integration_platform.transform.ucmi_hubspot.Transform.landing`
        '''
        _test_mask = pl.lit(False)
        for _col in ('FirstName', 'LastName'):
            if _col in df.columns:
                _test_mask = _test_mask | pl.col(_col).str.contains(r'(?i)(\btest|test\b)').fill_null(False)
        _n_before = df.height
        df = df.filter(~_test_mask)
        _n = _n_before - df.height
        if _n:
            self.logger.info(f'  Dropped {_n} test/junk customer rows')
        return df


        
    def _null_where_(self, df: pl.DataFrame, col: str, mask: pl.Expr, note: str) -> pl.DataFrame:
        ''':class:`~Transform`.:meth:`~_null_where_`
        ---

        Nulls out values in `col` wherever `mask` is true, logging how many rows were affected

        Parameters
        ---
        :param (*pl.DataFrame*) `df`: dataframe of hubspot customers
        :param (*str*) `col`: column to null values in
        :param (*pl.Expr*) `mask`: boolean expression selecting the rows to null
        :param (*str*) `note`: description of what's being nulled, used in the log message

        Returns
        ---
        :return `df` (pl.DataFrame): dataframe with `col` nulled wherever `mask` is true

        <hr>

        ## Upstream Calls (Methods/Functions Called by)

         ### :class:`~integration_platform.transform.ucmi_hubspot.Transform`.:meth:`~integration_platform.transform.ucmi_hubspot.Transform._names_`
        '''
        _n = df.filter(mask.fill_null(False)).height
        if _n:
            self.logger.info(f'{col}: {note} {_n} rows')
        return df.with_columns(
            pl.when(mask)
              .then(None)
              .otherwise(pl.col(col))
              .alias(col)
        )


    def _strip_caller_(self, df: pl.DataFrame, col: str, extra_chars: str | None = None) -> pl.DataFrame:
        ''':class:`~Transform`.:meth:`~_strip_caller_`
        ---

        Removes the word caller then nulls
        out anything left empty afterward

        Parameters
        ---
        :param (*pl.DataFrame*) `df`: dataframe of hubspot customers
        :param (*str*) `col`: column to clean
        :param (*str*) `extra_chars`: optional regex of extra characters to strip alongside "caller"

        Returns
        ---
        :return `df` (pl.DataFrame): dataframe with `col` cleaned

        <hr>

        ## Upstream Calls (Methods/Functions Called by)

         ### :class:`~integration_platform.transform.ucmi_hubspot.Transform`.:meth:`~integration_platform.transform.ucmi_hubspot.Transform._names_`
        '''
        _n = df.filter(pl.col(col).str.contains(r'(?i)\bcaller\b').fill_null(False)).height
        if _n:
            self.logger.info(f'{col}: removed "caller" from {_n} rows')
        _cleaned = pl.col(col)
        if extra_chars:
            _cleaned = _cleaned.str.replace_all(extra_chars, '')
        _cleaned = _cleaned.str.replace_all(r'(?i)\bcaller\b', '').str.strip_chars()
        df = df.with_columns(_cleaned.alias(col))
        return df.with_columns(
            pl.when(pl.col(col).str.len_chars() == 0)
              .then(None)
              .otherwise(pl.col(col))
              .alias(col)
        )


    def _set_mappings_(self):
        ''':class:`~integration_platform.pipelines.ucmi_hubspot.UCMI_HubspotCustomers`.:class:`~Transform`.:meth:`~_set_mappings_`
        ---
        
        Sets global variables that will be used at transformation
        
        Sets
        ---
        - #### :class:`~integration_platform.transform.ucmi_hubspot.Transform`.:attr:`~rename_columns`: *dict*

        - #### :class:`~integration_platform.transform.ucmi_hubspot.Transform`.:attr:`~drop_columns`: *list*

        - #### :class:`~integration_platform.transform.ucmi_hubspot.Transform`.:attr:`~junk_strings`: *list*

        - #### :class:`~integration_platform.transform.ucmi_hubspot.Transform`.:attr:`~honorifics`: *list*
        
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
            'Date Became the New Lead Status': 'DateBecameTheNewLeadStatus',
            'Date Became the Open Lead Lead Status': 'DateBecameTheOpenLeadLeadStatus',
            'Date Became the Outbound Lead Status': 'DateBecameTheOutboundLeadStatus',
            'Date Became the Reserved Lead Status': 'DateBecameTheReservedLeadStatus',
            'Date Became the Sold Lead Status': 'DateBecameTheSoldLeadStatus',
            'Date Became the Unqualified Lead Status': 'DateBecameTheUnqualifiedLeadStatus',
            'Date Became the DNC Lead Status': 'DateBecameTheDncLeadStatus',
            'Date Became the Lead Exhausted Lead Status': 'DateBecameTheLeadExhaustedLeadStatus',
            'First Conversion': 'FirstConversion',
            'First Conversion Date': 'FirstConversionDate',
            'Recent Conversion Date': 'RecentConversionDate',
            'Recent Conversion': 'RecentConversion',
            'Lead Source Date': 'LeadSourceDate',
            'LinkedIn click id': 'LinkedinClickId',
            'IP State/Region': 'IpState/region',
            'Time in current stage (HH:mm:ss)': 'TimeInCurrentStage',
            'Latest time in "Unqualified Lead (Lifecycle Stage Pipeline)" (HH:mm:ss)': 'LatestTimeInUnqualifiedLead',
            'Latest time in "Subscriber (Lifecycle Stage Pipeline)" (HH:mm:ss)': 'LatestTimeInSubscriber',
            'Latest time in "Opportunity (Lifecycle Stage Pipeline)" (HH:mm:ss)': 'LatestTimeInOpportunity',
            'Latest time in "Lead (Lifecycle Stage Pipeline)" (HH:mm:ss)': 'LatestTimeInLead',
            'Date exited "Unqualified Lead (Lifecycle Stage Pipeline)"': 'DateExitedUnqualifiedLead',
            'Date entered current stage': 'DateEnteredCurrentStage',
            'Date entered "Unqualified Lead (Lifecycle Stage Pipeline)"': 'DateEnteredUnqualifiedLead',
            'Date entered "Subscriber (Lifecycle Stage Pipeline)"': 'DateEnteredSubscriber',
            'Date entered "Marketing Qualified Lead (Lifecycle Stage Pipeline)"': 'DateEnteredMarketingQualifiedLead',
            'Date entered "Lead (Lifecycle Stage Pipeline)"': 'DateEnteredLead',
            'Cumulative time in "Unqualified Lead (Lifecycle Stage Pipeline)" (HH:mm:ss)': 'CumulativeTimeInUnqualifiedLead',
            'Cumulative time in "Subscriber (Lifecycle Stage Pipeline)" (HH:mm:ss)': 'CumulativeTimeInSubscriber',
            'Cumulative time in "Opportunity (Lifecycle Stage Pipeline)" (HH:mm:ss)': 'CumulativeTimeInOpportunity',
            'IpState/region': "IPRegion",
            'kustomer_id': 'KustomerID',
            'kustomer_last_sync': 'KustomerLastSync',
            'kustomer_sync_error': 'KustomerSyncError',
            'kustomer_sync_needed': 'KustomerSyncNeeded',
            'kustomer_sync_status': 'KustomerSyncStatus',
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
            'CompanyPhone',
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
            '--'
        ]
        self.honorifics = {'mr.', 'mrs.', 'ms.', 'miss', 'dr.', 'prof.', 'rev.', 'sr.', 'jr.'}


