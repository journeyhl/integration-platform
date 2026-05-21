import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipelines import HubSpotContacts

hs_contacts = HubSpotContacts(function='.debug')
hs_contacts.run()

bp = 'here'
