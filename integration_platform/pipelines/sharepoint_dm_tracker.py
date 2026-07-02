from io import BytesIO
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd

from integration_platform.pipelines.base import Pipeline
from integration_platform.connectors import Sharepoint


def _classify_product(campaign: str) -> str:
    c = str(campaign).upper()
    if 'AIR' in c:
        return 'Air'
    if 'PSC' in c:
        return 'PSC'
    if 'SO LITE' in c or 'SOLITE' in c:
        return 'So Lite Scooter'
    if 'ZOOMER' in c:
        return 'Zoomer'
    if 'UPBED' in c:
        return 'Upbed'
    if 'UPWALKER' in c:
        return 'Upwalker'
    return 'Generic-Brand Page'


class SharepointDmTracker(Pipeline):
    def __init__(self, function: str):
        super().__init__('sharepoint_dm_tracker', function)
        self.sharepoint = Sharepoint(self)

    def extract(self) -> bytes:
        self.logger.info('Fetching Ad Plan 2026.xlsx from SharePoint')
        return self.sharepoint.get_file('Shared Documents/Ad PLanning/Ad Plan 2026.xlsx')

    def transform(self, file_bytes: bytes) -> list[dict]:
        df = pd.read_excel(BytesIO(file_bytes), sheet_name='DMTracker ', header=1)
        df = df.iloc[44:].reset_index(drop=True)
        df = df[
            df['Mail Name'].notna() &
            df['Campaign'].notna() &
            df['TFN'].notna()
        ].copy()

        df['SpendMonth'] = (
            pd.to_datetime(df['Month'].astype(str) + ' 1 2026', format='%b %d %Y', errors='coerce')
            + pd.offsets.MonthEnd(0)
        )
        df = df[df['SpendMonth'].notna()].copy()

        grouped = (
            df.groupby(['SpendMonth', 'In-Home Start Date', 'Mail Name', 'Campaign', 'TFN'])
            .agg(TotalSpend=('Print Totals', 'sum'))
            .reset_index()
        )

        grouped['ProductGroup'] = grouped['Campaign'].apply(_classify_product)
        grouped['LoadTimestamp'] = datetime.now(ZoneInfo('America/New_York'))
        grouped = grouped.rename(columns={
            'In-Home Start Date': 'InHomeStartDate',
            'Mail Name': 'MailName',
        })

        cols = ['SpendMonth', 'InHomeStartDate', 'MailName', 'Campaign', 'TFN',
                'TotalSpend', 'ProductGroup', 'LoadTimestamp']
        records = grouped[cols].to_dict('records')
        for row in records:
            if pd.isnull(row['InHomeStartDate']):
                row['InHomeStartDate'] = None
        return records

    def load(self, data_transformed: list[dict]) -> int:
        self.centralstore.checked_upsert(table_name='src_dm_tracker', data=data_transformed)
        return len(data_transformed)

    def log_results(self, data_loaded: int) -> None:
        self.logger.info(f'Loaded {data_loaded} rows to dbo.src_dm_tracker')