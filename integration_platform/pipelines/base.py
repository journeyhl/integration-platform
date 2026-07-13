from abc import ABC, abstractmethod
from datetime import datetime
from zoneinfo import ZoneInfo
import logging
import polars as pl
from integration_platform.connectors.sql import SQLConnector, CentralStoreQueries, AcumaticaDbQueries
import colorlog
from typing import TypeVar, Generic, Any

T = TypeVar('T', list, dict)

class MillisecondFormatter(colorlog.ColoredFormatter):
    def formatTime(self, record, datefmt = None):
        time = datetime.fromtimestamp(record.created)
        if datefmt:
            new_time = time.strftime(datefmt)[:-3]
            return new_time
        return time.isoformat()

class LogHistory(logging.Handler):
    def __init__(self, logs: list, pipe_start: datetime, function: str):
        super().__init__()
        self.logs = logs
        self.pipe_start = pipe_start
        self.function = function
    
    def emit(self, log_entry):
        self.logs.append(self.format(log_entry))

    def format(self, log_entry):
        log_id = len(self.logs) + 1
        time = datetime.fromtimestamp(log_entry.created, ZoneInfo('America/New_York'))
        pipeline = log_entry.name if '.' not in log_entry.name else log_entry.name.split('.')[0]
        new_log_entry = {
            'AzureFunction': self.function,
            'Pipeline': pipeline,
            'LogID': log_id,
            'PipeLogName': log_entry.name,
            'FileName': log_entry.filename,
            'Method': log_entry.funcName,
            'LineNbr': log_entry.lineno,
            'PLevel': log_entry.levelno,
            'Msg': log_entry.msg,
            'Priority': log_entry.levelname,
            'Module': log_entry.module,
            'Timestamp': datetime.now(ZoneInfo('America/New_York')),
            'PipeStartTimestamp': self.pipe_start
        }
        return new_log_entry

class Pipeline(ABC):
    def __init__(self, pipeline_name: str, function: str, env: str = 'prod'):
        '''`init`(self, pipeline_name: *str*)
        ---
        <hr>
        
        Pipeline superclass initialization
            
        <hr>
        
        Parameters
        ---
        :param (*str*) `pipeline_name`: Name of Pipeline, passed from subclass
        :param (*str*) `function`: Name of function in Azure Functions, passed from subclass
        :param (*str*) `env = 'prod'` `env`: Whether or not pipeline is to be run in 'prod' (AcumaticaDb) or 'dev' (AcudevDb)
        
        <hr>
        
        Sets
        ---
        >>> self.pipeline_name = pipeline_name
        >>> self.centralstore =SQLConnector[CentralStoreQueries] = SQLConnector(self, 'db_CentralStore')
        >>> self.acudb = SQLConnector[AcumaticaDbQueries] = SQLConnector(self, 'AcumaticaDb')
        >>> if env == 'dev':
        >>>     self.acudb: SQLConnector[AcumaticaDbQueries] = SQLConnector(self, 'AcudevDb')
        >>> self.logger = logging.getLogger(pipeline_name)
        '''
        self.pipeline_name = pipeline_name
        self.function = function
        self.centralstore: SQLConnector[CentralStoreQueries] = SQLConnector(self, 'db_CentralStore')
        self.acudb: SQLConnector[AcumaticaDbQueries] = SQLConnector(self, 'AcumaticaDb')
        if env == 'dev':
            self.acudb: SQLConnector[AcumaticaDbQueries] = SQLConnector(self, 'AcudevDb')
        self.logger = logging.getLogger(pipeline_name)
        self.logs = []
        self.ts_pipeline_start = datetime.now(ZoneInfo('America/New_York'))
        self.logger.addHandler(LogHistory(self.logs, self.ts_pipeline_start, self.function))        
        if not logging.root.handlers:
            handler = colorlog.StreamHandler()
            handler.setFormatter(MillisecondFormatter(
                fmt='%(log_color)s%(asctime)s:  %(name)s ╍ %(levelname)s ╍ %(message)s',
                datefmt='%m/%d/%Y %H:%M:%S.%f',
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'white',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'bold_red'
                }
            ))
            logging.root.setLevel(logging.INFO)
            logging.root.addHandler(handler)


    @abstractmethod
    def extract(self, *args, **kwargs) -> Any: ...

    @abstractmethod
    def transform(self, data_extract) -> Any: ...

    @abstractmethod
    def load(self, data_transformed) -> Any: ...

    @abstractmethod
    def log_results(self, data_loaded) -> Any: ...
        


    def run(self):
        self.ts_pipeline_start = datetime.now(ZoneInfo('America/New_York'))
        self.logger.info(f'Starting {self.pipeline_name}')


        self.logger.info('Extracting...')
        data_extract = self.extract()

        ts_extract_complete = datetime.now(ZoneInfo('America/New_York'))
        self.extract_dur = self._time_differential_(start=self.ts_pipeline_start, end=ts_extract_complete)
        self.logger.info(f'Extract complete in {self.extract_dur['dur_string']}!')


        self.logger.info('Transforming...')
        data_transformed = self.transform(data_extract=data_extract)
        ts_transform_complete = datetime.now(ZoneInfo('America/New_York'))
        self.transform_dur = self._time_differential_(start=ts_extract_complete, end=ts_transform_complete)
        self.logger.info(f'Transform complete in {self.transform_dur['dur_string']}!')


        self.logger.info('Loading...')
        data_loaded = self.load(data_transformed=data_transformed)
        ts_load_complete = datetime.now(ZoneInfo('America/New_York'))
        self.load_dur = self._time_differential_(start=ts_transform_complete, end=ts_load_complete)
        self.logger.info(f'Load complete in {self.load_dur['dur_string']}!')

        self.logger.info('Logging...')
        self.log_results(data_loaded=data_loaded)
        try:
            self.centralstore.insert_df(df_data_loaded=pl.DataFrame(self.logs), table_name='_util.Logs')
        except Exception as e:
            self.logger.warning(f"{e}: Couldn't insert logs to SQL but pipeline execution was successful")
        
        pipe_complete = datetime.now(ZoneInfo('America/New_York'))
        self.pipe_dur = self._time_differential_(start=self.ts_pipeline_start, end=pipe_complete)
        self.logger.info(f'Pipeline complete in {self.pipe_dur['dur_string']}!')

        return{
            'pipeline': self.pipeline_name,
            'status': 'success',
            'extracted': data_extract,
            'transformed': data_transformed,
            'loaded': data_loaded
        }



    def _time_differential_(self, start: datetime, end: datetime):
        total_seconds = (end - start).seconds
        minutes = int(total_seconds / 60)
        seconds = int(total_seconds % 60)
        elapsed = f'{minutes}m {seconds}s'
        duration = {
            'started': start,
            'completed': end,
            'total_seconds': total_seconds,
            'minutes': minutes,
            'seconds': seconds,
            'dur_string': elapsed
        }
        return duration