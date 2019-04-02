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

    def parse_map_url(self):
        """
        Parses map url
        """
        layerConfig = self.attributes.get('layerConfig')

        # if tileLayer
        if self.attributes.get('provider') == 'leaflet' and layerConfig.get('type') == 'tileLayer':
            url = layerConfig.get('url', None)
            if not url:
                url = layerConfig.get('body').get('url')

            params_config = self.attributes.get('layerConfig').get('params_config', None)
            if params_config:
                for config in params_config:
                    key = config['key']
                    default = config['default']
                    required = config['required']
                    if required:
                        url = url.replace(f'{{{key}}}', f'default')
            
            return url

        # if GEE
        if self.attributes.get('provider') == 'gee':
            url = f'https://api.resourcewatch.org/v1/layer/{self.id}/tile/gee/{{z}}/{{x}}/{{y}}.png'
            return url

        # If CARTO
        if self.attributes.get('provider') == 'cartodb':
            sql_config = self.attributes.get('layerConfig').get('sql_config', None)
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

            return f'{response["cdn_url"]["templates"]["https"]["url"]}/{layerConfig["account"]}/api/v1/map/{response["layergroupid"]}/{{z}}/{{x}}/{{y}}.png'

    def map(self, lat=0, lon=0, zoom=3):
        """
        Returns a folim map with styles applied
        """

        url = self.parse_map_url()

        map = folium.Map(
                location=[lon, lat],
                zoom_start=zoom,
                tiles='Mapbox Bright',
        )

        map.add_tile_layer(
            tiles=url,
            attr=self.attributes.get('name')
        )

        return map