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
        return data_loaded
    
    def log_results(self, data_loaded):
        pass