import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines import AddressValidator
from integration_platform.connectors import SQLConnector, AcumaticaAPI, AddressVerificationSystem
import polars as pl

addy_validator = AddressValidator('.debug')
completed_addy_validator = addy_validator.run()




bp = 'here'