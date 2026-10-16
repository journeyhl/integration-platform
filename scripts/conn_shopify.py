import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.connectors.shopify import ShopifyAPI

shop = ShopifyAPI('.debug')

shop.get_customers_bulk()
bp = 'here'