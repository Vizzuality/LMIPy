import requests
import folium
import urllib
import json
import random
from .utils import html_box


class Geometry:
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
    def __init__(self, id_hash=None, attributes=None, server='http://production-api.globalforestwatch.org'):
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
            self.attributes = self.get_geometry()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Geometry {self.id}"

    def _repr_html_(self):
        return html_box(item=self)

    def get_geometry(self, simplify=False):
        """
        Returns a layer from a Vizzuality API.
        """
        hash = random.getrandbits(16)
        url = (f'{self.server}/v2/geostore/{self.id}?simplify={simplify}&hash={hash}')
        r = requests.get(url)
        if r.status_code == 200:
            return r.json().get('data').get('attributes')
        else:
            raise ValueError(f'Unable to get dataset {self.id} from {r.url}')

    def map(self, lat=0, lon=0, zoom=3):
        """
        Returns a folim choropleth map with styles applied via attributes
        """
        pass
        return None