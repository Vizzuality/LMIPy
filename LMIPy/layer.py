import requests
import geopandas as gpd
import folium
import urllib
import json
import random
import re
from .utils import html_box
from colored import fg, bg, attr


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
                    server='https://api.resourcewatch.org', mapbox_token=None):
        self.server = server
        self.mapbox_token = mapbox_token
        if not id_hash:
            if attributes:
                self.id = attributes.get('id', None)
                self.attributes = attributes.get('attributes', None)
            else:
                self.id = None
                self.attributes = None
        else:
            self.id = id_hash
            self.attributes = self.get_layer()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Layer {self.id}"

    def _repr_html_(self):
        return html_box(item=self)

    def get_layer(self):
        """
        Returns a layer from a Vizzuality API.
        """
        try:
            hash = random.getrandbits(16)
            url = (f'{self.server}/v1/layer/{self.id}?includes=vocabulary,metadata&hash={hash}')
            r = requests.get(url)
        except:
            raise ValueError(f'Unable to get Layer {self.id} from {r.url}')

        if r.status_code == 200:
            return r.json().get('data').get('attributes')
        else:
            raise ValueError(f'Layer with id={self.id} does not exist.')

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
        url = f'{self.server}/v1/layer/{self.id}/tile/gee/{{z}}/{{x}}/{{y}}'
        return url

    def get_carto_tiles(self):
        """Get carto tiles"""
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
        url = f"https://{layerConfig.get('account')}.carto.com/api/v1/map{apiParams}"
        r = requests.get(url, headers={'Content-Type': 'application/json'})
        if r.status_code == 200:
            response = r.json()
        else:
            raise ValueError(f'Unable to get retrieve map url for {self.id} from {self.attributes.get("provider")}')

        tile_url = f'{response["cdn_url"]["templates"]["https"]["url"]}/{layerConfig["account"]}/api/v1/map/{response["layergroupid"]}/{{z}}/{{x}}/{{y}}.png'
        return tile_url

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

    def map(self, lat=0, lon=0, zoom=3, geometry=None):
        """
        Returns a folim map with styles applied

        Parameters
        ----------
        lat: float
            A latitude to focus the map on.
        lon: float
            A longitude to focus the map on.
        zoom: int
            A z-level for the map.
        geometry: LMIPy.Geometry()
            A geometry object.
        """
        url = self.parse_map_url()
        map = folium.Map(
                location=[lon, lat],
                zoom_start=zoom,
                tiles='Mapbox Bright',
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
                    data=geometry.table(),
                    style_function=lambda x: {
                    'fillOpacity': 0,
                    'weight': 2
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

    def update(self, update_params=None, token=None, show_difference=False):
        """
        Update layer specific attribute values

        Pass a dictionary of update_params and update a layer target.

        Parameters
        ----------
        update_params: dic
            A dictionary of update paramters. You can identify the possible keys by calling
            self.update_keys(silent=False)
        token: str
            A valid Resource Watch Token.
        show_difference: bool
            Display the updates.
        """
        red_color = fg('#FF0000')
        green_color = fg('#00FF00')
        res = attr('reset')
        if not token:
            raise ValueError(f'[token=None] Resource Watch API TOKEN required for updates.')
        update_blacklist = ['updatedAt', 'userId', 'dataset', 'slug']
        attributes = {f'{k}':v for k,v in self.attributes.items() if k not in update_blacklist}
        if not update_params:
            payload = { **attributes }
        else:
            payload = { f'{key}': update_params[key] for key in update_params if key in list(attributes.keys()) }
        try:
            url = f"{self.server}/dataset/{self.attributes['dataset']}/layer/{self.id}"
            headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
            r = requests.patch(url, data=json.dumps(payload), headers=headers)
        except:
            raise ValueError(f'Layer update failed.')
        if r.status_code == 200:
            response = r.json()['data']
        else:
            print(red_color + f"PATCH attempt threw a {r.status_code}!" + res)
            return None
        if show_difference:
            old_attributes = { f'{k}': attributes[k] for k,v in payload.items() }
            print(f"Attributes to change:")
            print(red_color + f'{old_attributes} {res}')
            print(green_color + f'Updated! {res}')
            print({ f'{k}': v for k, v in response['attributes'].items() if k in payload })
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
            raise ValueError(f'[token=None] Resource Watch API token required to delete.')
        if not force:
            conf = self.confirm_delete()
        elif force:
            conf = True
        if conf:
            try:
                url = f'{self.server}/dataset/{self.attributes["dataset"]}/layer/{self.id}'
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

    def clone(self, token=None, env='staging', layer_params={}, target_dataset_id=None):
        """
        Create a clone of current Layer (and its parent Dataset) as a new staging or prod Layer.
        A set of attributes can be specified for the clone Layer using layer_params.
        Optionally, you can also select a target Dataset to attach your Layer clone to.
        """
        from .dataset import Dataset
        if not token:
            raise ValueError(f'[token] Resource Watch API token required to clone.')
        # unneccesary?
        # if not all(x not in layer_params.keys() for x in ['name', 'app']):
        #     print('The keys "name" and "app" must be defined in layer_params.')
        #     return None
        target_layer_name  = self.attributes['name']
        name = layer_params.get('name', f'{target_layer_name} CLONE')
        clone_layer_attr = {**self.attributes, 'name': name}
        for k, _ in clone_layer_attr.items():
            if k in layer_params:
                clone_layer_attr[k] = layer_params[k]
        if target_dataset_id:
            target_dataset = Dataset(target_dataset_id)
        else:
            target_dataset = Dataset(self.attributes['dataset'])
            clone_dataset_attr = {**target_dataset.attributes, 'name': name}
            payload = {
                'application': clone_dataset_attr['application'],
                'connectorType': clone_dataset_attr['connectorType'],
                'connectorUrl': clone_dataset_attr['connectorUrl'],
                'tableName': clone_dataset_attr['tableName'],
                'provider': clone_dataset_attr['provider'],
                'env': env,
                'name': clone_dataset_attr['name']
            }
            print(f'Creating clone dataset')
            url = f'{self.server}/dataset'
            headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
            r = requests.post(url, data=json.dumps(payload), headers=headers)
            if r.status_code == 200:
                target_dataset_id = r.json()['data']['id']
                clone_dataset = Dataset(target_dataset_id)
                try:
                    vocab = target_dataset.vocabulary[0].attributes
                    vocab_payload = {
                        'application': vocab['application'],
                        'name': vocab['name'],
                        'tags': vocab['tags']
                    }
                    clone_dataset.add_vocabulary(vocab_params=vocab_payload, token=token)
                    meta = target_dataset.metadata[0].attributes
                    meta_payload = {
                        'application': meta['application'],
                        'info': meta['info'],
                        'language': meta['language']
                    }
                    clone_dataset.add_metadata(meta_params=meta_payload, token=token)
                except:
                    raise ValueError('Failed to clone Vocabulary and Metadata.')
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
        }
        print(f'Creating clone layer on target dataset')
        url = f'{self.server}/dataset/{target_dataset_id}/layer'
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        if r.status_code == 200:
                clone_layer_id = r.json()['data']['id']
        else:
            print(r.status_code)
            return None
        print(f'{self.server}/v1/dataset/{target_dataset_id}/layer/{clone_layer_id}')
        self.attributes = Layer(clone_layer_id).attributes
        return Layer(clone_layer_id)

    def parse_query(self, sql):
        """
        Distriibuter to decide interect method
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
        Intersect layer against some geometry class object, geosjon object, shapely shape, or by id.
        """
        return self.parse_query(sql=sql)

    def dataset(self):
        """
        Returns parent datset
        """
        from .dataset import Dataset
        return Dataset(self.attributes['dataset'])

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
        url = f"{self.server}/query/{self.attributes.get('dataset')}"
        sql = f"SELECT ST_SUMMARYSTATS() from {self.attributes.get('layerConfig').get('assetId')}"
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
        from .dataset import Dataset
        self.dataset().save(path=path)

    def load(self, path=None, check=True):
        """
        From a local backup at the specified path, loads and returns a previous version of the current dataset.
        """
        from .dataset import Dataset
        if not path:
            print('Requires a file path to valid backup .json file.')
            return None
        try:
            with open(f"{path}/{self.id}.json") as f:
                recovered_dataset = json.load(f)
            recovered_layer = [l for l in recovered_dataset.layers if l.id == self.id][0]

            if check:
                blacklist = ['updatedAt']
                attributes = {f'{k}':v for k,v in recovered_layer['attributes'].items() if k not in blacklist}
                if self.attributes == attributes:
                    print('Loaded == existing')
                elif check:
                    print('Loaded != existing')
        except:
            raise ValueError(f'Failed to load backup from f{path}')

        return Layer(id_hash=recovered_layer['id'], attributes=recovered_dataset['attributes'])


