import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines.acu_to_dbc_b2b_collections import AcuToDbcB2BCollections

b2b_collections = AcuToDbcB2BCollections('.debug')

b2b_collections.run()

bp = 'here'
