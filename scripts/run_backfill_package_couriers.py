import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines.link_courier_to_packages_acu_backfill import CourierPackage_Backfill

couriers = CourierPackage_Backfill('.debug')
couriers.run()

bp = 'here'
