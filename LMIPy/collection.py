import requests
import random
import os
import datetime
from tqdm import tqdm
from .dataset import Dataset
from .table import Table
from .layer import Layer

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
    """
    def __init__(self, search='', app=['gfw','rw'], env='production', limit=1000, order='name', sort='desc',
                 object_type=['dataset', 'layer','table'], server='https://api.resourcewatch.org',
                 mapbox_token=None):
        self.search = search.lower().strip().split(' ')
        self.server = server
        self.app = ",".join(app)
        self.env = env
        self.limit = limit
        self.order = order
        self.sort = sort
        self.mapbox_token = mapbox_token
        self.object_type = object_type
        self.collection = self.get_collection()
        self.iter_position = 0

    def __repr__(self):
        rep_string = "["
        for n, c in enumerate(self.collection):
            rep_string += str(c)
            if n < len(self.collection)-1:
                rep_string += ', '
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
        return self.collection[key]

    def __len__(self):
        return len(self.collection)

    def get_collection(self):
        """
        Getter for the a collection object. In this case dataset and layers
        are the objects in the API. I.e. tables are a dataset type.
        """
        response_list = []
        if 'layer' in self.object_type:
            _ = [response_list.append(l) for l in self.get_layers()]
        if 'dataset' in self.object_type:
            _ = [response_list.append(d) for d in self.get_datasets()]
        ordered_list = self.order_results(response_list)
        return ordered_list

    def get_datasets(self):
        """Return all datasets and connected items within a limit and specified environment"""
        hash = random.getrandbits(16)
        url = (f'{self.server}/v1/dataset?app={self.app}&env={self.env}&'
               f'includes=layer,vocabulary,metadata&page[size]=1000&hash={hash}')
        r = requests.get(url)
        response_list = r.json().get('data', None)
        if len(response_list) < 1:
            raise ValueError('No items found')
        identified_layers = self.filter_results(response_list)
        return identified_layers

    def get_layers(self):
        """Return all layers from specified apps and environment within a limit number"""
        hash = random.getrandbits(16)
        url = (f"{self.server}/v1/layer?app={self.app}&env={self.env}"
               f"&includes=vocabulary,metadata&page[size]=1000&hash={hash}")
        r = requests.get(url)
        response_list = r.json().get('data', None)
        if len(response_list) < 1:
            raise ValueError('No items found')
        identified_layers = self.filter_results(response_list)
        return identified_layers

    def filter_results(self, response_list):
        """Search by a list of strings to return a filtered list of Dataset or Layer objects"""
        filtered_response = []
        collection = []
        for item in response_list:
            in_description = False
            in_name = False
            return_layers = 'layer' in self.object_type
            return_datasets = 'dataset' in self.object_type
            return_tables = 'dataset' in self.object_type
            name = item.get('attributes').get('name').lower()
            description = item.get('attributes').get('description')
            if description:
                description = description.lower()
                in_description = any([s in description for s in self.search])
            if name:
                in_name = any([s in name for s in self.search])
            if in_name or in_description:
                if len(filtered_response) < self.limit:
                    filtered_response.append(item)
                if item.get('type') == 'dataset' and item.get('attributes').get('provider') in ['csv', 'json'] and return_tables:
                    collection.append(Table(id_hash = item.get('id'), attributes=item.get('attributes'), server=self.server))
                elif item.get('type') == 'dataset' and item.get('attributes').get('provider') != ['csv','json'] and return_datasets:
                    collection.append(Dataset(id_hash = item.get('id'), attributes=item.get('attributes'), server=self.server))
                if item.get('type') == 'layer' and return_layers:
                    collection.append(Layer(id_hash = item.get('id'), attributes=item.get('attributes'),
                                            mapbox_token=self.mapbox_token, server=self.server))
        return collection

    def order_results(self, collection_list):
        """Operate on a list of objects given the order key, limit, and rule a user has passed"""
        tmp_sorted = []
        try:
            d = {}
            for n, z in enumerate([c.attributes.get(self.order.lower()) for c in collection_list]):
                d[z] = collection_list[n]
            keys = sorted(d, reverse=self.sort.lower() == 'asc')
            for key in keys:
                tmp_sorted.append(d[key])
        except:
            raise ValueError(f'[Order-error] Param does not exist in collection: {self.order}, rule: {self.sort}')
        if self.limit < len(tmp_sorted):
            tmp_sorted = tmp_sorted[0:self.limit]
        return tmp_sorted

    def save(self, path=None):
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
        for item in tqdm(self):
            if item.id not in saved:
                if type(item) == Layer:
                    item = item.dataset()
                elif type(item) == Dataset or type(item) == Table:
                    for layer in item.layers:
                        saved.append(layer.id)

                item.save(path)
                saved.append(item.id)
