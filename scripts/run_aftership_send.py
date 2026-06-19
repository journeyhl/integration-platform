import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines import SendToAfterShip, UpdateAfterShip
import time
aftership = SendToAfterShip('.debug')
u_aftership = UpdateAfterShip('.debug')

aftership.run()
time.sleep(5)
u_aftership.run()
bp = 'here'
