import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines.link_b2b_cohorts_to_acu import B2BCohortsLinkToAcu



cohorts = B2BCohortsLinkToAcu('.debug')
cohorts.run()

bp = 'here'