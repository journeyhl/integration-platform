import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines import CustomerCohorts


d2c = CustomerCohorts(function='.debug', b2b_d2c='D2C')
d2c.run()
bp = 'here'


# cohorts = CustomerCohorts(function='.debug', b2b_d2c='Both')
# cohorts.run()

b2b = CustomerCohorts(function='.debug', b2b_d2c='B2B')
b2b.run()
bp = 'here'
