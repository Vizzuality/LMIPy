import requests
import geopandas as gpd
import folium
import urllib
import json
import random
import re
from pprint import pprint
from .utils import html_box, get_geojson_string, nested_set
from .user import User

class Layer:
    """
    This is the main Layer class.

    Parameters
    ----------
    id_hash: int
        An ID hash.
    attributes: dic
        A dictionary holding the attributes of a dataset.
    server: str
        A string of the server URL.
    """
    def __init__(self, id_hash=None, attributes=None,
                    server="https://api.skydipper.com", mapbox_token=None, token=None):
        self.server = server
        self.User = User()
        self.mapbox_token = mapbox_token
        if not attributes and id_hash:
            self.id = id_hash
            self.attributes = self.get_layer()
        elif attributes and token:
            created_layer = self.new_layer(token=token, attributes=attributes, server=self.server)
            self.attributes = created_layer.attributes
            self.id = created_layer.id
        elif attributes:
            self.id = attributes.get('id')
            self.attributes = self.get_layer()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Layer {self.id} {self.attributes['name']}"

    def _repr_html_(self):
        return html_box(item=self)

    def get_layer(self):
        """
        Returns a layer from the Skydipper API.
        """
        try:
            hash = random.getrandbits(16)
            url = f'{self.server}/v1/layer/{self.id}?includes=metadata&hash={hash}'
            r = requests.get(url, headers=self.User.headers)
        except:
            raise ValueError(f'Unable to get Layer {self.id} from {r.url}')
        if r.status_code == 200:
            return r.json().get('data').get('attributes')
        else:
            raise ValueError(f'Layer with id={self.id} does not exist for server={self.server}.')

    def parse_map_url(self):
        """
        Parses map urls
        """
        if self.attributes.get('layerConfig') == None:
            raise ValueError("No layerConfig present in layer from which to create a map.")
        # if tileLayer
        if self.attributes.get('provider') == 'leaflet' and self.attributes.get('layerConfig').get('type') == 'tileLayer':
            return self.get_leaflet_tiles()
        # if GEE
        if self.attributes.get('provider') == 'gee':
            return self.get_ee_tiles()
        # If CARTO
        if self.attributes.get('provider') == 'cartodb':
            return self.get_carto_tiles()
        if self.attributes.get('provider') == 'mapbox':
            if not self.mapbox_token:
                raise ValueError("Requires a Mapbox Access Token in param: 'mapbox_token'.")
            return self.get_mapbox_tiles()

    def get_leaflet_tiles(self):
        """
        Returns leaflet urls.
        """
        url = self.attributes.get('layerConfig').get('url', None)
        if not url:
            url = self.attributes.get('layerConfig').get('body').get('url')
        # This below code is an issue. Not working and probably wont fix the problem
        # as far as I can see. E.g. check Forma case. tmp hack for now is to catch directly.
        # params_config = self.attributes.get('layerConfig').get('params_config', None)
        # if params_config:
        #     for config in params_config:
        #         key = config['key']
        #         default = config['default']
        #         required = config['required']
        #         if required:
        #             url = url.replace(f'{{{key}}}', f'{default}')
        if '{thresh}' in url:
            # try to replace thresh with a best-guess valid threshold (say 30%)
            url = url.replace('{thresh}','30')
        if '{{date}}' in url:
            # try to replace date with a best-guess valid date
            url = url.replace('{{date}}','20190331')
        return url

    def get_ee_tiles(self):
        """Returns tiles from EE assets"""
        if self.server == 'https://api.skydipper.com':
            return f'{self.server}/v1/basemaps/layer/{self.id}/{{z}}/{{x}}/{{y}}'
        else:
            return f'{self.server}/v1/layer/{self.id}/tile/gee/{{z}}/{{x}}/{{y}}'

    def get_carto_tiles(self):
        """Get tiles for Skydipper Carto Assets"""
        if self.server != 'https://api.skydipper.com':
            print(f"Not implemented for {self.server} source.")
            return None
        sql_config = self.attributes.get('layerConfig').get('sql_config', None)
        layerConfig = self.attributes.get('layerConfig')
        if sql_config:
            for config in sql_config:
                key = config['key']
                key_params = config['key_params']
                if key_params[0].get('required', False):
                    for l in layerConfig["body"]["layers"]:
                        l['options']['sql'] = l['options']['sql'].replace(f'{{{key}}}', '0').format(key_params['key'])
                else:
                    for l in layerConfig["body"]["layers"]:
                        l['options']['sql'] = l['options']['sql'].replace(f'{{{key}}}', '0').format('')
        _layerTpl = urllib.parse.quote_plus(json.dumps({
            "version": "1.3.0",
            "stat_tag": "API",
            "layers": [{ **l, "options": { **l["options"]}} for l in layerConfig.get("body").get("layers")]
        }))
        apiParams = f"?stat_tag=API&config={_layerTpl}"
        url = f"http://35.233.41.65/user/skydipper/api/v1/map{apiParams}"
        r = requests.get(url, headers={'Content-Type': 'application/json'})
        try:
            tile_url = r.json().get('metadata').get('tilejson').get('raster').get('tiles')[0]
            return tile_url
        except:
            raise ValueError(f'Unable to find map layer from {r.json()} response. Status code: {r.status_code}')

    def get_mapbox_tiles(self):
        """"Retrieve mapbox tiles... as raster :("""
        layerConfig = self.attributes['layerConfig']
        vector_target = layerConfig['body'].get('format', None)
        if vector_target and vector_target.lower() == 'mapbox':
            vector_source = layerConfig['body'].get('url', '').split('mapbox://')[1]
            url = f"https://api.mapbox.com/v4/{vector_source}.json?secure&access_token={self.mapbox_token}"
            r = requests.get(url, headers={'Content-Type': 'application/json'})
            if r.status_code == 200:
                return r.json().get('tiles', [None])[0].replace('vector.pbf', 'png')
            else:
                raise ValueError(f'Unable to get retrieve map url for {self.id} from {vector_target.lower()}')
        else:
            raise ValueError('Mapbox target not found')

    def map(self, lat=0, lon=0, zoom=3, geometry=None, color='#64D1B8', weight=4):
        """
        Returns a folim map with styles applied.

        Parameters
        ----------
        lat: float
            A latitude to focus the map on.
        lon: float
            A longitude to focus the map on.
        zoom: int
            A z-level for the map.
        geometry: Skydipper.Geometry()
            A geometry object.
        weight: int
            Weight of geom outline. Default = 4.
        color: str
            Hex code for geom outline. Default = #64D1B8.
        """
        url = self.parse_map_url()
        map = folium.Map(
                location=[lon, lat],
                zoom_start=zoom,
                tiles='OpenStreetMap',
                detect_retina=True,
                prefer_canvas=True
        )
        map.add_tile_layer(tiles=url, attr=self.attributes.get('name'))
        if geometry:
            geojson = geometry.attributes['geojson']
            geom = geojson['features'][0]['geometry']
            centroid = list(geometry.shape()[0].centroid.coords)
            bounds = [geometry.attributes['bbox'][2:][::-1],
                      geometry.attributes['bbox'][:2][::-1]]
            if geom['type'] == 'Point':
                folium.Marker(
                    centroid
                ).add_to(map)
            else:
                folium.GeoJson(
                    data=get_geojson_string(geom),
                    style_function=lambda x: {
                    'fillOpacity': 0,
                    'weight': weight,
                    'color': color
                    }
                ).add_to(map)
            map.fit_bounds(bounds)
        return map

    def update_keys(self):
        """
        Returns a list of theattribute values which could be updated
        """
        update_blacklist = ['updatedAt', 'userId', 'dataset', 'slug']
        updatable_fields = {f'{k}':v for k,v in self.attributes.items() if k not in update_blacklist}
        uk = list(updatable_fields.keys())
        return uk

    def update(self, update_params=None, token=None):
        """
        Update layer specific attribute values

        Pass a dictionary of update_params and update a layer target.

        Parameters
        ----------
        update_params: dic
            A dictionary of update paramters. You can identify the possible keys by calling
            self.update_keys(silent=False)
        token: str
            A valid API Token.
        """
        if not token:
            raise ValueError(f'[token=None] API TOKEN required for updates.')
        update_blacklist = ['updatedAt', 'userId', 'dataset', 'slug']
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
            url = f"{self.server}/dataset/{self.attributes['dataset']}/layer/{self.id}"
            headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
            r = requests.patch(url, data=json.dumps(payload), headers=self.User.headers)
        except:
            raise ValueError(f'Layer update failed.')
        if r.status_code == 200:
            response = r.json()['data']
        else:
            print(f"PATCH attempt threw a {r.status_code}!")
            return None
        self.attributes = self.get_layer()
        return self

    def confirm_delete(self):
        print(f"Delete Layer {self.attributes['name']} with id={self.id}?\n> y/n")
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
        Deletes a target layer
        """
        if not token:
            raise ValueError(f'[token=None] API token required to delete.')
        if not force:
            conf = self.confirm_delete()
        elif force:
            conf = True
        if conf:
            try:
                url = f'{self.server}/dataset/{self.attributes["dataset"]}/layer/{self.id}'
                r = requests.delete(url, headers=self.User.headers)
            except:
                raise ValueError(f'Layer deletion failed.')
            if r.status_code == 200:
                print(r.url)
                print('Deletion successful!')
                self = None
        else:
            print('Deletion aborted')
        return None

    def clone(self, token=None, env='staging', clone_server=None, layer_params={}, target_dataset_id=None):
        """
        Create a clone of current Layer (and its parent Dataset) as a new staging or prod Layer.
        A set of attributes can be specified for the clone Layer using layer_params.
        Optionally, you can also select a target Dataset to attach your Layer clone to.

        The argument `clone_server` specifies the server to clone to. Default server is the layers own server.
        """
        from .dataset import Dataset
        if not clone_server: clone_server = self.server

        if not token:
            raise ValueError(f'[token] API token required to clone.')
        target_layer_name  = self.attributes['name']
        name = layer_params.get('name', f'{target_layer_name} CLONE')
        clone_layer_attr = {**self.attributes, 'name': name}
        for k in clone_layer_attr.keys():
            if k in layer_params:
                clone_layer_attr[k] = layer_params[k]
        if target_dataset_id:
            target_dataset = Dataset(id_hash=target_dataset_id, server=clone_server)
        else:
            target_dataset = self.dataset()
            clone_dataset_attr = {**target_dataset.attributes, 'name': name, }
            payload = {"dataset":{
                'application': clone_dataset_attr['application'],
                'connectorType': clone_dataset_attr['connectorType'],
                'connectorUrl': clone_dataset_attr['connectorUrl'],
                'published': clone_dataset_attr['published'],
                'tableName': clone_dataset_attr['tableName'],
                'provider': clone_dataset_attr['provider'],
                'env': env,
                'name': clone_dataset_attr['name']
                }
            }
            print(f'Creating clone dataset')
            url = f'{clone_server}/dataset'
            r = requests.post(url, data=json.dumps(payload), headers=self.User.headers)
            print(r.url)
            pprint(payload)
            if r.status_code == 200:
                target_dataset_id = r.json()['data']['id']
            else:
                print(r.status_code)
                return None

        payload = {
            'application': clone_layer_attr['application'],
            'applicationConfig': clone_layer_attr['applicationConfig'],
            'description': clone_layer_attr.get('description', ''),
            'env': env,
            'interactionConfig': clone_layer_attr['interactionConfig'],
            'iso': clone_layer_attr['iso'],
            'layerConfig': clone_layer_attr['layerConfig'],
            'legendConfig':clone_layer_attr['legendConfig'] ,
            'name': name,
            'provider': clone_layer_attr['provider'],
            'published': clone_layer_attr['published']
        }
        print(f'Creating clone layer on target dataset')
        url = f'{clone_server}/dataset/{target_dataset_id}/layer'
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
        r = requests.post(url, data=json.dumps(payload), headers=self.User.headers)
        if r.status_code == 200:
                clone_layer_id = r.json()['data']['id']
        else:
            print(r.status_code)
            return None
        print(f'{clone_server}/v1/dataset/{target_dataset_id}/layer/{clone_layer_id}')
        return Layer(id_hash=clone_layer_id, server=clone_server)

    def parse_query(self, sql):
        """
        Distributer to decide interect method
        """
        if self.attributes.get('layerConfig') == None:
            raise ValueError("No layerConfig present in layer from which to create a query.")
        # if tileLayer
        if self.attributes.get('provider') == 'leaflet' and self.attributes.get('layerConfig').get('type') == 'tileLayer':
            print(f"Queries on provider type {self.attributes.get('provider')} currently unavailable.")
            return None
        # if GEE
        if self.attributes.get('provider') == 'gee':
            print(f"Queries on provider type {self.attributes.get('provider')} currently unavailable.")
            return None
        # If CARTO
        if self.attributes.get('provider') == 'cartodb':
            return self.get_carto_query(sql)
        return None

    def get_carto_query(self, sql):
        """
        Intersect layer against some geometry class object, geosjon object, shapely shape, or by id.
        """
        attributes = self.attributes
        sql_config = attributes.get('layerConfig').get('sql_config', None)
        layerConfig = attributes.get('layerConfig')
        if sql_config:
            for config in sql_config:
                key = config['key']
                key_params = config['key_params']
                if key_params[0].get('required', False):
                    for l in layerConfig["body"]["layers"]:
                        l['options']['sql'] = l['options']['sql'].replace(f'{{{key}}}', '0').format(key_params['key'])
                else:
                    for l in layerConfig["body"]["layers"]:
                        l['options']['sql'] = l['options']['sql'].replace(f'{{{key}}}', '0').format('')
        base_query = f'with t as ({layerConfig["body"]["layers"][0]["options"]["sql"]}) '
        sql = re.sub("from data", "from t", sql, flags=re.I)
        sql = base_query + sql.replace('"', "'")
        account = layerConfig.get('account')
        urlCarto = f"https://{account}.carto.com/api/v2/sql"
        params = {"q": sql}
        r = requests.get(urlCarto, params=params)
        if r.status_code == 200:
            return gpd.GeoDataFrame(r.json().get('rows'))
        else:
            print(f'{r.url}')
            raise ValueError(f"Bad response from Carto {r.status_code}: {r.json()}")

    def query(self, sql='SELECT * FROM data LIMIT 5'):
        """
        Query the dataset object attaced to an instanciated layer object.
        """
        return self.dataset().query(sql=sql)

    def dataset(self):
        """
        Returns parent datset
        """
        from .dataset import Dataset
        return Dataset(self.attributes['dataset'], server=self.server)

    def intersect(self, geometry):
        """
        Intersect an EE raster with a geometry

        Given a valid Skydipper.Geometry object, return a dictionary based on reduceRegion
        Parameters
        ---------
        geometry: Geometry
            An Skydipper.Geometry object
        server: str
            A string of a server to call to.
        """
        if self.attributes.get('provider') != 'gee':
            raise ValueError("Intersect currently only supported for EE raster data")
        url = f"{self.server}/query/{self.attributes.get('dataset')}"
        sql = f"SELECT ST_SUMMARYSTATS() from {self.attributes.get('layerConfig').get('assetId')}"
        params = {"sql": sql,
                  "geostore": geometry.id}
        r = requests.get(url, params=params, headers=self.User.headers)
        if r.status_code == 200:
            try:
                return r.json().get('data', None)[0].get('st_summarystats')
            except:
                raise ValueError(f'Unable to retrieve values from response {r.json()}')
        else:
            print("Hint: sometimes this service fails due to restore on EE servers. Try again.")
            raise ValueError(f'Bad response: {r.status_code} from query: {r.url}')

    def save(self, path=None):
        """
        Construct dataset json and save to local path in a date-referenced folder
        """
        from .dataset import Dataset
        self.dataset().save(path=path)

    def restore(self, path=None, check=True):
        """
        From a local backup at the specified path, restores and returns a previous version of the current dataset.
        """
        from .dataset import Dataset
        if not path:
            print('Requires a file path to valid backup .json file.')
            return None
        try:
            ds = self.dataset()
            with open(f"{path}/{ds.id}.json") as f:
                recovered_dataset = json.load(f)
            layers = recovered_dataset['attributes']['layer']
            server = recovered_dataset.get('server', "https://api.skydipper.com")
            if len(layers) > 0: recovered_layer = [l for l in layers if l['id'] == self.id][0]
            else: raise ValueError(f'No save layers found!')
            if check:
                blacklist = ['updatedAt']
                attributes = {f'{k}':v for k,v in recovered_layer['attributes'].items() if k not in blacklist}
                if self.attributes == attributes:
                    print('Loaded == existing')
                elif check:
                    print('Loaded != existing')
        except:
            raise ValueError(f'Failed to restore backup from f{path}')

        return Layer(attributes={**recovered_layer['attributes'], 'id': recovered_layer['id']}, server=server)


    def new_layer(self, token=None, attributes=None, server="https://api.skydipper.com"):
        """
        Create a new staging or prod Layer entity from attributes.
        """
        if not token:
            raise ValueError(f'[token] API token required to create a new dataset.')
        elif not attributes:
            raise ValueError(f'Attributes required to create a new dataset.')
        elif not attributes.get('dataset', None):
            raise ValueError(f'Attributes must include dataset key.')
        else:
            dataset_id = attributes['dataset']
            url = f'{server}/v1/dataset/{dataset_id}/layer'
            payload = {**attributes}
            r = requests.post(url, data=json.dumps(payload), headers=self.User.headers)
            if r.status_code == 200:
                new_layer_id = r.json()['data']['id']
            else:
                print(r.status_code)
                return None
            return Layer(id_hash=new_layer_id, server=server)

    def merge(self, token=None, target_layer=None, target_layer_id=None, target_server="https://api.skydipper.com", key_whitelist=[], force=False):
        """
        'Merge' one Layer entity into another target Layer.
        The argument `key_whitelist` can be used to specify which properties you wish to merge (if not all)
        Note: requires API token.
        """
        if not token:
            raise ValueError(f'[token] API token required update Layer.')
        if not target_layer and target_layer_id and target_server:
            target_layer = Layer(target_layer_id, server=target_server)
        else:
            raise ValueError(f'Requires either target Layer or Layer id plus server.')
        atts = self.attributes
        payload = {
            'layerConfig': atts.get('layerConfig', None),
            'legendConfig': atts.get('legendConfig', None),
            'applicationConfig': atts.get('applicationConfig', None),
            'interactionConfig': atts.get('interactionConfig', None),
            'name': atts.get('name', None),
            'description': atts.get('description', None),
            'iso': atts.get('iso', None),
            'application': atts.get('application', None),
            'provider': atts.get('provider', None)
        }
        if not key_whitelist: key_whitelist = [k for k in payload.keys()]
        filtered_payload = {k:v for k,v in payload.items() if v and k in key_whitelist}
        print(f'Merging {self.id} from {self.server} into {target_layer_id} on {target_server}.\nAre you sure you sure you want to continue?')
        if not force:
            conf = input()
        else:
            conf = 'y'
        if conf.lower() == 'y':
            try:
                merged_layer = target_layer.update(update_params=filtered_payload, token=token)
            except:
                print('Aborting...')
            print('Completed!')
            return merged_layer

        elif conf.lower() == 'n':
            print('Aborting...')
            return False
        else:
            print('Requires y/n input!')
            return False
