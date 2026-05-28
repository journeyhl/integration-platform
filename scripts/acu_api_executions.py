import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from connectors import AcumaticaAPI



acu = AcumaticaAPI('.debug')

bp = 'here'
