from . import Pipeline
from integration_platform.connectors.sftp import SFTP
from datetime import datetime
from zoneinfo import ZoneInfo


class MFRInsertsExport(Pipeline):
    '''Weekly export of the summarized `analytics.mfr_with_spend` "Inserts" pull.

    Extracts from db_CentralStore, writes the result to a CSV, and uploads it to
    the INC_MEDIA SFTP server. Scheduled Mondays at 10:00 AM Eastern.
    '''

    def __init__(self, function: str):
        super().__init__('mfr-inserts-export', function)

    def extract(self):
        df = self.centralstore.query_to_dataframe(self.centralstore.queries.MFRInsertsExport)
        self.logger.info(f'Extracted {df.height} rows from analytics.mfr_with_spend')
        return df

    def transform(self, data_extract):
        # Result set is exported as-is; no reshaping required.
        return data_extract

    def load(self, data_transformed):
        today = datetime.now(ZoneInfo('America/New_York')).strftime('%Y%m%d')
        remote_path = f'MFR_Inserts_{today}.csv'
        sftp = SFTP(self, server='INC_MEDIA')
        sftp.upload_dataframe_as_csv(data_transformed, remote_path)
        return {'remote_path': remote_path, 'rows': data_transformed.height}

    def log_results(self, data_loaded):
        self.logger.info(
            f"Exported {data_loaded['rows']} rows to {data_loaded['remote_path']} on INC_MEDIA SFTP"
        )
