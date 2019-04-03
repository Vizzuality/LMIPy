import requests
import folium
import urllib
import json
import random
from .utils import html_box


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
    def __init__(self, id_hash=None, attributes=None, server='https://api.resourcewatch.org'):
        self.server = server
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
        hash = random.getrandbits(16)
        url = (f'{self.server}/v1/layer/{self.id}?includes=vocabulary,metadata&hash={hash}')
        r = requests.get(url)
        if r.status_code == 200:
            return r.json().get('data').get('attributes')
        else:
            raise ValueError(f'Unable to get dataset {self.id} from {r.url}')

    def parse_map_url(self, TOKEN=None):
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
            if not TOKEN:
                raise ValueError("Requires a Mapbox Access Token in param: 'TOKEN'.")
            return self.get_mapbox_tiles(TOKEN)


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
        url = f'https://api.resourcewatch.org/v1/layer/{self.id}/tile/gee/{{z}}/{{x}}/{{y}}.png'
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

    def get_mapbox_tiles(self, MAPBOX_ACCESS_TOKEN):
        """"Retrieve mapbox tiles... as raster :("""
        layerConfig = self.attributes['layerConfig']

        vector_target = layerConfig['body'].get('format', None)

        if vector_target and vector_target.lower() == 'mapbox':
            vector_source = layerConfig['body'].get('url', '').split('mapbox://')[1]

            url = f"https://api.mapbox.com/v4/{vector_source}.json?secure&access_token={MAPBOX_ACCESS_TOKEN}"

            r = requests.get(url, headers={'Content-Type': 'application/json'})
            if r.status_code == 200:
                return r.json().get('tiles', [None])[0].replace('vector.pbf', 'png')
            else:
                raise ValueError(f'Unable to get retrieve map url for {self.id} from {vector_target.lower()}')
        else:
            raise ValueError('Mapbox target not found')

    def map(self, TOKEN=None, lat=0, lon=0, zoom=3):
        """
        Returns a folim map with styles applied
        """

        url = self.parse_map_url(TOKEN)
        print(f'Displaying: {url}')
        map = folium.Map(
                location=[lon, lat],
                zoom_start=zoom,
                tiles='Mapbox Bright',
                detect_retina=True,
                prefer_canvas=True
        )

        map.add_tile_layer(
            tiles=url,
            attr=self.attributes.get('name')
        )

        return map