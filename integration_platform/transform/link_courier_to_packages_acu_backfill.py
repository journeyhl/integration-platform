from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.link_courier_to_packages_acu_backfill import CourierPackage_Backfill
import logging
import polars as pl
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dateutil.relativedelta import relativedelta
import uuid
class Transform:
    def __init__(self, pipeline: CourierPackage_Backfill):
        self.pipeline = pipeline        
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.Transform')

        
    def landing(self, data_extract: dict[str, pl.DataFrame]):
        dbc = self.explode_dbc(dbc=data_extract['dbc'])
        df_dbc = pl.DataFrame(data=dbc)
        data_transformed = self.join(acu=data_extract['acu'], dbc=df_dbc)
        return data_transformed


    def join(self, acu: pl.DataFrame, dbc: pl.DataFrame):
        ''':class:`~integration_platform.pipelines.link_courier_to_packages_acu_backfill.CourierPackage_Backfill`.:class:`~integration_platform.transform.link_courier_to_packages_acu_backfill.Transform`.:meth:`~integration_platform.transform.link_courier_to_packages_acu_backfill.Transform.join`
        ---
        
        Join dbc and acu extracts together on ShipmentNbr and TrackingNbr
        
        Parameters
        ---
        :param (*pl.DataFrame*) `acu`: Shipment/Tracking extract from AcumaticaDb
        :param (*pl.DataFrame*) `dbc`: Shipment/Tracking extract from db_CentralStore
        
        Returns
        ---
        :return `data_transformed` (list[dict]): joined list of dicts of distinct shipment/tracking numbers
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.pipelines.link_courier_to_packages_acu_backfill.CourierPackage_Backfill`.:class:`~integration_platform.transform.link_courier_to_packages_acu_backfill.Transform`.:meth:`~integration_platform.transform.link_courier_to_packages_acu_backfill.Transform.landing`
        '''        
        joined = acu.join(other=dbc, left_on=['ShipmentNbr', 'TrackNumber'], right_on=['ShipmentNbr_3pl', 'TrackingNumbers'], how='inner')
        data_transformed = joined.to_dicts()
        return data_transformed


    def explode_dbc(self, dbc: pl.DataFrame) -> list[dict]:
        ''':class:`~integration_platform.pipelines.link_courier_to_packages_acu_backfill.CourierPackage_Backfill`.:class:`~integration_platform.transform.link_courier_to_packages_acu_backfill.Transform`.:meth:`~integration_platform.transform.link_courier_to_packages_acu_backfill.Transform.explode_dbc`
        ---
        
        Given the RedStag events extract from db_CentralStore (dbc), format tracking numbers & explode rows with more than one track number
        
        Parameters
        ---
        :param (*pl.DataFrame*) `dbc`: RedStag events from db_CentralStore
        
        Returns
        ---
        :return `exploded` (list[dict]): list of tracking data, each distinct shipment nbr and tracking having it's own row
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.pipelines.link_courier_to_packages_acu_backfill.CourierPackage_Backfill`.:class:`~integration_platform.transform.link_courier_to_packages_acu_backfill.Transform`.:meth:`~integration_platform.transform.link_courier_to_packages_acu_backfill.Transform.landing`
        '''        
        dbc_dicts = dbc.to_dicts()
        exploded = []
        for row in dbc_dicts:
            ship_nbr = row[f'ShipmentNbr_3pl']
            courier = row['Courier']
            tracks = row['TrackingNumbers'].replace('[', '').replace(']', '').replace('"', '')
            if ',' in row['TrackingNumbers']:
                multiple_tracks = tracks.split(',')
                mult = [{'ShipmentNbr_3pl': ship_nbr, 'ContentTypeDesc': courier, 'TrackingNumbers': track} for track in multiple_tracks]
                exploded.extend([{'ShipmentNbr_3pl': ship_nbr, 'ContentTypeDesc': courier, 'TrackingNumbers': track} for track in multiple_tracks])
                bp = 'here'
            else:
                exploded.append({
                    'ShipmentNbr_3pl': ship_nbr,
                    'ContentTypeDesc': courier,
                    'TrackingNumbers': tracks
                })

        bp = 'here'
        return exploded

