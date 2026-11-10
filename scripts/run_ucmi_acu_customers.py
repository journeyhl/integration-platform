import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines.ucmi_acumatica import UCMI_AcumaticaCustomers

ucmi = UCMI_AcumaticaCustomers('.debug')
ucmi.run()

bp = 'here'
