import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipelines import Five9CallSegments

five9 = Five9CallSegments('.debug')
five9.run()
bp = 'here'