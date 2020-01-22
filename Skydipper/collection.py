import requests
import random
import os
import json
import datetime
from tqdm import tqdm
from .dataset import Dataset
from .layer import Layer
from .utils import create_class, show, flatten_list, parse_filters, server_uses_widgets

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
    def __init__(self, search='', app=['gfw','rw'], env='production', limit=1000, order='name', sort='desc',
                 object_type=['dataset', 'layer','table', 'widget'], server="https://api.skydipper.com",
                 filters=None, mapbox_token=None):
        self.search = [search.lower()] + search.lower().strip().split(' ')
        self.server = server
        self.app = ",".join(app)
        self.env = env
        self.limit = limit
        self.order = order
        self.sort = sort
        self.filters = filters
        self.mapbox_token = mapbox_token
        self.object_type = object_type
        self.collection = self.get_collection()
        self.iter_position = 0

    def _repr_html_(self):
        str_html = ""
        for n, c in enumerate(self.collection):
            str_html += show(c, n)
            if n < len(self.collection)-1:
                str_html += '<p></p>'
        return str_html

    def __repr__(self):
        rep_string = "["
        for n, c in enumerate(self.collection):
            rep_string += str(f"{n}. {c['type']} {c['id']} {c['attributes']['name']}")
            if n < len(self.collection)-1:
                rep_string += ',\n '
        rep_string += ']'
        return rep_string

    def __iter__(self):
        return self

    def __next__(self):
        if self.iter_position >= len(self.collection):
            self.iter_position = 0
            raise StopIteration
        else:
            self.iter_position += 1
            return self.collection[self.iter_position - 1]

    def __getitem__(self, key):
        items = self.collection[key]
        if type(items) == list:
            return [create_class(item) for item in items]
        else:
            return create_class(items)

    def __len__(self):
        return len(self.collection)

    def get_collection(self):
        """
        Getter for the a collection object. In this case dataset and layers
        are the objects in the API. I.e. tables are a dataset type.
        """
        datasets = self.get_entities()
        layers = []
        for d in datasets:
            tmp_atts = d.get('attributes', None)
            layers = tmp_atts.get('layer', None)
        layers = flatten_list(layers)
        #layers = flatten_list([d.get('attributes').get('layer') for d in datasets])
        if server_uses_widgets(server=self.server):
            widgets = flatten_list([d.get('attributes').get('widget') for d in datasets])
        else:
            widgets = None
        response_list = []
        if 'layer' in self.object_type:
            _ = [response_list.append(l) for l in layers]
        if 'dataset' in self.object_type:
            _ = [response_list.append(d) for d in datasets]
        if 'widget' in self.object_type:
            _ = [response_list.append(w) for w in widgets]
        filtered_list = self.filter_results(response_list)
        ordered_list = self.order_results(filtered_list)
        return ordered_list

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
                found.append(any([s in description for s in self.search]))
            if name:
                name = name.lower()
                found.append(any([s in name for s in self.search]))
            if slug:
                slug = slug.lower().split('_')
                found.append(any([s in slug for s in self.search]))
            if any(found):
                if len(filtered_response) < self.limit:
                    filtered_response.append(item)
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
                if entity_type in ['Dataset']:
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
