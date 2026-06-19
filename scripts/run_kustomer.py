import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines import SendOrderDetailsToKustomer

kustomer = SendOrderDetailsToKustomer('.debug')
kustomer._re_init('backfill')
bp = 'here'
kustomer._re_init('backfill')
