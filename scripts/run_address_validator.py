import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines import AddressValidator
from integration_platform.connectors import SQLConnector, AcumaticaAPI, AddressVerificationSystem
import polars as pl

addr_validator = AddressValidator(function='.debug', env='dev')
addr_validator.run()




bp = 'here'