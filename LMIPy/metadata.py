import requests
import random
import json
from .utils import html_box, nested_set
    

class Metadata:
    """
    This is the main Metadata class.

    Parameters
    ----------
    attributes: dic
        A dictionary holding the attributes of a metadata (which are attached to a Dataset).
    """
    def __init__(self, attributes=None, server='https://api.resourcewatch.org'):
        if attributes.get('type', None) != 'metadata':
            raise ValueError(f"Non metadata attributes passed to Metadata class ({attributes.get('type')})")
        self.id = attributes.get('id')
        self.type = 'Metadata'
        self.server = server
        self.attributes = attributes.get('attributes')

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Metadata {self.id}"

    def update(self, update_params=None, token=None):
        """
        Update the attributes of a Metadata object providing a RW-API token is supplied.

        A single application string and language string ('en' by default) must be specified within the
        `update_params` dictionary, as well as an (optional) info dictionary.
        Info has a free schema.
        """
        from .dataset import Dataset
        if not token:
            raise ValueError(f'[token] API token required to update metadata.')
        app = self.attributes.get('application', None)
        lang = update_params.get('language', 'en')
        info = update_params.get('info', None)
        ds_id = self.attributes.get('dataset', None)
        if info and app:
            payload = {
                "application": app,
                "language": lang,
                "info": info,
            }
            print('payload',payload)
            try:
                url = f'{self.server}/v1/dataset/{ds_id}/metadata'
                print('url',url)
                headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
                r = requests.patch(url, data=json.dumps(payload), headers=headers)
            except:
                raise ValueError(f'Metadata update failed.')
            if r.status_code == 200:
                print(f'Metadata updated.')
                return Dataset(id_hash=ds_id, server=self.server).metadata
            else:
                print(f'Failed with error code {r.status_code}')
                return None
        else:
            raise ValueError(f'Metadata update requires info object and application string.')

    def delete(self, token=None):
        """
        Delete the current metadata, removing it's association to the parent dataset.
        A RW-API token is required.
        """
        if not token:
            raise ValueError(f'[token] API token required to delete vocabulary.')
        lang = self.attributes.get('language', None)
        app = self.attributes.get('application', None)
        ds_id = self.attributes.get('dataset', None)
        if lang and app:
            try:
                url = f'{self.server}/dataset/{ds_id}/metadata?application={app}&language={lang}'
                headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
                r = requests.delete(url, headers=headers)
            except:
                raise ValueError(f'Metdata deletion failed.')
            if r.status_code == 200:
                print(f'Metdata deleted.')
        return None