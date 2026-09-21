import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines import B2BCohorts, B2BCohortsLinkToAcu, CustomerCohorts


cohorts = CustomerCohorts(function='.debug', b2b_d2c='Both')
cohorts.run()

d2c = CustomerCohorts(function='.debug', b2b_d2c='D2C')
d2c.run()
bp = 'here'

b2bs = B2BCohorts('.debug')
b2bs.run()

b2b_link = B2BCohortsLinkToAcu('.debug')
b2b_link.run()
bp = 'here'