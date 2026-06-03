import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipelines import AcuToDbcShipments




shipments_to_dbc = AcuToDbcShipments('.debug')
completed_shipments_to_dbc = shipments_to_dbc.run()

