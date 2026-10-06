from integration_platform.pipelines import Pipeline
from integration_platform.transform.b2b_zipcodes import Transform
from integration_platform.transform.b2b_zipcodes_hubspot import TransformHubspot
from integration_platform.connectors.sftp import SFTP
from integration_platform.connectors.hubspot_api import HubSpotAPI
import polars as pl
from datetime import datetime
from zoneinfo import ZoneInfo
class B2BZipCodes(Pipeline):
    def __init__(self, function: str, env: str='prod'):
        super().__init__(pipeline_name='b2b-zipcodes', function=function, env=env)
        self.hubspot = HubSpotAPI(self)
        self.transformer = Transform(self)
        self.hubspot_transformer = TransformHubspot(self)
        self.sftp = SFTP(self)

    def extract(self):
        self.ts_extract_s = datetime.now(ZoneInfo('America/New_York'))
        db_extract = self._shape_db_extract_()
        hubspot_extract = self._shape_hubspot_extract_()
        self.ts_extract_f = datetime.now(ZoneInfo('America/New_York'))
        data_extract = {
            'hubspot': hubspot_extract,
            'db': db_extract
        }
        self.centralstore.reconnect()
        return data_extract

    def transform(self, data_extract):
        db_transformed = self.transformer.landing(data_extract=data_extract['db'])
        hubspot_transformed = self.hubspot_transformer.landing(data_extract=data_extract['hubspot'])
        data_transformed = {
            'db_transformed': db_transformed,
            'hubspot_transformed': hubspot_transformed
        }
        return data_transformed
    
    def load(self, data_transformed):
        data_loaded = {}
        self._load_hubspot_to_db_(data_transformed['hubspot_transformed'])
        db_dicts = data_transformed['db_transformed'].to_dicts()
        db_dicts = self.default_loader.add_InsertedDT_to_list(db_dicts)
        self.centralstore.merge_table_paginated(table_name='_dev.B2BZipCodes', data=db_dicts)
        return data_loaded
    
    def log_results(self, data_loaded):
        pass


    def _load_hubspot_to_db_(self, hubspot: dict):
        hs_territories = hubspot['territories']
        hs_zipcodes = hubspot['zipcodes']
        hs_associations = hubspot['associations']
        for key, dataset in hubspot.items():
            bp = 'here'
            hubspot[key]['data'] = self.default_loader.add_InsertedDT_to_list(dataset['data'])
            bp = 'here'
            self.centralstore.merge_table_paginated(table_name=hubspot[key]['qualified_name'], data=hubspot[key]['data'])
            bp = 'here'


    def _shape_db_extract_(self) -> pl.DataFrame:
        ''':class:`~integration_platform.pipelines.b2b_zipcodes.B2BZipCodes`.:meth:`~integration_platform.pipelines.b2b_zipcodes.B2BZipCodes._shape_db_extract_`
        ---
        
        Manages database portion of data extract
        
        Returns
        ---
        :return `db_extract` (pl.DataFrame): dataframe of zipcodes from database joined with that of the file found in sftp server
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.pipelines.b2b_zipcodes.B2BZipCodes`.:meth:`~integration_platform.pipelines.b2b_zipcodes.B2BZipCodes.extract`
        
        ## Downstream Calls (Methods/Functions called)
        
         ### :class:`~integration_platform.connectors.sftp.SFTP`.:meth:`~integration_platform.connectors.sftp.SFTP.get_file_as_dataframe`
        
         ### :class:`~integration_platform.connectors.sql.SQLConnector`.:meth:`~integration_platform.connectors.sql.SQLConnector.query_db`
        '''        
        bp = 'here'
        b2bs = self.sftp.get_file_as_dataframe(type='xlsx', path=r'/users/jj/ZIP_Code_by_Territory_Aug_2026.xlsx')
        zips = self.centralstore.query_db('select * from ZipCodes order by Zip')
        db_extract = zips.join(other=b2bs, on='Zip', how='inner')
        return db_extract

    def _shape_hubspot_extract_(self) -> dict:
        ''':class:`~integration_platform.pipelines.b2b_zipcodes.B2BZipCodes`.:meth:`~integration_platform.pipelines.b2b_zipcodes.B2BZipCodes._shape_hubspot_extract_`
        ---
        
        Manages hubspot portion of data extract
        
        Returns
        ---
        :return `hubspot_extract` (dict): dictionary containing `zipcodes` and `territories`, which contain the members of the respective lists
        
        <hr>
        
        ## Upstream Calls (Methods/Functions Called by)
        
         ### :class:`~integration_platform.pipelines.b2b_zipcodes.B2BZipCodes`.:meth:`~integration_platform.pipelines.b2b_zipcodes.B2BZipCodes.extract`
        
        ## Downstream Calls (Methods/Functions called)
        
         ### :class:`~integration_platform.pipelines.b2b_zipcodes.B2BZipCodes`.:meth:`~integration_platform.pipelines.b2b_zipcodes.B2BZipCodes._shape_hubspot_extract_`
        
          - Called twice, once for territories and zipcodes
        '''        
        properties = self.centralstore.query_db(query="select ObjectType, otName, Name, Label, Type, FieldType from hs.Properties where otName in('zip_codes', 'territories')")
        test = properties.group_by(['ObjectType', 'otName']).agg(['Name', 'Label', 'Type', 'FieldType'])
        terrs = test.sql("select * from self where otName = 'territories'").row(0, named=True)
        zips = test.sql("select * from self where otName = 'zip_codes'").row(0, named=True)

        territories = self.hubspot.get_list_with_membership_details(list_id=3547, object_type=terrs['ObjectType'], props=','.join(terrs['Name']), associations=','.join(['0-2', terrs['ObjectType']]), object_data=terrs)
        zipcodes = self.hubspot.get_list_with_membership_details(list_id=3548, object_type=zips['ObjectType'], props=','.join(zips['Name']), associations=','.join(['0-2', zips['ObjectType']]), object_data=zips)
        hubspot_extract = {
            'territories': territories,
            'zipcodes': zipcodes
        }
        return hubspot_extract

