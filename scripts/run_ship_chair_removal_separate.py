import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines import ShipChairRemovalSeparate


ship_sep = ShipChairRemovalSeparate('.debug', 
env='dev'
)
ship_sep.run()
bp = 'here'
# acu = AcumaticaAPI('acu')