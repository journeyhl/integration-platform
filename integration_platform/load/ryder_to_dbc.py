from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.ryder_to_dbc import RyderToDbc

import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Any
import polars as pl
class Load:
    def __init__(self, pipeline: RyderToDbc):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.Load')
        pass



    def landing_format_for_sql(self, data_transformed: dict):
        orders = [v for v in data_transformed.values()]
        bp = 'here'
        total = len(orders)
        sql_orders = []
        sql_order_events = []
        sql_shipment_items = []
        sql_shipment_events = []
        for i, order in enumerate(orders):
            sql_order = self.format_order_for_sql(order)
            sql_orders.append(sql_order)
            sql_order_events.extend([{**event, 'TrackingNbr': order['parsed_order_info']['TrackingNbr'], 'LastChecked': order['extract_time']} for event in order['parsed_order_info']['Events']])
            sql_shipment_events.extend([{**event, 'LastChecked': order['extract_time']} for s in order['parsed_shipment_info'] for event in s['ship_events']])
            sql_shipment_items.extend([{**item, 'LastChecked': order['extract_time']} for s in order['parsed_shipment_info'] for item in s['ship_items']])
            bp = 'here'

        data_to_load = {
            'ryder.Orders': self.pipeline.default_loader.add_InsertedDT_to_list(sql_orders),
            'ryder.OrderEvents': self.pipeline.default_loader.add_InsertedDT_to_list(sql_order_events),
            'ryder.ShipmentEvents': self.pipeline.default_loader.add_InsertedDT_to_list(sql_shipment_events),
            'ryder.ShipmentItems': self.pipeline.default_loader.add_InsertedDT_to_list(sql_shipment_items)
        }
        
        return data_to_load



    def format_order_for_sql(self, order: dict):
        rlm_order = {
            'RLM_OrderNumber': order['parsed_order_info']['RLM_OrderNumber'],
            'TrackingNbr': order['parsed_order_info']['TrackingNbr'],
            'ShipmentNbr': order['parsed_order_info']['ShipmentNbr'],
            'RyderID': order['parsed_order_info']['RyderID'],
            'OrderType': order['parsed_order_info']['OrderType'],
            'OrderNbr': order['parsed_order_info']['OrderNbr'],
            'CurrentEventNbr': order['parsed_order_info']['CurrentStatus']['EventNbr'],
            'CurrentStatusCode': order['parsed_order_info']['CurrentStatus']['StatusCode'],
            'CurrentStatusDescr': order['parsed_order_info']['CurrentStatus']['Description'],
            'CurrentCity': order['parsed_order_info']['CurrentStatus']['City'],
            'StatusDatetimeUTC': order['parsed_order_info']['CurrentStatus']['DatetimeUTC'],
            'ShipName': order['parsed_order_info']['ShipTo']['Name'],
            'ShipAddress1': order['parsed_order_info']['ShipTo']['Address1'],
            'ShipAddress2': order['parsed_order_info']['ShipTo']['Address2'],
            'ShipAddress3': order['parsed_order_info']['ShipTo']['Address3'],
            'ShipAddress4': order['parsed_order_info']['ShipTo']['Address4'],
            'ShipCity': order['parsed_order_info']['ShipTo']['City'],
            'ShipState': order['parsed_order_info']['ShipTo']['State'],
            'ShipZip': order['parsed_order_info']['ShipTo']['Zip'],
            'ShipEmail': order['parsed_order_info']['ShipTo']['Email'],
            'ShipPhone': order['parsed_order_info']['ShipTo']['PhonePrimary'],
            'CountShipments': order['count_shipments'],
            'LastChecked': order['extract_time']
        }
        return rlm_order


