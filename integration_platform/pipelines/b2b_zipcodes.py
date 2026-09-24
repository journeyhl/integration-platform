from integration_platform.pipelines import Pipeline
from integration_platform.transform.b2b_zipcodes import Transform
from integration_platform.connectors.sftp import SFTP
from integration_platform.connectors.hubspot_api import HubSpotAPI
import polars as pl

class B2BZipCodes(Pipeline):
    def __init__(self, function: str, env: str='prod'):
        super().__init__(pipeline_name='b2b-zipcodes', function=function, env=env)
        self.hubspot = HubSpotAPI(self)
        self.transformer = Transform(self)
        self.sftp = SFTP(self)

    def extract(self):
        properties = self.centralstore.query_db(query="select ObjectType, otName, Name, Label, Type, FieldType from hs.Properties where otName in('zip_codes', 'territories')")
        self._extract_shapeup_(properties=properties)



        b2bs = self.sftp.get_file_as_dataframe(type='xlsx', path=r'/users/jj/ZIP_Code_by_Territory_Aug_2026.xlsx')
        zips = self.centralstore.query_db('select * from ZipCodes order by Zip')
        data_extract = zips.join(other=b2bs, on='Zip', how='inner')
        return data_extract

    def transform(self, data_extract):
        data_transformed = self.transformer.landing(data_extract=data_extract)
        return data_transformed
    
    def load(self, data_transformed):
        data_loaded = {}
        dt_dicts = data_transformed.to_dicts()
        dt_dicts = self.default_loader.add_InsertedDT_to_list(dt_dicts)
        self.centralstore.merge_table_paginated(table_name='_dev.B2BZipCodes', data=dt_dicts)
        return data_loaded
    
    def log_results(self, data_loaded):
        pass




    def _extract_shapeup_(self, properties: pl.DataFrame):
        '''_extract_shapeup_
        ---
        
        Move elsewhere when complete!
        
        Parameters
        ---
        :param (*pl.DataFrame*) `properties`: extracted properties from sql
        '''
        test = properties.group_by(['ObjectType', 'otName']).agg(['Name', 'Label', 'Type', 'FieldType'])
        terrs = test.sql("select * from self where otName = 'territories'").row(0, named=True)
        zips = test.sql("select * from self where otName = 'zip_codes'").row(0, named=True)
        territories = self.hubspot.get_list_with_membership_details(list_id=3547, object_type=terrs['ObjectType'], props=','.join(terrs['Name']), associations=','.join(['0-2', zips['ObjectType']]), object_data=terrs)
        
        zipcodes = self.hubspot.get_list_with_membership_details(list_id=3548, object_type=zips['ObjectType'], props=','.join(zips['Name']), associations=','.join(['0-2', terrs['ObjectType']]), object_data=zips)

        bp = 'here'

