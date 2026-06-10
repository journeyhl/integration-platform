import logging
import paramiko
from config.settings import JHL_SFTP
import polars as pl

class SFTP():
    def __init__(self, pipeline):
        self.pipeline = pipeline
        if type(pipeline) == str:
            self.logger = logging.getLogger(f'{pipeline}.sftp')
        else:
            self.logger = logging.getLogger(f'{pipeline.pipeline_name}.sftp')
        self.host = JHL_SFTP['host']
        self.port = JHL_SFTP['port']
        self.username = JHL_SFTP['username']
        self.password = JHL_SFTP['password']
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
            files.append(file)
            bp = 'here'

    
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