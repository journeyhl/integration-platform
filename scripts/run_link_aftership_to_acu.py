import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines.link_aftership_to_acu import AftershipLinkToAcu

aftership = AftershipLinkToAcu('.debug')
aftership.run()

bp = 'here'
