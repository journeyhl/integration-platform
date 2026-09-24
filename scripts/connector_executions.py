import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# from integration_platform.connectors import Teams, HubSpotAPI, SFTP, RyderAPI, RMIAPI
# from integration_platform.connectors.ryder_api import RyderAPI
from integration_platform.connectors.hubspot_api import HubSpotAPI
# from integration_platform.connectors.klaviyo import KlaviyoAPI
# from integration_platform.pipelines.base import Pipeline

map = {
    'territories':'2-67850902',
    'zip_codes': '2-61043340',
}

hs = HubSpotAPI(pipeline='.debug')
test = hs._request_(method='get', path=f'/crm/v3/objects/{map['territories']}')
t2 = hs.get_properties(object_type=map['territories'])

bp = 'here'
test2 = hs._request_(method='get', path=f'/crm/v3/objects/{map['zip_codes']}')

bp = 'here'





# rmi = RMIAPI('.script')
# inv_facility = rmi.get_inventory_data(rmi.ep_inventory_by_facility)
# inv_location = rmi.get_inventory_data(rmi.ep_inventory_by_location)
# inv_serials = rmi.get_inventory_data(rmi.ep_inventory_with_serials)
# bp = 'here'
