import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines import SendRMIReturns




rmi_returns = SendRMIReturns('.debug')
returns_result = rmi_returns.run()
bp = 'here'