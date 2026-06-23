import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integration_platform.pipelines.get_closed_shipments_from_RMI import GetClosedShipmentsFromRMI #rmi-shipments

closed_shipment_pipeline = GetClosedShipmentsFromRMI('rmi_data_retrieval_pipeline')
closed_shipment_pipeline.run()

rmi_api = closed_shipment_pipeline.rmi
from integration_platform.pipelines.get_receipts_from_RMI import GetReceiptsFromRMI #rmi-receipts
receipt_pipeline = GetReceiptsFromRMI('rmi_data_retrieval_pipeline', rmi_api=rmi_api)
receipt_pipeline.run()

from integration_platform.pipelines.get_rmas_from_RMI import GetRMAsFromRMI #rmi-rmas
rma_pipeline = GetRMAsFromRMI('rmi_data_retrieval_pipeline', rmi_api=rmi_api)
rma_pipeline.run()