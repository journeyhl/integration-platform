import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines.acu_to_dbc_inventory_summary import AcuToDbcInventorySummary




inventory_summary = AcuToDbcInventorySummary('.debug')
inventory_summary.run()

    