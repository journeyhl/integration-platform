import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines.send_ryder_shipments import SendRyderShipments

ryder = SendRyderShipments('.debug')
ryder.run()

bp = 'here'
