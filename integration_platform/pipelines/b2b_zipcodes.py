from integration_platform.pipelines import Pipeline
from integration_platform.transform.b2b_zipcodes import Transform
from integration_platform.connectors.sftp import SFTP


class B2BZipCodes(Pipeline):
    def __init__(self, function: str, env: str='prod'):
        super().__init__(pipeline_name='b2b-zipcodes', function=function, env=env)
        # self.hubspot = HubSpotAPI(self)
        self.transformer = Transform(self)
        self.sftp = SFTP(self)

    def extract(self):
        b2bs = self.sftp.get_file_as_dataframe(type='xlsx', path=r'/users/jj/ZIP_Code_by_Territory_Aug_2026.xlsx')
        zips = self.centralstore.query_db('select * from ZipCodes order by Zip')
        data_extract = zips.join(other=b2bs, on='Zip', how='inner')
        return data_extract

    def transform(self, data_extract):
        data_transformed = self.transformer.landing(data_extract=data_extract)
        return data_transformed
    
    def load(self, data_transformed):
        data_loaded = {}
        # test = self.centralstore.sqlhelper.dataframe_to_table_create_statement(df=data_transformed, table_name='_dev.B2BZipCodes')
        dt_dicts = data_transformed.to_dicts()
        dt_dicts = self.default_loader.add_InsertedDT_to_list(dt_dicts)
        self.centralstore.merge_table_paginated(table_name='_dev.B2BZipCodes', data=dt_dicts)
        # self.centralstore.insert_df(df_data_loaded=)
        return data_loaded
    
    def log_results(self, data_loaded):
        pass