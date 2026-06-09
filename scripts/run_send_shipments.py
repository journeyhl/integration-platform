import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipelines import SendRMIShipments, SendRedStagShipments


send_redstag = SendRedStagShipments('.debug')
send_redstag.run()
bp = 'here'

rmi_shipments = SendRMIShipments('.debug')
rmi_shipments.run()
bp = 'here'