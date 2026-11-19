import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines.klaviyo_data_push import KlaviyoDataPush
from integration_platform.pipelines.klaviyo_newsletter import KlaviyoNewsletter
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import json


klaviyo = KlaviyoDataPush('.debug')
klaviyo.run()
bp = 'here'



