from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.b2b_cohorts import B2BCohorts
import logging
import polars as pl

class Transform:
    def __init__(self, pipeline: B2BCohorts):
        self.pipeline = pipeline