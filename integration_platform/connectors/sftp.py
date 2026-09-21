import io
import logging
import paramiko
from integration_platform.config.settings import JHL_SFTP, DARWILL_SFTP, INC_MEDIA_SFTP
import polars as pl
from datetime import datetime, timezone
from typing import Literal

class SFTP():
    def __init__(self, pipeline, server: str = 'JHL'):
        self.pipeline = pipeline
        if type(pipeline) == str:
            self.logger = logging.getLogger(f'{pipeline}.SFTP')
        else:
            self.logger = logging.getLogger(f'{pipeline.pipeline_name}.SFTP')
        self._set_server_config_(server=server)
        self._connect_()

        pass


    def _set_server_config_(self, server: str):
        ''':class:`~integration_platform.connectors.sftp.SFTP`.:meth:`~integration_platform.connectors.sftp.SFTP._set_server_config_`
        ---
        
        Given the server name to connect to, resolve mapping for connection details found in .env file and set class level connection variables
        
        Parameters
        ---
        :param (*str*) `server`: string for server, mapping currently setup for 'JHL', 'Darwill', or 'INC_MEDIA' values

        <hr>
        
        Sets
        ---
        - ### self.:attr:`~integration_platform.connectors.sftp.SFTP.host`, self.:attr:`~integration_platform.connectors.sftp.SFTP.port`, self.:attr:`~integration_platform.connectors.sftp.SFTP.username`, self.:attr:`~integration_platform.connectors.sftp.SFTP.password`
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.connectors.sftp.SFTP`.:meth:`~integration_platform.connectors.sftp.SFTP.__init__`
        
          - Called upon connector's initialization
        '''        
        try:
            mapping = {
                'JHL': JHL_SFTP,
                'Darwill': DARWILL_SFTP,
                'INC_MEDIA': INC_MEDIA_SFTP
            }
            self.host = mapping[server]['host']
            self.port = mapping[server]['port']
            self.username = mapping[server]['username']
            self.password = mapping[server]['password']
        except:
            self.logger.error(f'Invalid server!')

    #MARK: _connect_
    def _connect_(self):
        ''':class:`~integration_platform.connectors.sftp.SFTP`.:meth:`~integration_platform.connectors.sftp.SFTP._connect_`
        ---
        
        Using self.:attr:`~integration_platform.connectors.sftp.SFTP.host`, self.:attr:`~integration_platform.connectors.sftp.SFTP.port`, self.:attr:`~integration_platform.connectors.sftp.SFTP.username` and self.:attr:`~integration_platform.connectors.sftp.SFTP.password`, connect to a given SFTP server

        <hr>

        Sets
        ---
        - #### self.:attr:`~integration_platform.connectors.sftp.SFTP.sftp`

        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.connectors.sftp.SFTP`.:meth:`~integration_platform.connectors.sftp.SFTP.__init__`
        
          - Called upon connector's initialization
        '''        
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
        

    #MARK: list_directory
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

    #MARK: list_directories
    def list_directories(self):
        dirs = self.sftp.listdir('/')
        return dirs


    
    #MARK: get_file_as_dataframe
    def get_file_as_dataframe(self, type: Literal['csv', 'xlsx'], path: str = '/apps/five9/reports/CallSegments3.csv') -> pl.DataFrame:
        ''':class:`~integration_platform.connectors.sftp.SFTP`.:meth:`~integration_platform.connectors.sftp.SFTP.get_file_as_dataframe`
        ---
        
        Given a path to a csv or xlsx file on an SFTP server, open the file and return its contents as a Polars DataFrame
        
        Parameters
        ---
        :param (**Literal***['csv', 'xlsx']*) `type`: The filetype of the file found at *path*, must be csv or xlsx
        
                
           ### ***Optional***
        :param (*str = '/apps/five9/reports/CallSegments3.csv'*) `path`: Path that the file is found at, defaults to `/apps/five9/reports/CallSegments3.csv`
        
        Returns
        ---
        :return `df_file` (pl.DataFrame): dataframe of the file contents found at the passed path
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.pipelines.ucmi_hubspot.UCMI_HubspotCustomers`.:meth:`~integration_platform.pipelines.ucmi_hubspot.UCMI_HubspotCustomers.extract`
        
         ### :class:`~integration_platform.pipelines.five9_call_segments.Five9CallSegments`.:meth:`~integration_platform.pipelines.five9_call_segments.Five9CallSegments.extract`
           
         ### :class:`~integration_platform.pipelines.darwill_addresses.DarwillAddresses`.:meth:`~integration_platform.pipelines.darwill_addresses.DarwillAddresses.extract`
        '''
        try:            
            with self.sftp.open(path, 'r') as f:
                file_contents = f.read()
                df_file = pl.read_csv(file_contents, infer_schema_length=0) if type == 'csv' else pl.read_excel(file_contents, infer_schema_length=0)
            self.logger.info(f'Successfully parsed {df_file.height} rows from {path}')
            return df_file
        except Exception as e:
            self.logger.error(f"Error! {e} Couldn't parse {path}")
            return pl.DataFrame()


    #MARK: upload_dataframe_as_csv
    def upload_dataframe_as_csv(self, df: pl.DataFrame, remote_path: str):
        '''`:class:`~integration_platform.connectors.sftp.SFTP`.:meth:`~integration_platform.connectors.sftp.SFTP.upload_dataframe_as_csv`
        ---

        Serialize a Polars DataFrame to CSV and upload it to the connected SFTP
        server at `remote_path`.

        Parameters
        ---
        :param (*pl.DataFrame*) `df`: DataFrame to write out as CSV
        :param (*str*) `remote_path`: Destination path (or filename, relative to
            the account's landing directory) on the SFTP server

        <hr>

        Returns
        ---
        The `remote_path` the file was written to.
        '''
        try:
            buffer = io.BytesIO(df.write_csv().encode('utf-8'))
            self.sftp.putfo(buffer, remote_path)
            self.logger.info(f'Uploaded {df.height} rows to {remote_path}')
            return remote_path
        except Exception as e:
            self.logger.error(f"Error! {e} Couldn't upload to {remote_path}")
            raise


#region Archived methods
#
#
#
#
    #MARK: get_csv_file_as_dataframe
    def get_csv_file_as_dataframe(self, type: str = 'csv', path: str = '/apps/five9/reports/CallSegments3.csv') -> pl.DataFrame:
        ''':class:`~integration_platform.connectors.sftp.SFTP`.:meth:`~integration_platform.connectors.sftp.SFTP.get_csv_file_as_dataframe`
        ---
        
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
                df_file = pl.read_csv(file_contents, infer_schema_length=0)
            self.logger.info(f'Successfully parsed {df_file.height} rows from {path}')
            return df_file
        except Exception as e:
            self.logger.error(f"Error! {e} Couldn't parse {path}")
            return pl.DataFrame()

#endregion