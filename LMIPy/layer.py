import requests
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
