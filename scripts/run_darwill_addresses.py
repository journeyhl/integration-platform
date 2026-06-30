import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines import DarwillAddresses

dw = DarwillAddresses('.debug')
# dw.run()

bp = 'here'

dw.etl_with_csv(csv_file_path=r'C:\Users\derfj\Desktop\Python\Work\logistics-integration-platform\dw_OlderBuyers.csv', source_file='OlderBuyers')
bp = 'here'
dw.etl_with_csv(csv_file_path=r'C:\Users\derfj\Desktop\Python\Work\logistics-integration-platform\dw_RecentBuyers.csv', source_file='RecentBuyers')

bp = 'here'

