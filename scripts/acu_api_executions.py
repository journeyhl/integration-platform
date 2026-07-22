import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.connectors import AcumaticaAPI, SQLConnector


acu = AcumaticaAPI(pipeline='.debug', 
# env='dev'
)
db = SQLConnector('.debug', 'AcumaticaDb')


order_data = {
    'OrderType': 'WB',
    'OrderNbr': 'WB109889',
    'Warehouse': 'REDSTAGSWT',
}

# acu.manage_sales_allocations(order_data=order_data)
# acu.prepare_shopify(entity='Product Availability')


acu.prepare_shopify(entity='Template Item')

records = db.query_to_dataframe(db.queries.ProductSyncHistory).to_dicts()

record_to_process = acu.get_process_shopify_records(entity='Template Item')

bp = 'here'

for record in records: 
    test = acu.process_shopify(record, entity='Template Item')
test = acu.process_shopify(entity_data=record_to_process, entity='Template Item')


bp = 'here'
