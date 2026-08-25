import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines import B2BCohorts, B2BCohortsLinkToAcu



b2bs = B2BCohorts('.debug')
b2bs.run()

b2b_link = B2BCohortsLinkToAcu('.debug')
b2b_link.run()
bp = 'here'