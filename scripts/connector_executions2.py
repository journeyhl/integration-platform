import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from integration_platform.connectors import Teams, HubSpotAPI, SFTP, RyderAPI, RMIAPI
# from integration_platform.connectors.ryder_api import RyderAPI
from integration_platform.connectors.fedex import Fedex
# from integration_platform.connectors.klaviyo import KlaviyoAPI
# from integration_platform.pipelines.base import Pipeline

fedex = Fedex('.debug')
fedex.get_rate()
bp = 'here'





# rmi = RMIAPI('.script')
# inv_facility = rmi.get_inventory_data(rmi.ep_inventory_by_facility)
# inv_location = rmi.get_inventory_data(rmi.ep_inventory_by_location)
# inv_serials = rmi.get_inventory_data(rmi.ep_inventory_with_serials)
# bp = 'here'
