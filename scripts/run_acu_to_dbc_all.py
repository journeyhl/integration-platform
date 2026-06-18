import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines import AcuToDbcCustomers, AcuToDbcPhoneRevenue, AcuToDbcQuotes, AcuToDbcSalesOrders, AcuToDbcShipments

'''
This script executes all AcumaticaDb to db_CentralStore pipelines

'''
orders = AcuToDbcSalesOrders('.debug')
orders.run()
bp = 'here'

shipments = AcuToDbcShipments('.debug')
shipments.run()
bp = 'here'

quotes = AcuToDbcQuotes('.debug')
quotes.run()
bp = 'here'

customers = AcuToDbcCustomers('.debug')
customers.run()
bp = 'here'

phone_rev = AcuToDbcPhoneRevenue('.debug')
phone_rev.run()
bp = 'here'

