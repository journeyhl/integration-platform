import logging


class RyderAPI:
    def __init__(self, pipeline):
        self.pipeline = pipeline
        if type(pipeline) == str:
            self.logger = logging.getLogger(f'{pipeline}.RyderAPI')
        else:
            self.logger = logging.getLogger(f'{pipeline.pipeline_name}.RyderAPI')
        pass