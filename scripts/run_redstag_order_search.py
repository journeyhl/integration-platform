import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipelines import RedStagOrderSearch



redstag_order_search = RedStagOrderSearch('.debug')
redstag_order_search.run()





