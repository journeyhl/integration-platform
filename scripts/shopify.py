import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.connectors.shopify import ShopifyAPI
from integration_platform.pipelines.dev.shopify import ShopifyGraphQL


shop = ShopifyGraphQL('.debug')

response = shop.extract()

bp = 'here'