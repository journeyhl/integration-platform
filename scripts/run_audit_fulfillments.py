import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.connectors import AcumaticaAPI
from integration_platform.pipelines import AuditFulfillment


audit_fulfillment = AuditFulfillment('.debug')
audit_fulfillment.run()
bp = 'here'
# acu = AcumaticaAPI('acu')