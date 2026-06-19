import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines import AcuToDbcCustomers




customers_to_dbc = AcuToDbcCustomers('.debug')
completed_customers_to_dbc = customers_to_dbc.run()

    