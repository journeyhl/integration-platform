import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from connectors import AcumaticaAPI


order_data = {
    'OrderType': 'WB',
    'OrderNbr': 'WB109889',
    'Warehouse': 'REDSTAGSWT',
}

acu = AcumaticaAPI(pipeline='.debug', env='dev')
acu.manage_sales_allocations(order_data=order_data)

bp = 'here'
