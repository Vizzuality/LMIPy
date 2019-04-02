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

    def __parse_map_url__(self):
        """
        Parses map url
        """

        # If CARTO
        if self.attributes.get('provider') == 'cartodb':
            layerConfig = self.attributes.get('layerConfig')

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

        url = self.__parse_map_url__()

        return folium.Map(
                location=[lon, lat],
                zoom_start=zoom,
                tiles=url,
                attr=self.attributes.get('name')
        )