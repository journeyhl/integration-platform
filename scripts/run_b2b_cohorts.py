import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines.b2b_cohorts import B2BCohorts



backorders = B2BCohorts('.debug')
backorders.run()

bp = 'here'