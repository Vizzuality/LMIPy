import requests
from .utils import html_box, nested_set

class Vocabulary:
    """
    This is the main Vocabulary class.

    Parameters
    ----------
    attributes: dic
        A dictionary holding the attributes of a vocabulary (which are attached to a Dataset).
    """
    def __init__(self, attributes=None, server='https://api.resourcewatch.org'):
        if attributes.get('type') != 'vocabulary':
            raise ValueError(f"Non vocabulary attributes passed to Vocabulary class ({attributes.get('type')})")
        self.server = server
        self.type = 'Vocabulary'
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
            raise ValueError(f'[token] API token required to update vocabulary.')
        update_params['application'] = self.attributes.get('application', None)
        ds_id = self.id
        self.delete(token=token)
        Dataset(id_hash=ds_id, server=self.server).add_vocabulary(vocab_params=update_params, token=token)
        return Dataset(id_hash=ds_id, server=self.server).vocabulary

    def delete(self, token=None):
        """
        Delete the current vocabulary, removing it's association to the parent dataset.
        A RW-API token is required.
        """
        if not token:
            raise ValueError(f'[token] API token required to delete vocabulary.')
        vocab_type = self.attributes.get('name', None)
        app = self.attributes.get('application', None)
        ds_id = self.id
        if vocab_type and app:
            try:
                url = f'{self.server}/dataset/{ds_id}/vocabulary/{vocab_type}?app={app}'
                headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
                r = requests.delete(url, headers=headers)
            except:
                raise ValueError(f'Vocabulary deletion failed.')
            if r.status_code == 200:
                print(f'Vocabulary {vocab_type} deleted.')
        return None
