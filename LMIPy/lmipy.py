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
        if attributes.get('type') != 'metadata':
            raise ValueError(f"Non metadata attributes passed to Metadata class ({attributes.get('type')})")
        self.id = attributes.get('id')
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

class Widget:
    """
    This is the main Widget class.

    Parameters
    ----------
    attributes: dic
        A dictionary holding the attributes of a widget (which are attached to a Dataset).
    """
    def __init__(self, id_hash=None, attributes=None, server='https://api.resourcewatch.org'):
        self.id = id_hash
        self.server = server
        if id_hash:
            self.attributes = self.get_widget()
        elif attributes:
            self.id = attributes.get('id')
            self.attributes = self.get_widget()

        else:
            raise ValueError(f'Unable to initialise Widget without id_hash.')

    def __repr__(self):
        return self.__str__()

    def _repr_html_(self):
        return html_box(item=self)

    def __str__(self):
        return f"Widget {self.id} {self.attributes.get('name','')}"

    def get_widget(self):
        """
        Returns a widget from a Vizzuality API.
        """
        try:
            hash = random.getrandbits(16)
            url = (f'{self.server}/v1/widget/{self.id}?hash={hash}')
            r = requests.get(url)
        except:
            raise ValueError(f'Unable to get Widget {self.id} from {r.url}')

        if r.status_code == 200:
            return r.json().get('data').get('attributes')
        else:
            raise ValueError(f'Widget with id={self.id} does not exist.')

    def update(self, update_params=None, token=None):
        """
        Update the attributes of a Widget object providing a RW-API token is supplied.

        A single application string must be specified within the
        `update_params` dictionary, as well as an (optional) widgetCOnfig dictionary.

        Note, widgetConfig has a free schema.
        """
        from .dataset import Dataset
        if not token:
            raise ValueError(f'[token] API token required to update widget.')
        ds_id = self.attributes.get('dataset', None)
        w_id = self.id
        update_keys = ["widgetConfig", "name", "description", "application", "default", "protected", "defaultEditableWidget", "published", "freeze"]
        attributes = {f'{k}':v for k,v in self.attributes.items() if k in update_keys}
        if update_params and any([x in update_keys for x in list(update_params.keys())]):
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
                url = f'{self.server}/v1/dataset/{ds_id}/widget/{w_id}'
                print('url',url)
                headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
                r = requests.patch(url, data=json.dumps(payload), headers=headers)
            except:
                raise ValueError(f'Widget update failed.')
            if r.status_code == 200:
                print(f'Widget updated.')
                self.attributes = self.get_widget()
                return self
            else:
                print(f'Failed with error code {r.status_code}')
                return None
        else:
            raise ValueError(f'Widget update requires update_params object.')

    def delete(self, token=None):
        """
        Delete the current widget.
        A RW-API token is required.
        """
        if not token:
            raise ValueError(f'[token] API token required to delete vocabulary.')
        w_id = self.id
        ds_id = self.attributes.get('dataset', None)
        try:
            url = f'{self.server}/dataset/{ds_id}/widget/{w_id}'
            headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
            r = requests.delete(url, headers=headers)
        except:
            raise ValueError(f'Widget deletion failed.')
        if r.status_code == 200:
            print(f'Widget deleted.')
        return None

    def save(self, path=None):
        """
        Construct dataset json and save to local path in a date-referenced folder
        """
        from .dataset import Dataset
        ds_id = self.attributes['dataset']
        ds = Dataset(id_hash=ds_id, server=self.server)
        ds.save(path=path)

    def merge(self, token=None, target_widget=None, target_widget_id=None, target_server='https://api.resourcewatch.org', key_whitelist=[], force=False):
        """
        'Merge' one Widget entity into another target Widget.
        The argument `key_whitelist` can be used to specify which properties you wish to merge (if not all)
        Note: requires API token.
        """
        if not token:
            raise ValueError(f'[token] API token required to update Dataset.')
        if not target_widget and target_widget_id and target_server:
            target_widget = Widget(target_widget_id, server=target_server)
        else:
            raise ValueError(f'Requires either target Dataset or Dataset id plus server.')
        atts = self.attributes
        payload = {
            'widgetConfig': atts.get('widgetConfig', None),
            'connectorUrl': atts.get('connectorUrl', None),
            'name': atts.get('name', None),
            'description': atts.get('description', None),
            'application': atts.get('application', None),
        }
        if not key_whitelist: key_whitelist = [k for k in payload.keys()]
        filtered_payload = {k:v for k,v in payload.items() if v and k in key_whitelist}
        print(f'Merging {self.id} from {self.server} into {target_widget_id} on {target_server}.\nAre you sure you sure you want to continue?')
        if not force:
            conf = input()
        else:
            conf = 'y'
        if conf.lower() == 'y':
            try:
                merged_widget = target_widget.update(update_params=filtered_payload, token=token)
            except:
                print('Aborting...')
            print('Completed!')
            return merged_widget

        elif conf.lower() == 'n':
            print('Aborting...')
            return False
        else:
            print('Requires y/n input!')
            return False