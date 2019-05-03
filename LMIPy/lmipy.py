import requests
import random
import json
from .utils import html_box


class Metadata:
    """
    This is the main Metadata class.

    Parameters
    ----------
    attributes: dic
        A dictionary holding the attributes of a metadata (which are attached to a Dataset).
    """
    def __init__(self, attributes=None):
        if attributes.get('type') != 'metadata':
            raise ValueError(f"Non metadata attributes passed to Metadata class ({attributes.get('type')})")
        self.id = attributes.get('id')
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
            raise ValueError(f'[token] Resource Watch API token required to update metadata.')
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
                url = f'https://api.resourcewatch.org/v1/dataset/{ds_id}/metadata'
                print('url',url)
                headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
                r = requests.patch(url, data=json.dumps(payload), headers=headers)
            except:
                raise ValueError(f'Metadata update failed.')
            if r.status_code == 200:
                print(f'Metadata updated.')
                return Dataset(ds_id).metadata
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
            raise ValueError(f'[token] Resource Watch API token required to delete vocabulary.')
        lang = self.attributes.get('language', None)
        app = self.attributes.get('application', None)
        ds_id = self.attributes.get('dataset', None)
        if lang and app:
            try:
                url = f'http://api.resourcewatch.org/dataset/{ds_id}/metadata?application={app}&language={lang}'
                headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
                r = requests.delete(url, headers=headers)
            except:
                raise ValueError(f'Metdata deletion failed.')
            if r.status_code == 200:
                print(f'Metdata deleted.')
        return None

class Vocabulary:
    """
    This is the main Vocabulary class.

    Parameters
    ----------
    attributes: dic
        A dictionary holding the attributes of a vocabulary (which are attached to a Dataset).
    """
    def __init__(self, attributes=None,):
        if attributes.get('type') != 'vocabulary':
            raise ValueError(f"Non vocabulary attributes passed to Vocabulary class ({attributes.get('type')})")
        self.attributes = attributes.get('attributes')
        self.id = self.attributes.get('resource').get('id')

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Vocabulary {self.id}"

    def update(self, update_params=None, token=None):
        """
        Update the attributes of a Vocabulary object providing a RW-API token is supplied.
        
        A single application string, name string and tags list must be specified within the `update_params` dictionary.
        """
        from .dataset import Dataset
        if not token:
            raise ValueError(f'[token] Resource Watch API token required to update vocabulary.')
        update_params['application'] = self.attributes.get('application', None)
        ds_id = self.id
        self.delete(token=token)
        Dataset(ds_id).add_vocabulary(vocab_params=update_params, token=token)
        return Dataset(ds_id).vocabulary

    def delete(self, token=None):
        """
        Delete the current vocabulary, removing it's association to the parent dataset.
        A RW-API token is required.
        """
        if not token:
            raise ValueError(f'[token] Resource Watch API token required to delete vocabulary.')
        vocab_type = self.attributes.get('name', None)
        app = self.attributes.get('application', None)
        ds_id = self.id
        if vocab_type and app:
            try:
                url = f'http://api.resourcewatch.org/dataset/{ds_id}/vocabulary/{vocab_type}?app={app}'
                headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
                r = requests.delete(url, headers=headers)
            except:
                raise ValueError(f'Vocabulary deletion failed.')
            if r.status_code == 200:
                print(f'Vocabulary {vocab_type} deleted.')
        return None
