import requests
import random
import geopandas as gpd
from shapely.geometry import shape
from .dataset import Dataset
from .utils import html_box

class Table(Dataset):
    """
    This is the main Table class.

    Parameters
    ----------
    id_hash: int
        An ID hash.
    attributes: dic
        A dictionary holding the attributes of a tabular dataset.
    server: str
        A string of the server URL.
    """
    def __init__(self, id_hash=None, attributes=None, server="https://api.skydipper.com"):
        super().__init__(id_hash=id_hash, attributes=attributes, server=server)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Table {self.id} {self.attributes['name']})"

    def fetch_query(self, sql):
        """
        Forms a base query and returns data
        """
        table_name = self.attributes.get('tableName', 'data')
        sql = sql.replace('FROM data', f'FROM {table_name}')
        try:
            url = (f'{self.server}/v1/query/{self.id}?sql={sql}')
            r = requests.get(url)
            if r.status_code == 200:
                response_data = r.json().get('data')
                for d in response_data:
                    if d.get('the_geom', None):
                        d['geometry'] = shape(d['the_geom'])
                return response_data
            else:
                raise ValueError(f'Unable to get table {self.id} from {r.url}')
        except:
            raise ValueError(f'Unable to get table {self.id} from {r.url}')

    def head(self, n=5):
        """
        Returns a table as a GeoPandas GeoDataframe from a Vizzuality API using the query endpoint.

        Parameters
        ----------
        n: int
            Number of rows in the head.
        decode_geom: bool
            A flag to decode geometries into geom objects.
        """
        sql = f'SELECT * FROM data LIMIT {n}'
        response_data = self.fetch_query(sql=sql)
        try:
            gdf = gpd.GeoDataFrame(response_data)
            if 'geometry' in gdf:
                gdf = gdf.set_geometry('geometry')
            return gdf
        except:
            raise ValueError(f'Unable to get table {self.id}')

    def query(self, sql=None):
        """
        Return an SQL query as a valid dataframe object.

        Parameters
        ----------
        sql: str
            A valid SQL query e.g. 'SELECT * FROM data LIMIT 5'
        decode_geom: bool
            A flag to decode geometries into geom objects.
        """
        if not sql: sql = 'SELECT * FROM data LIMIT 5'
        if type(sql) != str:
            raise ValueError('SQL query should be passed as a string.')
        response_data = self.fetch_query(sql=sql)
        try:
            gdf = gpd.GeoDataFrame(response_data)
            if 'geometry' in gdf:
                gdf = gdf.set_geometry('geometry')
            return gdf
        except:
            raise ValueError(f'Unable to query table {self.id} with {sql}')