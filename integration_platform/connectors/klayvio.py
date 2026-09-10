from __future__ import annotations
from typing import TYPE_CHECKING,  Any, Iterator
# if TYPE_CHECKING:
    # from integration_platform.pipelines
import logging


class KlayvioAPI:

    def __init__(self, pipeline) -> None:
        self.pipeline = pipeline
        if type(pipeline) == str:
            self.logger = logging.getLogger(f'{pipeline}.KlayvioAPI')
        else:
            self.logger = logging.getLogger(f'{pipeline.pipeline_name}.KlayvioAPI')

        pass