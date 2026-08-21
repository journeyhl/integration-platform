import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines.pack_ryder_shipments import PackRyderShipments


ship_sep = PackRyderShipments('.debug', 
# env='dev'
)
ship_sep.run()
bp = 'here'
# acu = AcumaticaAPI('acu')