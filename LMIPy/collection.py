import requests
import random
import os
import json
import datetime
from tqdm import tqdm
from .dataset import Dataset
from .table import Table
from .layer import Layer
from .utils import html_box, create_class, show, flatten_list, parse_filters, server_uses_widgets

class Collection:
    """
    Returns a list of objects from a server

    This function searches all avaiable layers or dataset entries within user specified limits and returns a list.
    of objects.

    Parameters
    ----------
    app: list
        A list of string IDs of applications to search, e.g. [‘gfw’, ‘rw’]
    limit: int
        Maximum number of items to return
    order: str
        Field to order items by, e.g. ’date’
    sort: str
        Rule to sort items by, either ascending (’asc’) or descending ('desc')
    search: str
        String to search records by, e.g. ’Forest loss’
    object_type: list
        A list of strings of object types to search, e.g. [‘dataset’, ‘layer’]
    filters: dict
        A dictionary of filter key, value pairs e.g. {'provider', 'gee'}
        Possible search keys: 'connectorType', 'provider', 'status', 'published', 'protected', 'geoInfo'.
    """
    def __init__(self, id_hash=None, attributes=None, search=None, app=['gfw','rw'], env='production', limit=1000, order='name', sort='desc',
                 object_type=['dataset', 'layer','table', 'widget'], server='https://api.resourcewatch.org',
                 filters=None, mapbox_token=None, token=None):
        self.search = search
        self.type = 'Collection'
        self.search_terms = [search.lower()] + search.lower().strip().split(' ') if search else ''
        self.server = server
        self.app = ",".join(app)
        self.env = env
        self.id_hash = id_hash
        self.limit = limit
        self.order = order
        self.sort = sort
        self.filters = filters
        self.mapbox_token = mapbox_token
        self.object_type = object_type

        if not attributes:
            self.attributes = self.get_collection(token=token)
        elif attributes and token:
            created_collection = self.new_collection(token=token, attributes=attributes)
            self.attributes = created_collection.attributes
            self.id = created_collection.id
        
        self.id = id_hash
        self.iter_position = 0

    def _repr_html_(self):
        str_html = ""
        for n, c in enumerate(self.attributes['resources']):
            str_html += show(c, n)
            if n < len(self.attributes['resources'])-1:
                str_html += '<p></p>'
        return str_html

    def __repr__(self):
        rep_string = "["
        for n, c in enumerate(self.attributes['resources']):
            rep_string += str(f"{n}. {c['type']} {c['id']} {c['attributes'].get('name', '')}")
            if n < len(self.attributes['resources'])-1:
                rep_string += ',\n '
        return rep_string

    def __str__(self):
        return f"Collection {self.id} {self.attributes['name']}"

    def __iter__(self):
        return self

    def __next__(self):
        if self.iter_position >= len(self.attributes['resources']):
            self.iter_position = 0
            raise StopIteration
        else:
            self.iter_position += 1
            return self.attributes['resources'][self.iter_position - 1]

    def __getitem__(self, key):
        items = self.attributes['resources'][key]
        if type(items) == list:
            return [create_class(item) for item in items]
        else:
            return create_class(items)

    def __len__(self):
        return len(self.attributes['resources'])

    def get_collection(self, token=None):
        """
        Getter for the a collection object. In this case dataset and layers
        are the objects in the API. I.e. tables are a dataset type.
        """
        if self.id_hash and token and self.search is None:
            try:
                url = f'{self.server}/v1/collection/{self.id_hash}'
                headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
                r = requests.get(url, headers=headers, timeout=10)
                col = r.json().get('data', {})
                if not col:
                    raise ValueError('No collection found')
            except:
                raise ValueError(f'Unable to get collection {self.id_hash} from {self.server}')

            resources = col.get('attributes', {}).get('resources', [])
            name = col.get('attributes', {}).get('name', '')
            owner = col.get('attributes', {}).get('ownerId', None)
            app = col.get('attributes', {}).get('application', None)
            entities = [{'type': item.get('type').title() , 'id': item.get('id'), 'attributes': {}, 'server': self.server} for item in resources]
            return {
                'resources': entities,
                'name': name,
                'application': app,
                'ownerId': owner

            }

        datasets = self.get_entities()
        layers = []
        layers = flatten_list([d.get('attributes').get('layer') for d in datasets])
        if server_uses_widgets(server=self.server):
            widgets = flatten_list([d.get('attributes').get('widget') for d in datasets])
        else:
            widgets = None
        
        response_list = []

        if 'layer' in self.object_type:
            _ = [response_list.append(l) for l in layers]
        if 'dataset' in self.object_type or 'table' in self.object_type:
            _ = [response_list.append(d) for d in datasets]
        if 'widget' in self.object_type:
            _ = [response_list.append(w) for w in widgets]

        filtered_list = self.filter_results(response_list)
        ordered_list = self.order_results(filtered_list)

        return {
            'resources': ordered_list,
            'name': f"Custom Search: '{self.search}'",
            'application': None,
            'ownerId': None
        }

    def get_entities(self):
        hash = random.getrandbits(16)
        filter_string = parse_filters(self.filters)
        if server_uses_widgets(server=self.server):
            url = (f'{self.server}/v1/dataset?app={self.app}&env={self.env}&{filter_string}'
                   f'includes=layer,vocabulary,metadata,widget&page[size]=1000&hash={hash}')
        else:
            url = (f'{self.server}/v1/dataset?app={self.app}&env={self.env}&{filter_string}'
                   f'includes=layer,metadata&page[size]=1000&hash={hash}')
        r = requests.get(url)
        response_list = r.json().get('data', None)
        if not response_list:
            raise ValueError('No items found')
        return response_list

    def filter_results(self, response_list):
        """Search by a list of strings to return a filtered list of Dataset or Layer objects"""
        filtered_response = []
        collection = []
        for item in response_list:
            return_layers = 'layer' in self.object_type
            return_datasets = 'dataset' in self.object_type
            return_tables = 'dataset' in self.object_type
            return_widgets = 'widget' in self.object_type
            #print(f"Filter: {type(item)}, {item}")
            if type(item) == dict:
                tmp_atts = item.get('attributes')
                name = tmp_atts.get('name', None)
                description = tmp_atts.get('description', None)
                slug = tmp_atts.get('slug', None)
            else:
                name = None
                description = None
                slug = None
            found = []
            if description:
                description = description.lower()
                found.append(any([s in description for s in self.search_terms]))
            if name:
                name = name.lower()
                found.append(any([s in name for s in self.search_terms]))
            if slug:
                slug = slug.lower().split('_')
                found.append(any([s in slug for s in self.search_terms]))
            if any(found):
                if len(filtered_response) < self.limit:
                    filtered_response.append(item)
                if item.get('type') == 'dataset' and item.get('attributes').get('provider') in ['csv', 'json'] and return_tables:
                    collection.append({'type': 'Table','id': item.get('id'), 'attributes': item.get('attributes'), 'server': self.server})
                elif item.get('type') == 'dataset' and item.get('attributes').get('provider') != ['csv','json'] and return_datasets:
                    collection.append({'type': 'Dataset','id': item.get('id'), 'attributes': item.get('attributes'), 'server': self.server})
                if item.get('type') == 'layer' and return_layers:
                    collection.append({'type': 'Layer', 'id': item.get('id'), 'attributes': item.get('attributes'), 'server': self.server, 'mapbox_token':self.mapbox_token})
                if item.get('type') == 'widget' and return_widgets:
                    collection.append({'type': 'Widget', 'id': item.get('id'), 'attributes': item.get('attributes'), 'server': self.server})
        return collection

    def order_results(self, collection_list):
        """Operate on a list of objects given the order key, limit, and rule a user has passed"""
        tmp_sorted = []
        try:
            d = {}
            duplicate = {}
            for n, z in enumerate([c['attributes'].get(self.order.lower()) for c in collection_list]):
                if duplicate.get(z, None):
                    d[f'{z} {duplicate[z]}'] = collection_list[n]
                    duplicate[z] += 1
                else:
                    d[z] = collection_list[n]
                    duplicate[z] = 1
            keys = sorted(d, reverse=self.sort.lower() == 'asc')
            for key in keys:
                tmp_sorted.append(d[key])
        except:
            raise ValueError(f'[Order-error] Param does not exist in collection: {self.order}, rule: {self.sort}')
        if self.limit < len(tmp_sorted):
            tmp_sorted = tmp_sorted[0:self.limit]
        return tmp_sorted

    def new_collection(self, token=None, attributes={}):
        name = attributes.get('name', None)
        app = attributes.get('application', None)
        if not token:
            raise ValueError(f'[token] API token required to create new collection.')
        elif not (name and app):
            raise ValueError(f'[name] and [application] strings required in attributes to create new collection.')

        entities = []
        if  attributes.get('resources', []):
            entities = [{
                'type': item['type'] if item and type(item) == dict else item.type.lower(),
                'id': item['id'] if item and type(item) == dict else item.id
            } for item in attributes['resources']]

        payload = {
            'name': str(name),
            'application': str(app),
            'resources': entities
        }

        try:
            url = (f'{self.server}/v1/collection/')
            headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
            r = requests.post(url, data=json.dumps(payload), headers=headers)
            if r.status_code == 200:
                new_col_id = r.json()['data']['id']
            else:
                print(r.status_code)
                return None
            print(f'{self.server}/v1/collection/{new_col_id}')
            return Collection(id_hash=new_col_id, token=token)
        except:
            raise ValueError(f'Unable to create collection.')

    def confirm_delete(self):
        print(f"Delete Collection {self.attributes['name']} with id={self.id}?\n> y/n")
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
        Deletes a target Collection (does not delete collection objects)
        """
        if not token:
            raise ValueError(f'[token=None] API token required to delete.')
        if not force:
            conf = self.confirm_delete()
        elif force:
            conf = True
        if conf:
            try:
                url = f'{self.server}/collection/{self.id}'
                headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
                r = requests.delete(url, headers=headers)
            except:
                raise ValueError(f'Layer deletion failed.')
            if r.status_code == 200:
                print(r.url)
                print('Deletion successful!')
                self = None
        else:
            print('Deletion aborted')
        return None

    def update(self, token=None, update_params={}):
        """Update the name of a collection"""
        if not token:
            raise ValueError(f'[token] API token required to create new collection.')
        elif not update_params or 'name' not in update_params.keys():
            raise ValueError(f'[update_params] must specify name in update parameters.')

        payload = {}

        if update_params.get('name',None): payload['name'] = update_params['name']

        try:
            url = (f'{self.server}/v1/collection/{self.id}')
            headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
            r = requests.patch(url, data=json.dumps(payload), headers=headers)
            col = r.json().get('data', {})
            if r.status_code == 200:
                print(f"Collection {col['id']} updated.")
            else:
                print(f'Failed with error code {r.status_code}')
        except:
            raise ValueError(f'Unable to update collection.')

        self.attributes = self.get_collection(token=token)
        return self

    def add_resources(self, token=None, resources=[]):
        """
        Adds new resources to an existing Collection.
        Resources must be a list of valid LMIPy objects (Layer, Dataset, Table, or Widget)
        Requires token.
        """
        if not token:
            raise ValueError(f'[token] API token required to add resources to collection.')
        elif not resources:
            raise ValueError(f'[resources] list required to add resources to update collection.')

        valid_resources = {
            "<class 'LMIPy.layer.Layer'>": "layer",
            "<class 'LMIPy.dataset.Dataset'>": "dataset",
            "<class 'LMIPy.table.Table'>": "dataset",
            "<class 'LMIPy.lmipy.Widget'>": "widget"
        }
        
        if not all([str(type(item)) in valid_resources.keys() for item in resources]):
            raise ValueError(f'[resources] list must contain valid LMIPy Layer, Dataset, Table, or Widget objects')

        payloads = [
            {
                'type': valid_resources[str(type(item))],
                'id': item.id
            } for item in resources
        ]

        for payload in payloads:
            try:
                url = f'{self.server}/v1/collection/{self.id}/resource'
                headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
                r = requests.post(url, data=json.dumps(payload), headers=headers)
                if r.status_code == 200:
                    print(f"{payload['type'].title()} {payload['id']} added to Collection {self.id}.")
                else:
                    print(f'Failed with error code {r.status_code}')
            except:
                raise ValueError(f'Unable to add resources to collection.')

        self.attributes = self.get_collection(token=token)
        return self
        
    def remove_resources(self, token=None, resources=[]):
        """
        Removes new resources from a existing Collection.
        Resources must be a list of valid LMIPy objects (Layer, Dataset, Table, or Widget)
        Requires token.
        """
        if not token:
            raise ValueError(f'[token] API token required to add resources to collection.')
        elif not resources:
            raise ValueError(f'[resources] list required to add resources to update collection.')

        valid_resources = {
            "<class 'LMIPy.layer.Layer'>": "layer",
            "<class 'LMIPy.dataset.Dataset'>": "dataset",
            "<class 'LMIPy.table.Table'>": "dataset",
            "<class 'LMIPy.lmipy.Widget'>": "widget"
        }
        
        if not all([str(type(item)) in valid_resources.keys() for item in resources]):
            raise ValueError(f'[resources] list must contain valid LMIPy Layer, Dataset, Table, or Widget objects')

        payloads = [
            {
                'type': valid_resources[str(type(item))],
                'id': item.id
            } for item in resources
        ]

        for payload in payloads:
            try:
                url = f"{self.server}/v1/collection/{self.id}/resource/{payload['type']}/{payload['id']}"
                headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
                r = requests.delete(url, headers=headers)
                if r.status_code == 200:
                    print(f"{payload['type'].title()} {payload['id']} removed from Collection {self.id}.")
                else:
                    print(f'Failed with error code {r.status_code}')
            except:
                raise ValueError(f'Unable to remove resources from collection.')

        self.attributes = self.get_collection(token=token)
        return self

    def save(self, path=None):
        """
        Save all entities in the collection to a local path.
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
        print(f'Saving to path: {path}')
        saved = []
        failed = []
        if server_uses_widgets(self.server):
            url_args = "vocabulary,metadata,layer,widget"
        else:
            url_args = "metadata,layer"
        for item in tqdm(self):
            if item['id'] not in saved:
                entity_type = item.get('type')
                if entity_type in ['Dataset', 'Table']:
                    ds_id = item['id']
                else:
                    ds_id = item['attributes']['dataset']
                try:
                    url = f'{self.server}/v1/dataset/{ds_id}?includes={url_args}'
                    r = requests.get(url)
                    dataset_config = r.json()['data']
                except:
                    failed.append(item)

                save_json = {
                    "id": ds_id,
                    "type": "dataset",
                    "server": self.server,
                    "attributes": dataset_config['attributes']
                }
                with open(f"{path}/{ds_id}.json", 'w') as fp:
                    json.dump(save_json, fp)

        if len(failed) > 0:
            print(f'Some entities failed to save: {failed}')
            return failed
        print('Save complete!')
