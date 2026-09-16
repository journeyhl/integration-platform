import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines.klaviyo_newsletter import KlaviyoNewsletter




klaviyo = KlaviyoNewsletter('.debug')
klaviyo.run()

    