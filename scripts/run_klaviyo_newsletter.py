import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines.klaviyo_newsletter import KlaviyoNewsletter
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

cutoff = datetime.now(ZoneInfo('America/New_York')) - timedelta(days=1)
cutoff_str = cutoff.strftime('%Y-%m-%dT%H:%M:%SZ')



klaviyo_created_records = KlaviyoNewsletter('.debug', is_newsletter=False, filter_if_not_newsletter=f"filter=greater-than(created,{cutoff_str})")
klaviyo_created_records.run()
klaviyo_updated_records = KlaviyoNewsletter('.debug', is_newsletter=False, filter_if_not_newsletter=f"filter=greater-than(updated,{cutoff_str})")
klaviyo_updated_records.run()
klaviyo_newsletter = KlaviyoNewsletter('.debug', is_newsletter=True)
klaviyo_newsletter.run()
