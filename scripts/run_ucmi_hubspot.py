import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines.ucmi_hubspot import UCMI_HubspotCustomers

ucmi = UCMI_HubspotCustomers('.debug')
ucmi.run()

bp = 'here'
