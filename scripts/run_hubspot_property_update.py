import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipelines import HubspotPropertyUpdate

product_list = HubspotPropertyUpdate(function='.debug')

product_list.run()

bp = 'here'
#IntegrationPlatform_acudev