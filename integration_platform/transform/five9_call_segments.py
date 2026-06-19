from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines import Five9CallSegments
import logging
import polars as pl

class Transform:
    def __init__(self, pipeline: Five9CallSegments):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.transform')
        pass
    
    def transform(self, data_extract: dict[str, pl.DataFrame]):
        five9_extract = data_extract['five9_extract']
        db_extract = data_extract['db_extract']
        formatted = five9_extract.with_columns(
            pl.col('CALL ID').cast(pl.String).alias('CallID'),
            pl.col('TIMESTAMP').str.to_datetime('%a, %d %b %Y %H:%M:%S').alias('Timestamp'),
            pl.col('CALL TYPE').alias('CallType'),
            pl.col('SESSION ID').alias('SessionID'),
            pl.col('CALL SEGMENT ID').cast(pl.String).alias('CallSegmentID'),
            pl.col('CALLED PARTY').alias('CalledParty'),
            pl.col('CALLING PARTY').alias('CallingParty'),
            pl.col('SEGMENT TYPE').alias('SegmentType'),
            pl.col('RESULT').alias('Result'),
            pl.col('AFTER CALL WORK TIME').alias('AfterCallWorkDuration'),
            pl.col('TALK TIME').alias('TalkDuration'),
            pl.col('HANDLE TIME').alias('HandleDuration'),
            pl.col('CALL TIME').alias('CallDuration'),
            pl.col('ANI').cast(pl.String).alias('ANI'),
            pl.col('SKILL').alias('Skill'),
            pl.col('DNIS').cast(pl.String).alias('DNIS'),
            pl.col('SPEED OF ANSWER').alias('AnswerSpeed'),
            pl.col('RING TIME').alias('RingDuration'),
            pl.col('IVR TIME').alias('IVRDuration'),
            pl.col('QUEUE WAIT TIME').alias('QueueWaitDuration'),
            pl.col('TOTAL QUEUE TIME').alias('TotalQueueDuration'),
            pl.col('SEGMENT TIME').alias('SegmentDuration'),
            pl.col('TIMESTAMP').cast(pl.String).alias('TimestampKey')
        ).drop([
            'CALL ID',
            'TIMESTAMP',
            'CALL TYPE',
            'SESSION ID',
            'CALL SEGMENT ID',
            'CALLED PARTY',
            'CALLING PARTY',
            'SEGMENT TYPE',
            'RESULT',
            'AFTER CALL WORK TIME',
            'TALK TIME',
            'HANDLE TIME',
            'CALL TIME',
            'SKILL',
            'SPEED OF ANSWER',
            'RING TIME',
            'IVR TIME',
            'QUEUE WAIT TIME',
            'TOTAL QUEUE TIME',
            'SEGMENT TIME'
        ])
        
        five9_transformed = formatted.to_dicts()
        return five9_transformed


    def filter(self, five9_transformed: list[dict], db_extract: list[dict]):
        bp = 'here'



















