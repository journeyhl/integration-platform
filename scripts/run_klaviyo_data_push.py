import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines.klaviyo_data_push import KlaviyoDataPush




klaviyo = KlaviyoDataPush('.debug')

# test = klaviyo.klaviyo.get_profiles(filter="equals(email,'barbara.roberts1798@gmail.com')")

klaviyo.run()
pass
    