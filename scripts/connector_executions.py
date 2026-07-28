import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.connectors import Teams, HubSpotAPI, SFTP, RyderAPI
from integration_platform.pipelines import HubspotSnapshot



# test = RyderAPI(pipeline='test', env='prod')
# bp = 'here'




hs = HubSpotAPI('.script')


list_pipe = hs.get_list_with_membership_contact_details(list_id=3285)

property_str = 'firstname,lastname,lead_source,email,phone,emailaddress,keycode,product,adddate,createdate,notes_last_updated,hubspot_owner_id,call_summary,hs_lead_status,hs_marketable_status,lead_source_date,intents_during_call,toll_free__,bps,unitsperorder,totalorders,revenueperorder,totalunits,revenue,last_five9_call_disposition,last_five9_call_at,acumatica_product_list,who_is_the_chair_for,notes_last_contacted,notes_next_activity_date,num_contacted_notes,hs_analytics_source,hs_latest_source,date_and_time_added_to_outbound_list,lead_grade,date_added_to_outbound_list,budget_range,created_on_weekend,kustomer_id,sold,date_became_the_warm_lead'

test1 = hs.get_list_with_membership(list_id=3285)

rows: dict = test1['rows']
bp = 'here'
rowlen = len(rows)
for i, (contact, data) in enumerate(rows.items()):
    bp = 'here'
    print(f'{i+1}/{rowlen}')
    contact_details = hs.get_contact_by_id(contact_id=contact, properties=property_str)
    data['details'] = contact_details
    bp = 'here'
bp = 'here'

test = hs.retrieve_companies()
hs.search_by_phone(phone_value='+18475731908', object_type='companies',)
bp = 'here'







sftp = SFTP('pipeline')
# sftp.list_directory('/apps/five9/reports')
call_segments = sftp.get_csv_file_as_dataframe()
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