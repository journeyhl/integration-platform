import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines.klaviyo_data_push import KlaviyoDataPush
from integration_platform.pipelines.klaviyo_newsletter import KlaviyoNewsletter
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import json


# cutoff = datetime.now(ZoneInfo('America/New_York')) - timedelta(days=1.5)
# cutoff_str = cutoff.strftime('%Y-%m-%dT%H:%M:%SZ')
    
# klaviyo_created_records = KlaviyoNewsletter('.debug', is_newsletter=False, filter_if_not_newsletter=f"filter=greater-than(created,{cutoff_str})")
# klaviyo_created_records.run()
# klaviyo_updated_records = KlaviyoNewsletter('.debug', is_newsletter=False, filter_if_not_newsletter=f"filter=greater-than(updated,{cutoff_str})")
# klaviyo_updated_records.run()
timestamp = datetime.now(ZoneInfo('America/New_York'))

klaviyo = KlaviyoDataPush('.debug')
klaviyo.run()
bp = 'here'





profiles = klaviyo.centralstore.query_db("""
select distinct ID 
from klaviyo.ProfileHeader h
inner join klaviyo.DataPushLog d on h.ID = d.KlaviyoID 

where ConsentUpdate like 'Email%' and IsNewsletter = 0
""").to_dicts()

payload = { "data":[{"type": "profile","id": row['ID']} for row in profiles]}

db_newsletter_rows = [{'ID': row['id'], 'Timestamp': timestamp} for row in payload['data']]
klaviyo.klaviyo.add_profiles_to_list(payload = payload)
klaviyo.centralstore.merge_table_paginated(table_name='klaviyo.NewsletterAdditions', data=db_newsletter_rows)

pass

# test = klaviyo.klaviyo.get_profiles(filter="equals(email,'barbara.roberts1798@gmail.com')")
