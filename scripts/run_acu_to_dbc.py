import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines.acu_to_dbc import ModularAcuToDbc

#TODO fix this
# acu_to_dbc = ModularAcuToDbc(function='.debug', table_name='acu.ARAdjust')
# acu_to_dbc.run()
# bp = 'here'

acu_to_dbc = ModularAcuToDbc(function='.debug', table_name='acu.ARRegister')
acu_to_dbc.run()
bp = 'here'

acu_to_dbc = ModularAcuToDbc(function='.debug', table_name='acu.ARTran')
acu_to_dbc.run()
bp = 'here'

acu_to_dbc = ModularAcuToDbc(function='.debug', table_name='acu.CADeposit')
acu_to_dbc.run()
bp = 'here'

acu_to_dbc = ModularAcuToDbc(function='.debug', table_name='acu.CADepositCharge')
acu_to_dbc.run()
bp = 'here'

acu_to_dbc = ModularAcuToDbc(function='.debug', table_name='acu.CADepositDetail')
acu_to_dbc.run()
bp = 'here'
