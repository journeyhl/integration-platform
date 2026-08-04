import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines.ryder_to_dbc import RyderToDbc

ryder = RyderToDbc('.debug')
ryder.run()

bp = 'here'
