import requests
import json
import pandas as pd

class Creds:
    """
    Defines a GFW Data-API credential object.
    Args:
        server: Server ('staging', 'production').
        attributes: Dictionary of attributes.

    Returns:
        Creds object.
    """
    def __init__(self, server=None, attributes={}):
        self.attributes = attributes
        self.alias = attributes.get('alias', None)
        self.api_key = attributes.get('api_key', None)
        self.created_on = attributes.get('created_on', None)
        self.domains = attributes.get('domains', None)
        self.email = attributes.get('email', None)
        self.expires_on = attributes.get('expires_on', None)
        self.organization = attributes.get('organization', None)
        self.updated_on = attributes.get('updated_on', None)
        self.user_id = attributes.get('user_id', None)

        self.server = server

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        expiry_str = f'expires on {self.expires_on[:10]}' if self.expires_on else 'does not expire' 
        return f"GFW Data API Credential: '{self.alias}' ({expiry_str})"

class Auth:
    """
    Defines a GFW Data-API Authorisation class object.
    Requires a RW-API key to initialise.
    Args:
        server: Server ('staging', 'production').
        rw_api_token: RW-API token string

    Returns:
        GFWAuth object.
    """
    def __init__(self, server='production', rw_api_token=None, attributes={}):
        server_str = 'staging-' if server == 'staging' else ''
        
        self.server = server
        self.url = f"https://{server_str}data-api.globalforestwatch.org"   
        self.rw_api_token = rw_api_token
        self.keys = self.getKeys()

    def getKeys(self):
        """
        Gets data-api keys associated with the the users RW-API token.
        Args:
            server: Server ('staging', 'production').
            rw_api_token: RW-API token string

        Returns:
            List of Data-API Credentials objects.
        """
        if not self.rw_api_token:
            print("Resource Watch API ('rw_api_token') required!")
            return None
        
        url = f"{self.url}/auth/apikeys"

        headers = {'Authorization': f'Bearer {self.rw_api_token}', 'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}

        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            return [Creds(server=self.server, attributes=cred) for cred in r.json()['data']]

        else:
            print(r.status_code)
            return None

    def generateKey(self, domain_list=[], org='Vizzuality', email='', alias='', never_expires=False, verbose=False):
        """
        Generate a new GFW data-api key associated with a list of domains.
        
        Args:
            domain_list: List of domains which can be used this API key.
                        There must be at least one domain listed, unless user is an admin.
                        When making request using the API key, make sure you add the correct 
                        orgin header matching a whitelisted domain.You can use wildcards for
                        subdomains such as *.yourdomain.com. Include www. if required.
            org: Name of organization or Website
            email: User email adress
            never_expires: if True, key will not expire (admin users only)
            verbose: if True, prints url

        Returns:
            Response json.
        """
        token = self.rw_api_token
        if not token:
                print("Resource Watch API ('rw_api_token') required!")
                return None
        
        args = {"org": org, "email": email, "alias": alias}
        
        for name, val in args.items():
            if not val:
                print(f'{name} value required!')
                return None
        
        payload = {
            'domains': domain_list,
            'organization': org,
            'alias': alias,
            'email': email,
            'never_expires': never_expires
        }

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache'
            }

        url = f"{self.url}/auth/apikey"
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        
        if verbose: print(r.url)

        if r.status_code == 200:
                return r.json()['data']

        else:
            print(r.raise_for_status)
            return None

    def validateKey(self, key=None, origin=None, verbose=False):
        """
        Validates a data-api key for a given origin.
        
        Args:
            key: data-api key to validate
            origin: Origin of request (checked against 'domains')
            verbose: if True, prints url

        Returns:
            Response json.
        """
        
        if not key:
            print("'key' required!")
            return None
        elif key not in [k['api_key'] for k in self.keys]:
            print("key not in list of keys for this user required!")
            return None
        
        token = self.rw_api_token
        if not token:
                print("Resource Watch API ('rw_api_token') required!")
                return None
        
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
        if origin:
            headers['origin'] = origin

        url = f"{self.url}/auth/apikey/{key}/validate"
        r = requests.get(url, headers=headers)

        if verbose: print(r.url)
        if r.status_code == 200:
                return r.json()['data']

        else:
            print(r.raise_for_status)
            return None

    def deleteKeys(self, keys=[], verbose=False):
        """
        Takes a list of data-api keys to bulk delete
        
        Args:
            keys: list of data-api keys to delete
            verbose: if True, prints url

        Returns:
            List of collected response jsons.
        """
        if not keys:
            print("List of keys to delete required!")
            return None
        
        token = self.rw_api_token
        if not token:
                print("Resource Watch API ('rw_api_token') required!")
                return None
        
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json', 'Cache-Control': 'no-cache'}
        
        responses = []
        for key in keys:
            url = f"{self.url}/auth/apikey/{key}"
            r = requests.delete(url, headers=headers)
            if verbose: print(r.url)
                
            responses += [r.json()['data']]
        return responses

class DataCatalogue:
    """
    Constructs an interface with the GFW Data API for querying datasets.
    """

    def __init__(self, search=None, server='production', token=None):
        self.url = 'https://staging-data-api.globalforestwatch.org/dataset/' if server == 'staging' else 'https://data-api.globalforestwatch.org/dataset/'
        self.server = server
        self.token = token

        self.datasets = self.search_datasets(search)

    def search_datasets(self, search):
        datasets_available = self.get_datasets()
        if not search:
            return {i+1: Dataset(slug=d['dataset'], server=self.server) for i,d in enumerate(datasets_available)}

        search_terms = [search.lower()] + search.lower().strip().split(' ') if search else ''

        datasets_slugs = []
        for d in datasets_available:
            found = False
            slug = d['dataset']
            function = d['metadata']['function']
            if function:
                _function = function.lower()
                found = any([s in _function for s in search_terms])

            if slug:
                _slug = slug.lower()
                found = any([s in _slug for s in search_terms])
            
            if found: datasets_slugs += [slug]

        return {i+1: Dataset(slug=s, server=self.server, token=self.token) for i,s in enumerate(datasets_slugs)}

    def get_datasets(self, verbose=False):
        server = self.server
        url = 'https://staging-data-api.globalforestwatch.org/datasets/' if server == 'staging' else 'https://data-api.globalforestwatch.org/datasets/'
        
        r = requests.get(url)
        if verbose: print(r.url)

        ## Check success
        data = r.json().get('data', None)
        return data

class Dataset:
    def __init__(self, slug=None, server='staging', token=None, attributes={}):
        """gfwDataTable constructs an interface with the GFW Data API for querying."""
        self.url = 'https://staging-data-api.globalforestwatch.org/dataset/' if server == 'staging' else 'https://data-api.globalforestwatch.org/dataset/'
        self.server = server

        self._version = attributes.get('version', 'latest')
        self._slug = slug

        self._token = token

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        name_str = f"'{self.slug}'" or "null"
        return f"GFW Data API Dataset: {name_str}"

    @property
    def token(self):  
        return self._token

    @token.setter
    def token(self, value):
        self._token = value

    @token.deleter
    def attr(self):
        del self.__token 
                                    
    @property
    def version(self):
        """Version of the table."""
        return self._version

    @version.setter
    def version(self, value):
        self._version = value

    @property
    def slug(self):
        """Slug of the table."""
        return self._slug

    @slug.setter
    def slug(self, value):
        self._slug = value
    
    def get_fields(self, verbose=False):
        """Get data fields"""
        dataset = self.slug
        url = self.url + dataset + f'/{self.version}/fields' 
        r = requests.get(url)
        if verbose: print(r.url)

        ## Check success
        data = r.json().get('data', None)
        if data:
            self.fields = [d['field_name'] for d in data]
            return data
        else:
            print(f"Error fetching metadata from Data API")

    def get_metadata(self, verbose=False):
        """Fetch and object populate metadata manually."""

        dataset = self.slug
        url = self.url + dataset + f'/{self.version}'
        r = requests.get(url)
        if verbose: print(r.url)

        ## Check success
        data = r.json().get('data', None)
        if data:
            self.created_on = data.get('created_on', None)
            self.updated_on = data.get('updated_on', None)
            self.dataset = data.get('dataset', None)
            self.version = data.get('version', None)
            self.is_latest = data.get('is_latest', None)
            self.is_mutable = data.get('is_mutable', None)
            self.metadata = data.get('metadata', {})
            self.status = data.get('status', None)
            self.assets = data.get('assets', None)
            return data
        else:
            print(f"Error fetching metadata from Data API")

    def get_versions(self, verbose=False):
            """Fetch and object populate metadata manually."""

            dataset =  self.slug
            url = self.url + dataset
            r = requests.get(url)
            if verbose: print(r.url)

            ## Check success
            data = r.json().get('data', None)
            if data:
                self.versions = data.get('versions', [])
                return data
            else:
                print(f"Error fetching metadata from Data API")
        
    def query(self, sql=None, as_df=False, verbose=False, download=False, geostore_id=None):
        """Query the Data API and return results as json or DataFrame."""
        
        dataset = self.slug
        url = self.url + dataset + f"/{self.version}/{'query' if not download else 'download'}" + (f"/{download}" if download else "")
        q = sql or """SELECT * FROM data LIMIT 5"""

        if geostore_id:
            q += f"&geostore_id={geostore_id}&geostore_origin=rw"

        url += f'?sql={q}'

        headers = {
            'x-api-key': self._token,
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache'}

        r = requests.get(url, headers=headers)
        if verbose: print(r.url)

        data = r.json().get('data', None)
        if data and not download:
            return pd.DataFrame(data) if as_df else data
        elif data:
            print('Cick link to download')
        else:
            print(f"Error submitting query to Data API")
        
