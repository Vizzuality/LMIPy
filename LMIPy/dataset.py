import requests
import json
import random
import geopandas as gpd
import os
import datetime
#from shapely.geometry import shape
from pprint import pprint
from .layer import Layer
from .utils import html_box
from .lmipy import Vocabulary, Metadata
from colored import fg, bg, attr


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

        if len(self.attributes.get('layer', [])) > 0:
            self.layers = [Layer(attributes=l, server=self.server) for l in self.attributes.get('layer')]
            _ = self.attributes.pop('layer')
        if len(self.attributes.get('metadata', [])) > 0:
            self.metadata = [Metadata(attributes=m) for m in self.attributes.get('metadata')]
            _ = self.attributes.pop('metadata')
        else:
            self.metadata = []
        if len(self.attributes.get('vocabulary', [])) > 0:
            self.vocabulary =[Vocabulary(attributes=v) for v in self.attributes.get('vocabulary')]
            _ = self.attributes.pop('vocabulary')
        else:
            self.vocabulary = []
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
        try:
            hash = random.getrandbits(16)
            url = (f'{self.server}/v1/dataset/{self.id}?includes=layer,vocabulary,metadata&hash={hash}')
            r = requests.get(url)
        except:
            raise ValueError(f'Unable to get Dataset {self.id} from {r.url}')
        if r.status_code == 200:
            return r.json().get('data').get('attributes')
        else:
            raise ValueError(f'Dataset with id={self.id} does not exist.')

    def carto_query(self, sql):
        """
        Returns a GeoPandas GeoDataFrame for CARTO datasets. The sql query should
        always use dataset as the source (i.e. 'from dataset') as this will be
        replaced with the tableName from dataset.attributes.
        """
        sql = sql.lower().replace('from data',f"FROM {self.attributes.get('tableName')}")
        if not self.attributes.get('connectorUrl'):
            raise ValueError("ConnectorUrl attribute missing.")
        account = self.attributes.get('connectorUrl').split('/')[2].split('.')[0]
        urlCarto = f"https://{account}.carto.com/api/v2/sql"
        params = {"q": sql}
        r = requests.get(urlCarto, params=params)
        if r.status_code == 200:
            return gpd.GeoDataFrame(r.json().get('rows'))
        else:
            raise ValueError(f"Bad response from Carto {r.status_code}: {r.json()}")

    def query(self, sql="SELECT * FROM data LIMIT 5"):
        """
        Query a Dataset object

        Returns a table as a from queries against datasets in an API using the query endpoint.
        Table name must be `data` by default (or the CARTO table name, if known)

        Parameters
        ----------
        sql: str
            Valid SQL string.
        """
        provider = self.attributes.get('provider', None)
        if provider == 'cartodb':
            return self.carto_query(sql=sql)
        else:
            raise ValueError(f'Unable to perform query on datasets with provider {provider}. Must be `cartodb`.')

    def head(self, n=5, decode_geom=True, token=None):
        """
        Returns a table as a GeoPandas GeoDataframe from a Vizzuality API using the query endpoint.
        """
        sql = f'SELECT * FROM data LIMIT {n}'
        return self.carto_query(sql=sql)

    def update_keys(self):
        """
        Returns a list of attribute keys which could be updated.
        """
        update_blacklist = ['metadata','layer', 'vocabulary', 'updatedAt', 'userId', 'slug', "clonedHost", "errorMessage", "taskId", "dataLastUpdated"]
        updatable_fields = {f'{k}':v for k,v in self.attributes.items() if k not in update_blacklist}
        uk = list(updatable_fields.keys())
        return uk

    def update(self, update_params=None, token=None, show_difference=False):
        """
        Update a Dataset object

        To view the potential attributes that could be updated use the Dataset.update_keys() method.

        Parameters
        ----------
        update_params: dic
            A dictionary object containing {key: value} pairs of attributes to update.
        token: str
            A valid API key from the Resource Watch API. https://resource-watch.github.io/doc-api/index-rw.html
        show_difference: bool
            If set to True a verbose description of the updates will be returned to the user.
        """
        red_color = fg('#FF0000')
        green_color = fg('#00FF00')
        res = attr('reset')
        if not token:
            raise ValueError(f'[token=None] Resource Watch API TOKEN required for updates.')
        update_blacklist = ['metadata','layer', 'vocabulary', 'updatedAt', 'userId', 'slug', "clonedHost", "errorMessage", "taskId", "dataLastUpdated"]
        attributes = {f'{k}':v for k,v in self.attributes.items() if k not in update_blacklist}
        if not update_params:
            payload = { **attributes }
        else:
            payload = { f'{key}': update_params[key] for key in update_params if key in list(attributes.keys()) }
        try:
            url = f"{self.server}/dataset/{self.id}"
            headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
            r = requests.patch(url, data=json.dumps(payload), headers=headers)
        except:
            raise ValueError(f'Dataset update failed.')
        if r.status_code == 200:
            response = r.json()['data']
        else:
            pass
            return None
        if show_difference:
            old_attributes = { f'{k}': attributes[k] for k,v in payload.items() }
            print(f"Attributes to change:")
            print(red_color + old_attributes + res)
            print(green_color + 'Updated!'+ res)
            print({ f'{k}': v for k, v in response['attributes'].items() if k in payload })
        self.attributes = self.get_dataset()
        return self

    def confirm_delete(self):
        print(f"Delete Dataset {self.attributes['name']} with id={self.id}?")
        print("Note: Dataset deletion cascades to all associated Layers, Metadata and Vocabularies.\n> y/n")
        conf = input()
        if conf.lower() == 'y':
            return True
        elif conf.lower() == 'n':
            return False
        else:
            print('Requires y/n input!')
            return False

    def delete(self, token=None, force=False):
        """
        Deletes a target Dataset object.
        """
        if not token:
            raise ValueError(f'[token] Resource Watch API token required to delete.')
        layer_count = len(self.layers)
        if layer_count > 0:
            print(f'WARNING - Dataset has {layer_count} associated Layer(s).')
            print('[D]elete ALL associated Layers, or\n[A]bort delete process?')
            conf = input()
            if conf.lower() == 'd':
                for l in self.layers:
                    l.delete(token, force=True)
            elif conf.lower() == 'a':
                return False
            else:
                print('Requires D/A input!')
                return False
        if not force:
            conf = self.confirm_delete()
        elif force:
            conf = True
        if conf:
            try:
                url = f'{self.server}/dataset/{self.id}'
                headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
                r = requests.delete(url, headers=headers)
            except:
                raise ValueError(f'Layer deletion failed.')
            if r.status_code == 200:
                print(r.url)
                print('Deletion successful!')
                self = None
        else:
            print('Deletion aborted.')
        return self

    def clone(self, token=None, env='staging', dataset_params=None, target_dataset_id=None):
        """
        Create a clone of a target Dataset as a new staging or prod Dataset.
        A set of attributes can be specified for the clone Dataset.
        """
        if not token:
            raise ValueError(f'[token] Resource Watch API token required to clone.')
        if not target_dataset_id:
            print('Must specify target_dataset_id.')
            return None
        else:
            target_dataset = Dataset(target_dataset_id)
            name = dataset_params.get('name', target_dataset.attributes['name'] + 'CLONE')
            clone_dataset_attr = {**target_dataset.attributes, 'name': name}
            for k,v in clone_dataset_attr.items():
                if k in dataset_params:
                    clone_dataset_attr[k] = dataset_params[k]
                clone_dataset_attr = {**target_dataset.attributes, 'name': name}
                payload = {
                    'application': clone_dataset_attr['application'],
                    'connectorType': clone_dataset_attr['connectorType'],
                    'connectorUrl': clone_dataset_attr['connectorUrl'],
                    'tableName': clone_dataset_attr['tableName'],
                    'provider': clone_dataset_attr['provider'],
                    'env': clone_dataset_attr['env'],
                    'name': clone_dataset_attr['name']
                }
                print(f'Creating clone dataset')
                url = f'{self.server}/dataset'
                headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
                r = requests.post(url, data=json.dumps(payload), headers=headers)
                if r.status_code == 200:
                    clone_dataset_id = r.json()['data']['id']
                else:
                    print(r.status_code)
                    return None
                print(f'{self.server}/v1/dataset/{clone_dataset_id}')
                self.attributes = Dataset(clone_dataset_id).attributes
                return Dataset(clone_dataset_id)

    def intersect(self, geometry):
        """
        Intersect an EE raster with a geometry

        Given a valid LMIPy.Geometry object, return a dictionary based on reduceRegion
        Parameters
        ---------
        geometry: Geometry
            An LMIPy.Geometry object
        server: str
            A string of a server to call to.
        """
        if self.attributes.get('provider') != 'gee':
            raise ValueError("Intersect currently only supported for EE raster data")
        url = f"{self.server}/query/{self.id}"
        sql = f"SELECT ST_SUMMARYSTATS() from {self.attributes.get('tableName')}"
        params = {"sql": sql,
                  "geostore": geometry.id}
        r = requests.get(url, params=params)
        if r.status_code == 200:
            try:
                return r.json().get('data', None)[0].get('st_summarystats')
            except:
                raise ValueError(f'Unable to retrieve values from response {r.json()}')
        else:
            print("Hint: sometimes this service fails due to load on EE servers. Try again.")
            raise ValueError(f'Bad response: {r.status_code} from query: {r.url}')

    def save(self, path=None):
        """
        Construct dataset json and save to local path in a date-referenced folder
        """
        if not path:
            path = './LMI-BACKUP'
            if not os.path.isdir(path):
                os.mkdir(path)
            today = datetime.datetime.today().strftime('%Y-%m-%d@%Hh-%Mm')
            path += f'/{today}'
            if not os.path.isdir(path):
                os.mkdir(path)
        else:
           if not os.path.isdir(path):
                os.mkdir(path)

        save_json = {
            "id": self.id,
            "type": "dataset",
            "attributes": {
                **self.attributes,
                'layer': [{
                    "id": layer.id,
                    "type": "layer",
                    "attributes": layer.attributes
                    } for layer in self.layers],
                'metadata': [{
                    "id": m.id,
                    "type": "metadata",
                    "attributes": m.attributes
                    } for m in self.metadata],
                'vocabulary': [{
                    "id": v.id,
                    "type": "vocabulary",
                    "attributes": v.attributes
                    } for v in self.vocabulary]
                },
        }

        if not os.path.isdir(path):
            os.mkdir(path)

        with open(f"{path}/{self.id}.json", 'w') as fp:
            json.dump(save_json, fp)

    def load(self, path=None, check=True):
        """
        From a local backup at the specified path, loads and returns a previous version of the current dataset.
        """
        if not path:
            print('Requires a file path to valid backup folder.')
            return None
        try:
            with open(f"{path}/{self.id}.json") as f:
                recovered_dataset = json.load(f)
            if check:
                blacklist = ['metadata','layer', 'vocabulary', 'updatedAt']
                attributes = {f'{k}':v for k,v in recovered_dataset['attributes'].items() if k not in blacklist}
                difs = {f'{k}': [v, self.attributes[k]] for k,v in attributes.items() if k not in blacklist and self.attributes[k] != attributes[k]}
                if check and self.attributes == attributes:
                    print('Loaded attributes == existing attributes')
                elif check and self.attributes == attributes:
                    print('Loaded attributes != existing attributes')
                    pprint(difs)
        except:
            raise ValueError(f'Failed to load backup from f{path}/{self.id}.json')
        return Dataset(id_hash=recovered_dataset['id'], attributes=recovered_dataset['attributes'])

    def add_vocabulary(self, vocab_params=None, token=None):
        """
        Create a new vocabulary association to the current dataset.

        A single application string, name string and tags list must be specified within the `vocab_params` dictionary.

        A RW-API token is required.
        """
        if not token:
            raise ValueError(f'[token] Resource Watch API token required to create new vocabulary.')
        vocab_type = vocab_params.get('name', None)
        vocab_tags = vocab_params.get('tags', None)
        app = vocab_params.get('application', None)
        ds_id = self.id
        if vocab_tags and len(vocab_tags) > 0 and vocab_type and app:
            payload = { 
                "tags": vocab_tags,
                "application": app
            }
            try:
                url = f'https://api.resourcewatch.org/v1/dataset/{ds_id}/vocabulary/{vocab_type}'
                headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
                r = requests.post(url, data=json.dumps(payload), headers=headers)
            except:
                raise ValueError(f'Vocabulary creation failed.')
            if r.status_code == 200:
                print(f'Vocabulary {vocab_type} created.')
                self.attributes = self.get_dataset()
                return self
            else:
                print(f'Failed with error code {r.status_code}')
                return None
        else:
            raise ValueError(f'Vocabulary creation requires: application string, name string, and a list of tags.')

    def add_metadata(self, meta_params=None, token=None):
        """
        Create a new metadata association to the current dataset.

        A single application string and language string ('en' by default) must be specified within the
        `meta_params` dictionary, as well as an (optional) info dictionary.
        Info has a free schema.

        A RW-API token is required.
        """
        if not token:
            raise ValueError(f'[token] Resource Watch API token required to create new vocabulary.')
        info = meta_params.get('info', None)
        app = meta_params.get('application', None)
        ds_id = self.id
        if info and app:
            payload = { 
                "info": info,
                "application": app,
                "language": meta_params.get('language', 'en')
            }
            try:
                url = f'https://api.resourcewatch.org/v1/dataset/{ds_id}/metadata'
                headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
                r = requests.post(url, data=json.dumps(payload), headers=headers)
            except:
                raise ValueError(f'Vocabulary creation failed.')
            if r.status_code == 200:
                print(f'Metadata created.')
                self.attributes = self.get_dataset()
                return self
            else:
                print(f'Failed with error code {r.status_code}')
                return None
        else:
            raise ValueError(f'Metadata creation requires an info object and application string.')

