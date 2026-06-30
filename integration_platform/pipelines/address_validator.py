from integration_platform.pipelines import Pipeline
from integration_platform.connectors import AddressVerificationSystem, AcumaticaAPI
import polars as pl
from integration_platform.transform.address_validator import Transform
from integration_platform.load.address_validator import Load
import json
import time
class AddressValidator(Pipeline):
    '''`AddressValidator`(Pipeline)
    ---
    <hr>
    
    Pipeline to ***override, update and validate*** any unvalidated addresses on WB orders with a status of **On Hold**. Afterwards, **Removes from hold** and **creates Shipment**

    # Extraction
     - Returns Sales Orders from **AcumaticaDb** that require address validation
        - Currently looks at **WB** orders in **Open** status that **do not have a validated address**

    # Transformation
     - Given a dictionary containing a response from AVS, format the payload needed to override and update a Customer's ShipTo Address on a particular **Order**
     - Formats the constant part of the dict of data that we'll load to **_util.acu_api_log** when overriding and updating an address
     - Formats the constant part of the dict of data that we'll load to **_util.acu_api_log** when validating an address


    # Load
     - Overrides and updates Order addresses
     - Validates Order address
     - Removes Order from hold
     - Creates Shipment

    # Results Logging
     - Upserts Acumatica API interactions to **_util.acu_api_log**
    '''
    def __init__(self, function: str):
        super().__init__('address-validator', function, env = 'dev')
        self.avs = AddressVerificationSystem(self)
        self.acu_api = AcumaticaAPI(self, env = 'dev')
        self.transformer = Transform(self)
        self.loader = Load(self)

    def extract(self) -> dict[str, pl.DataFrame]:
        main_extract = self.acudb.query_to_dataframe(self.acudb.queries.ValidateAddresses)
        filter_extract = self.acudb.query_to_dataframe(self.acudb.queries.AllocateSalesOrders_filter_address_validator)
        data_extract = {
            'main_extract': main_extract,
            'filter_extract': filter_extract
        }
        return data_extract

    def transform(self, data_extract: dict[str, pl.DataFrame]) -> list:
        data_transformed = self.transformer.transform(data_extract)
        return data_transformed
    
    def load(self, data_transformed: list):
        data_loaded = self.loader.landing(data_transformed)
        return self.acu_api.data_log
    
    def log_results(self, data_loaded):
        self.acu_api._logout()

        self.logger.info(f'Logging acu_api interactions...')
        for entry in data_loaded:
            entry['Payload'] = json.dumps(entry['Payload'])
        self.centralstore.checked_upsert('_util.acu_api_log', data_loaded)
        pass