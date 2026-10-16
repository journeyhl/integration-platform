import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines.ucmi_shopify import UCMI_ShopifyCustomers

ucmi = UCMI_ShopifyCustomers('.debug')
ucmi.run()

bp = 'here'
