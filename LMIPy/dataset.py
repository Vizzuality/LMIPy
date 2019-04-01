import requests
import random
from .layer  import Layer
from .utils import html_box
from .lmipy import Vocabulary, Metadata


class Dataset:
    """
    This is the main Dataset class.

    Parameters
    ----------
    id_hash: int
        An ID hash of the dataset in the API.
    attributes: dic
        A dictionary holding the attributes of a dataset.
    sever: str
        A URL string of the vizzuality server.
    """
    def __init__(self, id_hash=None, attributes=None, server='https://api.resourcewatch.org'):
        self.id = id_hash
        self.layers = []
        self.server = server
        if not attributes:
            self.attributes = self.get_dataset()
        else:
            self.attributes = attributes
        if len(self.attributes.get('layer')) > 0:
            self.layers = [Layer(attributes=l) for l in self.attributes.get('layer')]
            _ = self.attributes.pop('layer')
        if len(self.attributes.get('metadata')) > 0:
            self.metadata = Metadata(self.attributes.get('metadata')[0])
            _ = self.attributes.pop('metadata')
        else:
            self.metadata = False
        if len(self.attributes.get('vocabulary')) > 0:
            self.vocabulary = Vocabulary(self.attributes.get('vocabulary')[0])
            _ = self.attributes.pop('vocabulary')
        else:
            self.vocabulary = False
        self.url = f"{server}/v1/dataset/{id_hash}?hash={random.getrandbits(16)}"

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Dataset {self.id}"

    def _repr_html_(self):
        return html_box(item=self)

    def get_dataset(self):
        """
        Retrieve a dataset from a server by ID.
        """
        hash = random.getrandbits(16)
        url = (f'{self.server}/v1/dataset/{self.id}?includes=layer,vocabulary,metadata&hash={hash}')
        r = requests.get(url)
        if r.status_code == 200:
            return r.json().get('data').get('attributes')
        else:
            raise ValueError(f'Unable to get dataset {self.id} from {r.url}')

    def __carto_query__(self, sql, decode_geom=False, APIKEY=None):
        """
        Returns a GeoPandas GeoDataFrame for CARTO datasets.
        """

        if 'the_geom' not in sql and decode_geom == True:
            sql = sql.replace('SELECT', 'SELECT the_geom,')

        if 'count' in sql:
            decode_geom = False

        table_name = self.attributes.get('tableName', 'data')
        sql = sql.replace('FROM data', f'FROM {table_name}').replace('"', "'")

        connector = self.attributes.get('connectorUrl', '')

        if connector:
            account = connector.split('.carto.com/')[0]
            urlCartoContext = "{0}.carto.com".format(account)

            cc = cf.CartoContext(base_url=urlCartoContext, api_key=APIKEY)

        table = self.attributes.get('tableName', None)
        if table:
            return cc.query(sql, decode_geom=decode_geom)

    def query(self, sql="SELECT * FROM data LIMIT 5", decode_geom=False, APIKEY=None):
        """
        Returns a carto table as a GeoPandas GeoDataframe from a Vizzuality API using the query endpoint.
        """
        provider = self.attributes.get('provider', None)
        if provider != 'cartodb':
            raise ValueError(f'Unable to perform query on datasets with provider {provider}. Must be `cartodb`.')

        return self.__carto_query__(sql=sql, decode_geom=decode_geom)

    def head(self, n=5, decode_geom=True, APIKEY=None):
        """
        Returns a table as a GeoPandas GeoDataframe from a Vizzuality API using the query endpoint.
        """
        sql = f'SELECT * FROM data LIMIT {n}'
        return self.__carto_query__(sql=sql, decode_geom=decode_geom)