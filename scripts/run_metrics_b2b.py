import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines import B2BMetrics

b2b = B2BMetrics('.debug')

b2b.run()

bp = 'here'
