from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from integration_platform.pipelines.send_ryder_shipments import SendRyderShipments
import logging
import polars as pl
from datetime import datetime

class Transform:
    def __init__(self, pipeline: SendRyderShipments):
        self.pipeline = pipeline
        self.logger = logging.getLogger(f'{pipeline.pipeline_name}.Transform')
        pass


    def landing(self, data_extract: pl.DataFrame):
        bp = 'here'
        dicts = data_extract.to_dicts()
        shipments = {}
        for i, shipment in enumerate(dicts):
            if shipments.get(shipment['ShipmentNbr']) == None:
                shipments[shipment['ShipmentNbr']] = [shipment]
            else:
                shipments[shipment['ShipmentNbr']].extend(shipment)
            bp = 'here'

        for i, (shipment, data) in enumerate(shipments.items()):
            bp = self.format_payload(shipment_data=data)
            bp = 'here'
        bp = 'here'



    def format_payload(self, shipment_data):
        shipment_header = {
            'ShipmentNbr': shipment_data[0]['ShipmentNbr'],
            'rlmActionCode': shipment_data[0]['rlmActionCode'],
            'PO': shipment_data[0]['PO'],
            'ShipDate': shipment_data[0]['ShipDate'],
        }
        payload = {
            'enterpriseClientID': 'JOURHL',
            'orderType': shipment_header['rlmActionCode'],
            'OrderreqWorkflow': 'REGULAR',
            'weightUOM': 'LB',
            'volumeUOM': 'IN',
            'ClientRefType': 'TS',
            'references': [
                {
                'referenceType': 'CLIENT',
                'referenceNumber': shipment_header['ShipmentNbr']
                },
                {
                'referenceType': 'PO',
                'referenceNumber': shipment_header['PO']
                }
            ],
            'orderreq-dates': [
                {
                'dateType': 'ENTRY',
                'date': shipment_header['ShipDate']
                }
            ],

        }
        return payload