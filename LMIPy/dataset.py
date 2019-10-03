import requests
import json
import random
import geopandas as gpd
import os
import datetime
#from shapely.geometry import shape
from pprint import pprint
from .layer import Layer
from .utils import html_box, nested_set
from .lmipy import Vocabulary, Metadata, Widget


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
    def __init__(self, id_hash=None, attributes=None, server='https://api.resourcewatch.org', token=None):
        self.id = id_hash
        self.layers = []
        self.server = server
        if not attributes:
            self.attributes = self.get_dataset()
        elif attributes and token:   
            created_dataset = self.new_dataset(token=token, attributes=attributes, server=server)
            self.attributes = created_dataset.attributes
            self.id = created_dataset.id
        elif attributes:
            self.id = attributes.get('id')
            self.attributes = self.get_dataset()

        if len(self.attributes.get('layer', [])) > 0:
            self.layers = [Layer(id_hash=l.get('id', None), attributes=l, server=self.server) for l in self.attributes.get('layer')]
            _ = self.attributes.pop('layer')
        if len(self.attributes.get('metadata', [])) > 0:
            self.metadata = [Metadata(attributes=m, server=self.server) for m in self.attributes.get('metadata')]
            _ = self.attributes.pop('metadata')
        else:
            self.metadata = []
        if len(self.attributes.get('vocabulary', [])) > 0:
            self.vocabulary =[Vocabulary(attributes=v, server=self.server) for v in self.attributes.get('vocabulary')]
            _ = self.attributes.pop('vocabulary')
        else:
            self.vocabulary = []
        if len(self.attributes.get('widget', [])) > 0:
            self.widget =[Widget(w.get('id'), attributes=1, server=self.server) for w in self.attributes.get('widget')]
            _ = self.attributes.pop('widget')
        else:
            self.widget = []
        self.url = f"{self.server}/v1/dataset/{id_hash}?hash={random.getrandbits(16)}"

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Dataset {self.id} {self.attributes['name']}"

    def _repr_html_(self):
        return html_box(item=self)

    def get_dataset(self):
        """
        Retrieve a dataset from a server by ID.
        """
        try:
            hash = random.getrandbits(16)
            url = (f'{self.server}/v1/dataset/{self.id}?includes=layer,widget,vocabulary,metadata&hash={hash}')
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
        if not token:
            raise ValueError(f'[token=None] Resource Watch API TOKEN required for updates.')
        update_blacklist = ['metadata','layer', 'vocabulary', 'updatedAt', 'userId', 'slug', "clonedHost", "errorMessage", "taskId", "dataLastUpdated"]
        attributes = {f'{k}':v for k,v in self.attributes.items() if k not in update_blacklist}
        if not update_params:
            raise ValueError(f'[update_params=None] Must specify update parameters.')
        else:
            payload = {}
            for k, v in update_params.items():
                if '.' in k:
                    nested_keys = k.split('.')
                    if len(nested_keys) > 1 and nested_keys[0] in list(attributes.keys()):
                        payload[nested_keys[0]] = attributes.get(nested_keys[0])
                        nested_set(payload, nested_keys, v)
                elif k in list(attributes.keys()):
                    payload[k] = v
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
            if not force:
                print(f'WARNING - Dataset has {layer_count} associated Layer(s).')
                print('[D]elete ALL associated Layers, or\n[A]bort delete process?')
                conf = input()
            else:
                conf = 'd'
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
                raise ValueError(f'Dataset deletion failed.')
            if r.status_code == 200:
                print(r.url)
                print('Deletion successful!')
                self = None
            else:
                raise ValueError(f'Dataset deletion unsuccessful. {r.status_code}')
        else:
            print('Deletion aborted.')
        return self

    def clone(self, token=None, env='staging', clone_server=None, dataset_params=None, clone_children=False):
        """
        Create a clone of a target Dataset as a new staging or prod Dataset.
        A set of attributes can be specified for the clone Dataset.

        The argument `clone_server` specifies the server to clone to. Default server = https://api.resourcewatch.org

        Set clone_children=True to clone all child layers, and widgets.
        """
        if not clone_server: clone_server = self.server
        if not token:
            raise ValueError(f'[token] Resource Watch API token required to clone.')
        else:
            name = dataset_params.get('name', self.attributes['name'] + 'CLONE')
            clone_dataset_attr = {**self.attributes, 'name': name}
            for k,v in clone_dataset_attr.items():
                if k in dataset_params:
                    clone_dataset_attr[k] = dataset_params.get(k, '')
            payload = {
                'dataset': {
                    'application': clone_dataset_attr['application'],
                    'connectorType': clone_dataset_attr['connectorType'],
                    'connectorUrl': clone_dataset_attr['connectorUrl'],
                    'tableName': clone_dataset_attr['tableName'],
                    'provider': clone_dataset_attr['provider'],
                    'published': clone_dataset_attr['published'],
                    'env': clone_dataset_attr['env'],
                    'name': clone_dataset_attr['name']
                }
            }
            print(f'Creating clone dataset')
            url = f'{clone_server}/dataset'
            headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
            r = requests.post(url, data=json.dumps(payload), headers=headers)
            if r.status_code == 200:
                clone_dataset_id = r.json()['data']['id'] 
                clone_dataset = Dataset(id_hash=clone_dataset_id, server=clone_server)
            else:
                print(r.status_code)
                return None
            print(f'{clone_server}/v1/dataset/{clone_dataset_id}')
            if clone_children:
                layers =  self.layers
                if len(layers) > 0:
                    for l in layers:
                        try:
                            layer_name = l.attributes['name']
                            
                            l.clone(token=token, env=env, layer_params={'name': layer_name}, clone_server=clone_server, target_dataset_id=clone_dataset_id)
                        except:
                            raise ValueError(f'Layer cloning failed for {l.id}')
                else:
                    print("No child layers to clone!")
                widgets =  self.widget 
                if len(widgets) > 0:
                    for w in widgets:
                        widget = w.attributes
                        widget_payload = {
                            "name": widget['name'],
                            "description": widget.get('description', None),
                            "env": payload['dataset']['env'],
                            "widgetConfig": widget['widgetConfig'],
                            "application": payload['dataset']['application']
                        }
                        try:
                            clone_dataset.add_widget(token=token, widget_params=widget_payload)
                        except:
                            raise ValueError(f'Widget cloning failed for {widget.id}')
                else:
                    print("No child widgets to clone!")
                vocabs = self.vocabulary
                if len(vocabs) > 0:
                    for v in vocabs:
                        vocab = v.attributes
                        vocab_payload = {
                            'application': vocab['application'],
                            'name': vocab['name'],
                            'tags': vocab['tags']
                        }
                        try:
                            clone_dataset.add_vocabulary(vocab_params=vocab_payload, token=token)
                        except:
                            raise ValueError('Failed to clone Vocabulary.')
                metas = self.metadata
                if len(metas) > 0:
                    for m in metas:
                        meta = m.attributes
                        meta_payload = {
                            'application': meta['application'],
                            'info': meta['info'],
                            'language': meta['language']
                        }
                        try:
                            clone_dataset.add_metadata(meta_params=meta_payload, token=token)
                        except:
                            raise ValueError('Failed to clone Metadata.')
            # self.attributes = Dataset(clone_dataset_id, server=clone_server).attributes
            return Dataset(id_hash=clone_dataset_id, server=clone_server)


    def intersect(self, geometry):
        """
        EXPERIMENTAL FEATURE
        
        Intersect an EE raster with a geometry

        Given a valid LMIPy.Geometry object, return a dictionary based on reduceRegion.
        
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
                return r.json().get('data', [{}])[0].get('st_summarystats', None)
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

        try:
            url = f'{self.server}/v1/dataset/{self.id}?includes=vocabulary,metadata,layer,widget'
            r = requests.get(url)
            dataset_config = r.json()['data']
        except:
            raise ValueError(f'Could not retrieve config.')
        
        save_json = {
            "id": self.id,
            "type": "dataset",
            "server": self.server,
            "attributes": dataset_config['attributes']
        }
        if not os.path.isdir(path):
            os.mkdir(path)
        with open(f"{path}/{self.id}.json", 'w') as fp:
            json.dump(save_json, fp)
        print('Save complete!')
        

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
            server = recovered_dataset.get('server', 'https://api.resourcewatch.org')
            if check:
                blacklist = ['metadata','layer','widget','vocabulary', 'updatedAt']
                attributes = {f'{k}':v for k,v in recovered_dataset['attributes'].items() if k not in blacklist}
                difs = {f'{k}': [v, self.attributes[k]] for k,v in attributes.items() if k not in blacklist and self.attributes[k] != attributes[k]}
                if check and self.attributes == attributes:
                    print('Loaded attributes == existing attributes')
                elif check and self.attributes == attributes:
                    print('Loaded attributes != existing attributes')
                    pprint(difs)
        except:
            raise ValueError(f'Failed to load backup from f{path}/{self.id}.json')
        return Dataset(attributes={**recovered_dataset['attributes'], 'id': recovered_dataset['id']}, server=server)

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
                url = f'{self.server}/v1/dataset/{ds_id}/vocabulary/{vocab_type}'
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
                url = f'{self.server}/v1/dataset/{ds_id}/metadata'
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

    def add_widget(self, widget_params=None, token=None):
        """
        Create a new widget association to the current dataset.

        A application list, name and widgetConfig must be specified within the
        `widget_params` dictionary.
        The widgetConfig key has a free schema.

        A RW-API token is required.
        """
        if not token:
            raise ValueError(f'[token] Resource Watch API token required to create new widget.')
        name = widget_params.get('name', None)
        description = widget_params.get('description', None)
        widget_config = widget_params.get('widgetConfig', None)
        app = widget_params.get('application', None)
        ds_id = self.id
        if name and widget_config and app:
            payload = {
                "name": name,
                "description": description,
                "widgetConfig": widget_config,
                "application": app
            }
            try:
                url = f'{self.server}/v1/dataset/{ds_id}/widget'
                print(url)
                headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
                r = requests.post(url, data=json.dumps(payload), headers=headers)
                print(r.json())
            except:
                raise ValueError(f'Widget creation failed.')
            if r.status_code == 200:
                print(f'Widget created.')
                self.attributes = self.get_dataset()
                return self
            else:
                print(f'Failed with error code {r.status_code}')
                return None
        else:
            raise ValueError(f'Widget creation requires name string, application list and a widgetConfig object.')

    def new_dataset(self, token=None, attributes=None, server='https://api.resourcewatch.org'):
        """
        Create a new staging or prod Dataset entity from attributes.
        """
        if not token:
            raise ValueError(f'[token] Resource Watch API token required to create a new dataset.')
        elif not attributes:
            raise ValueError(f'Attributes required to create a new dataset.')
        else:
            url = f'{server}/dataset'
            headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
            payload = {'dataset': attributes}

            r = requests.post(url, data=json.dumps(payload), headers=headers)
            if r.status_code == 200:
                new_dataset_id = r.json()['data']['id']
            else:
                print(r.status_code)
                return None
            print(f'{self.server}/v1/dataset/{new_dataset_id}')
            return Dataset(id_hash=new_dataset_id, server=server)
            
    def merge(self, token=None, target_dataset=None, target_dataset_id=None, target_server='https://api.resourcewatch.org', key_whitelist=[], force=False):
        """
        'Merge' one Dataset entity into another target Dataset.
        The argument `key_whitelist` can be used to specify which properties you wish to merge (if not all)
        Note: requires API token.
        """
        if not token:
            raise ValueError(f'[token] Resource Watch API token required to update Dataset.')
        if not target_dataset and target_dataset_id and target_server:
            target_dataset = Dataset(target_dataset_id, server=target_server)
        else:
            raise ValueError(f'Requires either target Dataset or Dataset id plus server.')
        atts = self.attributes
        payload = {
            'connectorType': atts.get('connectorType', None),
            'connectorUrl': atts.get('connectorUrl', None),
            'tableName': atts.get('tableName', None),
            'name': atts.get('name', None),
            'description': atts.get('description', None),
            'application': atts.get('application', None),
            'provider': atts.get('provider', None)
        }
        if not key_whitelist: key_whitelist = [k for k in payload.keys()]
        filtered_payload = {k:v for k,v in payload.items() if v and k in key_whitelist}
        print(f'Merging {self.id} from {self.server} into {target_dataset_id} on {target_server}.\nAre you sure you sure you want to continue?')
        if not force:
            conf = input()
        else:
            conf = 'y'
        if conf.lower() == 'y':
            try:
                merged_dataset = target_dataset.update(update_params=filtered_payload, token=token)
            except:
                print('Aborting...')
            print('Completed!')
            return merged_dataset

        elif conf.lower() == 'n':
            print('Aborting...')
            return False
        else:
            print('Requires y/n input!')
            return False
