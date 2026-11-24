import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines import UCMI_HubspotCustomers, KlaviyoNewsletter, KlaviyoDataPush, KlaviyoWritebackHubspot
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def run():
    fn = '.debug-klaviyo_hubspot_data_feed'
    hubspot = UCMI_HubspotCustomers(function=fn, rapid_fire=True, rapid_fire_frequency_mins=60)
    hubspot.run()

    klaviyo_to_db = KlaviyoNewsletter(function=fn, is_newsletter=True)
    klaviyo_to_db.run()
    cutoff = (datetime.now(ZoneInfo('America/New_York')) - timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
    klaviyo_to_db.is_newsletter = False
    klaviyo_to_db.filter_if_not_newsletter = f"filter=greater-than(updated,{cutoff})"
    klaviyo_to_db.ts_pipeline_start = datetime.now(ZoneInfo('America/New_York'))
    klaviyo_to_db._init_logging_()
    klaviyo_to_db.run()


    db_to_klaviyo = KlaviyoDataPush(function=fn)
    db_to_klaviyo.run()

    hubspot_writeback = KlaviyoWritebackHubspot(function='fn')
    hubspot_writeback.run()



run()
bp = 'here'
