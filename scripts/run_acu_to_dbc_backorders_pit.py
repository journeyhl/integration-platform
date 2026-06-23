import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines import AcuToDbcBackordersPointInTime



backorders = AcuToDbcBackordersPointInTime('.debug')
backorders.run()

bp = 'here'