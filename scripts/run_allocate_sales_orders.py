import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines import AllocateSalesOrders

allocate_orders = AllocateSalesOrders(function='.debug', env='dev')

allocate_orders.run()

bp = 'here'
#IntegrationPlatform_acudev