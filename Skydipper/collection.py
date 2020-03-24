import requests
import random
import os
import json
import datetime
from tqdm import tqdm
from .dataset import Dataset
from .layer import Layer
from .utils import create_class, show, flatten_list, parse_filters
from .user import User
from .Skydipper import Metadata

class Collection:
    """
    Returns a list of objects from a server

    This function searches all avaiable dataset entries within user specified limits and returns a list.
    of objects.

    Parameters
    ----------
    name: str
        A string to search for
    altname: str
        An alternative name string to search for
    description: str
        A description string to search for
    citation: str
        A citation string to search for
    language: str
        A two-character language code string to search for (e.g. 'en')
    app: list
        A list of string IDs of applications to search, e.g. ['skydipper', ‘soilsRevealed’]
    limit: int
        Maximum number of items to return
    order: str
        Field to order items by, e.g. ’date’
    sort: str
        Rule to sort items by, either ascending (’asc’) or descending ('desc')
    search: str
        String to search records by, e.g. ’Forest loss’
    filters: dict
        A dictionary of filter key, value pairs e.g. {'provider', 'gee'}
        Possible search keys: 'connectorType', 'provider', 'status', 'published', 'protected', 'geoInfo'.
    """
    def __init__(self, name=None, altname=None, description=None, app=['skydipper','soilsRevealed','test'], env='production', limit=1000, order='name', sort='desc',
                server="https://api.skydipper.com", language=None, citation=None,
                 filters=None, mapbox_token=None):
        self.User = User()
        # self.search = search
        self.name = name
        self.altname = altname
        self.description = description
        self.server = server
        self.app = ",".join(app)
        self.env = env
        self.limit = limit
        self.language = language
        self.citation = citation
        self.order = order
        self.sort = sort
        self.filters = filters
        self.mapbox_token = mapbox_token
        self.object_type = ['datasett']
        self.payload = self.get_payload()
        self.metadata = self.get_metadata()
        #self.collection = self.get_collection()
        self.iter_position = 0

    def _repr_html_(self):
        str_html = ""
        for n, c in enumerate(self.metadata):
            c['server'] = self.server
            str_html += show(c, n)
            if n < len(self.metadata)-1:
                str_html += '<p></p>'
        return str_html

    def __repr__(self):
        rep_string = "["
        for n, c in enumerate(self.metadata):
            rep_string += str(f"{n}. {c.get('type')} {c.get('id')} {c.get('attributes', None).get('name', None)}")
            if n < len(self.metadata)-1:
                rep_string += ',\n '
        rep_string += ']'
        return rep_string

    def __iter__(self):
        return self

    def __next__(self):
        if self.iter_position >= len(self.metadata):
            self.iter_position = 0
            raise StopIteration
        else:
            self.iter_position += 1
            return self.metadata[self.iter_position - 1]

    def __getitem__(self, key):
        items = self.metadata[key]
        if type(items) == list:
            return [create_class(item) for item in items]
        else:
            return create_class(items)

    def __len__(self):
        return len(self.metadata)

    def get_collection(self):
        """
        Getter for the a collection object. In this case dataset and layers
        are the objects in the API. I.e. tables are a dataset type.
        """
        metadata = self.get_metadata()
        id_hashes = [item.get('attributes').get('dataset') for item in metadata if len(metadata) > 0]
        for id_hash in id_hashes:
            collection=[]
            try:
                collection.append(Dataset(id_hash=id_hash, server=self.server))
            except:
                pass
        return collection

    def get_payload(self):
        payload = {}
        if self.name: payload['name'] = self.name
        if self.altname: payload['altName'] = self.altname
        if self.description: payload['description'] = self.description
        if self.app: payload['app'] = self.app
        if self.language: payload['language'] = self.language
        if self.citation: payload['citation'] = self.citation
        return payload

    def get_metadata(self):
        url = f"{self.server}/v1/search"
        r = requests.get(url, params=self.payload, headers=self.User.headers)
        response_list = r.json().get('data', None)
        if not response_list:
            raise ValueError('No items found')
        #return [Metadata(attributes=item, server=self.server) for item in response_list]
        # in the future changing this to metadata native type is the right thing to do
        return response_list

    # def filter_results(self, response_list):
    #     """Search by a list of strings to return a filtered list of Dataset or Layer objects"""
    #     filtered_response = []
    #     collection = []
    #     for item in response_list:
    #         return_layers = 'layer' in self.object_type
    #         return_datasets = 'dataset' in self.object_type
    #         return_tables = 'dataset' in self.object_type
    #         #print(f"Filter: {type(item)}, {item}")
    #         if type(item) == dict:
    #             tmp_atts = item.get('attributes')
    #             name = tmp_atts.get('name', None)
    #             description = tmp_atts.get('description', None)
    #             slug = tmp_atts.get('slug', None)
    #         else:
    #             name = None
    #             description = None
    #             slug = None
    #         found = []
    #         if description:
    #             description = description.lower()
    #             found.append(any([s in description for s in self.search]))
    #         if name:
    #             name = name.lower()
    #             found.append(any([s in name for s in self.search]))
    #         if slug:
    #             slug = slug.lower().split('_')
    #             found.append(any([s in slug for s in self.search]))
    #         if any(found):
    #             if len(filtered_response) < self.limit:
    #                 filtered_response.append(item)
    #             elif item.get('type') == 'dataset' and item.get('attributes').get('provider') != ['csv','json'] and return_datasets:
    #                 collection.append({'type': 'Dataset','id': item.get('id'), 'attributes': item.get('attributes'), 'server': self.server})
    #             if item.get('type') == 'layer' and return_layers:
    #                 collection.append({'type': 'Layer', 'id': item.get('id'), 'attributes': item.get('attributes'), 'server': self.server, 'mapbox_token':self.mapbox_token})
    #     return collection

    # def order_results(self, collection_list):
    #     """Operate on a list of objects given the order key, limit, and rule a user has passed"""
    #     tmp_sorted = []
    #     try:
    #         d = {}
    #         duplicate = {}
    #         for n, z in enumerate([c['attributes'].get(self.order.lower()) for c in collection_list]):
    #             if duplicate.get(z, None):
    #                 d[f'{z} {duplicate[z]}'] = collection_list[n]
    #                 duplicate[z] += 1
    #             else:
    #                 d[z] = collection_list[n]
    #                 duplicate[z] = 1
    #         keys = sorted(d, reverse=self.sort.lower() == 'asc')
    #         for key in keys:
    #             tmp_sorted.append(d[key])
    #     except:
    #         raise ValueError(f'[Order-error] Param does not exist in collection: {self.order}, rule: {self.sort}')
    #     if self.limit < len(tmp_sorted):
    #         tmp_sorted = tmp_sorted[0:self.limit]
    #     return tmp_sorted

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
        for item in tqdm(self):
            if item['id'] not in saved:
                entity_type = item.get('type')
                if entity_type in ['Dataset']:
                    ds_id = item['id']
                else:
                    ds_id = item['attributes']['dataset']
                try:
                    url = f'{self.server}/v1/dataset/{ds_id}?includes=metadata,layer'
                    r = requests.get(url, headers=self.User.headers)
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
