import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines import UCMI_HubspotCustomers, KlaviyoNewsletter, KlaviyoDataPush
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def run():
    fn = '.debug-klaviyo_hubspot_data_feed'
    hubspot = UCMI_HubspotCustomers(function=fn, rapid_fire=True)
    hubspot.run()

    cutoff = datetime.now(ZoneInfo('America/New_York')) - timedelta(hours=1)
    cutoff_str = cutoff.strftime('%Y-%m-%dT%H:%M:%SZ')
    klaviyo_to_db = KlaviyoNewsletter(function=fn, is_newsletter=False, filter_if_not_newsletter=f"filter=greater-than(created,{cutoff_str})")
    klaviyo_to_db.run()
    bp = 'here'
    klaviyo_to_db.filter_if_not_newsletter = f"filter=greater-than(updated,{cutoff_str})"
    klaviyo_to_db.run()

    db_to_klaviyo = KlaviyoDataPush(function=fn)
    db_to_klaviyo.run()


run()
bp = 'here'
