import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipelines import ConsignmentReclassification

cosignments = ConsignmentReclassification(function='.debug', env='dev')

cosignments.run()

bp = 'here'
#IntegrationPlatform_acudev