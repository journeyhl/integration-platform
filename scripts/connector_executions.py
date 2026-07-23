import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.connectors import Teams, HubSpotAPI, SFTP, RyderAPI
from integration_platform.pipelines import HubSpotSnapshot



test = RyderAPI(pipeline='test', env='prod')
bp = 'here'












sftp = SFTP('pipeline')
# sftp.list_directory('/apps/five9/reports')
call_segments = sftp.get_csv_file_as_dataframe()
bp = 'here'


hs = HubSpotAPI('.script')
test = hs.retrieve_companies()
hs.search_by_phone(phone_value='+18475731908', object_type='companies',)
bp = 'here'


# sp = Sharepoint('testing')
# test = sp.get_file('/sites/Marketing/Shared Documents/Ad Planning/Ad Plan 2026.xlsx')
# bp = 'here'



# acu = AcumaticaAPI('.debug')

# acu.customers()

# bp = 'here'
# properties = hubsnap.hubapi.get_properties('contacts')


# hubsnap.centralstore.checked_upsert_paginated('hs.Properties', properties)

# bp = 'here'
# hubsnap.run()
# teams = Teams('script')
# bp = teams.send_message('test')
# bp = 'here'
# files.list_files(files)



# for p in hubapi.get_deal_pipelines():
#     print(p['id'], p['label'])
#     for s in p.get('stages', []):
#         print(' ', s['id'], s['label'])
# for owner_id, name in api.list_owners().items():
#     print(owner_id, name)