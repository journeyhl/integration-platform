import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines import CallCenterMFR

mfr = CallCenterMFR('.debug')

mfr.run()

bp = 'here'
