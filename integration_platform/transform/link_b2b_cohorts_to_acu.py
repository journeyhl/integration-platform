from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.link_b2b_cohorts_to_acu import B2BCohortsLinkToAcu
import logging
import polars as pl
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dateutil.relativedelta import relativedelta
import uuid
class Transform:
    def __init__(self, pipeline: B2BCohortsLinkToAcu):
        self.pipeline = pipeline        
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.Transform')

        
    def landing(self, data_extract: pl.SQLContext):
        context_query = data_extract.execute(
        '''
        select *
        from customer_attributes c
        inner join all_customers a on c.CustomerID = a.CustomerID                                              
        ''',
        eager =True
        )
        self.logger.info(f'Combining db_CentralStore and Acumatica extracts (the current values for the Customer Cohort attributes and all B2B customers in acu)')
        list_context_query = context_query.to_dicts()
        exploded_attributes = [
            {
                'CompanyID': 2,
                'CustomerID': row['CustomerID'],
                **entry,
                'RefNoteID': row['NoteID'],
                'PseudonymizationStatus': 0, 'IsActive': 1
            } for row in list_context_query 
            for entry in [
                {
                    'AttributeID': 'COHORT',
                    'Value': row['Cohort'],
                    'NoteID': row['CohortNoteID'],
                },
                {
                    'AttributeID': 'ANCHORDATE',
                    'Value': row['AnchorDate'],
                    'NoteID': row['AnchorDateNoteID']
                },
                {
                    'AttributeID': 'ANCHORTYPE',
                    'Value': row['AnchorType'],
                    'NoteID': row['AnchorTypeNoteID']
                },
                {
                    'AttributeID': 'LASTPRODDT',
                    'Value': row['LastProductDate'],
                    'NoteID': row['LastProductDateNoteID']
                },
                {
                    'AttributeID': 'LASTPADT',
                    'Value': row['LastPADate'],
                    'NoteID': row['LastPADateNoteID']
                },
                {
                    'AttributeID': 'MONTHSPROD',
                    'Value': row['MonthsSinceProduct'],
                    'NoteID': row['MonthsSinceProductNoteID']
                },
                {
                    'AttributeID': 'MONTHSPA',
                    'Value': row['MonthsSincePA'],
                    'NoteID': row['MonthsSincePANoteID']
                }
            ] if entry['Value'] != None
        ]
        self.logger.info(f'Exploded {len(list_context_query)} rows to {len(exploded_attributes)} rows')
        return exploded_attributes