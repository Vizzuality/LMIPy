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
    def __init__(self, id_hash=None, search=None, app=['gfw','rw'], env='production', limit=1000, order='name', sort='desc',
                 object_type=['dataset', 'layer','table', 'widget'], server='https://api.resourcewatch.org',
                 filters=None, mapbox_token=None, token=None):
        self.search = search
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
        self.attributes = self.get_collection(token=token)
        self.id = id_hash
        self.resources = self.attributes.get('resources', None)
        self.iter_position = 0

    def _repr_html_(self):
        if self.search is not None:
            str_html = ""
            for n, c in enumerate(self.resources):
                str_html += show(c, n)
                if n < len(self.resources)-1:
                    str_html += '<p></p>'
            return str_html
        else:
            return html_box(item=self)

    def __repr__(self):
        rep_string = "["
        if self.search is not None:
            for n, c in enumerate(self.resources):
                rep_string += str(f"{n}. {c['type']} {c['id']} {c['attributes'].get('name', '')}")
                if n < len(self.resources)-1:
                    rep_string += ',\n '
        else:
            rep_string += self.__str__()
        rep_string += ']'
        return rep_string

    def __str__(self):
        return f"Collection {self.id} {self.attributes['name']}"

    def __iter__(self):
        return self

    def __next__(self):
        if self.iter_position >= len(self.resources):
            self.iter_position = 0
            raise StopIteration
        else:
            self.iter_position += 1
            return self.resources[self.iter_position - 1]

    def __getitem__(self, key):
        items = self.resources[key]
        if type(items) == list:
            return [create_class(item) for item in items]
        else:
            return create_class(items)

    def __len__(self):
        return len(self.resources)

    def get_collection(self, token=None):
        """
        Getter for the a collection object. In this case dataset and layers
        are the objects in the API. I.e. tables are a dataset type.
        """
        if self.id_hash and token and self.search is None:
            try:
                url = (f'{self.server}/v1/collection/{self.id_hash}')
                headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
                print(url)
                r = requests.get(url, headers=headers, timeout=10)
                print(r)
                col = r.json().get('data', {})
                if not col:
                    raise ValueError('No collection found')
            except:
                raise ValueError(f'Unable to get collection {self.id_hash} from {self.server}')

            resources = col.get('attributes', {}).get('resources', [])
            name = col.get('attributes', {}).get('name', [])
            app = col.get('attributes', {}).get('application', [])
            entities = [{'type': item.get('type').title() , 'id': item.get('id'), 'attributes': {}, 'server': self.server} for item in resources]
            return {
                'resources': entities,
                'name': name,
                'application': app
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
            'application': None
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

    # def create_collection(self, token=None):
    #     if not token:
    #         raise ValueError(f'[token] API token required to create new collection.')
    #     elif not (name and app):
    #         raise ValueError(f'[name] and [app] strings required to create new collection.')

    #     payload = {
    #         'name': str(name),
    #         'application': str(app),
    #         'resources': entities
    #     }

    #     try:
    #         url = (f'{self.server}/v1/collection/')
    #         headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    #         r = requests.post(url, data=json.dumps(payload), headers=headers)
    #         col = r.json().get('data', {})
    #         if r.status_code == 200:
    #             print(f"Collection {col['id']} created.")
    #             return col
    #         else:
    #             print(f'Failed with error code {r.status_code}')
    #             return None
    #     except:
    #         raise ValueError(f'Unable to create collection.')
        

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
