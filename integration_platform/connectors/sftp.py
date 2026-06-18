import logging
import paramiko
from integration_platform.config.settings import JHL_SFTP, DARWILL_SFTP
import polars as pl
from datetime import datetime, timezone

class SFTP():
    def __init__(self, pipeline, server: str = 'JHL'):
        self.pipeline = pipeline
        if type(pipeline) == str:
            self.logger = logging.getLogger(f'{pipeline}.sftp')
        else:
            self.logger = logging.getLogger(f'{pipeline.pipeline_name}.sftp')
        if server == 'JHL':
            self.host = JHL_SFTP['host']
            self.port = JHL_SFTP['port']
            self.username = JHL_SFTP['username']
            self.password = JHL_SFTP['password']
        elif server == 'Darwill':
            self.host = DARWILL_SFTP['host']
            self.port = DARWILL_SFTP['port']
            self.username = DARWILL_SFTP['username']
            self.password = DARWILL_SFTP['password']
        else:
            self.logger.error(f'Invalid server!')

        self._connect()

        pass



    def _connect(self):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=self.host, port=self.port, username=self.username, password=self.password)
        except Exception as e:
            self.logger.error(f'Error! {e}')
            return
        self.logger.info(f'Connected!')
        self.sftp = ssh.open_sftp()
        bp = 'here'
        


    def list_directory(self, directory: str):
        files = []
        for file in self.sftp.listdir(directory):
            sftp_path = directory + '/' + file
            stats = self.sftp.stat(sftp_path)
            int_dt_added = stats.st_atime if isinstance(stats.st_atime, int) else 0
            dt_added = datetime.fromtimestamp(timestamp=int_dt_added, tz=timezone.utc)
            file = {
                'name': file,
                'path': sftp_path,
                'dt_added': dt_added,
                'stats': stats
            }
            files.append(file)
            bp = 'here'
        return files

    def list_directories(self):
        dirs = self.sftp.listdir('/')
        return dirs

    def get_csv_file_as_dataframe(self, path: str = '/apps/five9/reports/CallSegments3.csv'):
        '''`get_csv_file_as_dataframe`(self, path: *str = '/apps/five9/reports/CallSegments3.csv'*):
        ---
        <hr>
        
        Given a path to a csv file on an SFTP server, open the file and return its contents as a Polars DataFrame
            
        <hr>
        
        Parameters
        ---
        :param (*dict*) `path`: str value with path to csv file. Defaults to Five9's call segments
        
        <hr>
        
        Returns
        ---
        '''
        try:            
            with self.sftp.open(path, 'r') as f:
                file_contents = f.read()
                df_file = pl.read_csv(file_contents)
            self.logger.info(f'Successfully parsed {df_file.height} rows from {path}')
            return df_file
        except Exception as e:
            self.logger.error(f"Error! {e} Couldn't parse {path}")

        bp = 'here'
        # self.sftp.get(path, )