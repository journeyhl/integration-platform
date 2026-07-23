
from integration_platform.pipelines.base import Pipeline
from integration_platform.transform.cron_calendar import Transform
from pathlib import Path

class CronCalendar(Pipeline):
    def __init__(self, function: str):
        super().__init__('cron-calendar', function)
        self.transformer = Transform(self)


    def extract(self):
        dir_path = Path(__file__).parent.parent.parent
        with open(str(dir_path / 'function_app.py'), 'r') as r:
            function_app = r.read()
        data_extract = function_app
        return data_extract

    def transform(self, data_extract):
        data_transformed = self.transformer.lander(data_extract)
        return data_transformed
    
    def load(self, data_transformed):
        data_loaded = data_transformed
        self.centralstore.raw_execute(f'delete from _util.Schedule')
        self.centralstore.insert_df(df_data_loaded=data_transformed, table_name='_util.Schedule')
        return data_loaded
    
    def log_results(self, data_loaded):
        pass