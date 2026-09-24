import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines.acu_to_dbc import ModularAcuToDbc




modular = ModularAcuToDbc(function='.debug', table_name='acu.Account')
modular.run()
modular.rerun(table_name='acu.CashAccount')
modular.rerun(table_name='acu.Sub')
modular.rerun(table_name='acu.CADeposit')
modular.rerun(table_name='acu.CADepositCharge')
modular.rerun(table_name='acu.CADepositDetail')
modular.rerun(table_name='acu.CATran')
modular.rerun(table_name='acu.ARRegister')
modular.rerun(table_name='acu.ARAdjust')
modular.rerun(table_name='acu.ARTran')
modular.rerun(table_name='acu.ARRegister')
bp = 'here'



modular = ModularAcuToDbc(function='.debug', table_name='acu.ARAdjust')
modular.run()
modular.rerun(table_name='acu.ARRegister')
modular.rerun(table_name='acu.ARTran')
bp = 'here'


modular = ModularAcuToDbc(function='.debug', table_name='acu.ARTran')
modular.run()
bp = 'here'
modular.rerun(table_name='acu.ARAdjust')
bp = 'here'




modular = ModularAcuToDbc(function='.debug', table_name='acu.Account')
modular.run()
modular.rerun(table_name='acu.Sub')
bp = 'here'



modular = ModularAcuToDbc(function='.debug', table_name='acu.ARRegister')
modular.run()
bp = 'here'

modular = ModularAcuToDbc(function='.debug', table_name='acu.ARTran')
modular.run()
bp = 'here'

modular = ModularAcuToDbc(function='.debug', table_name='acu.CADeposit')
modular.run()
bp = 'here'

modular = ModularAcuToDbc(function='.debug', table_name='acu.CADepositCharge')
modular.run()
bp = 'here'

modular = ModularAcuToDbc(function='.debug', table_name='acu.CADepositDetail')
modular.run()
bp = 'here'
