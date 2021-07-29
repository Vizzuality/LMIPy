import requests
import random
import json
from .utils import html_box, nested_set
import getpass

class Auth:
    def __init__(self, server='production'):
        self.server =  {
            'production': 'https://api.resourcewatch.org',
            'staging': 'https://staging-api.resourcewatch.org'
        }.get(server, None)

    def login(self, email=None):
        data = None
        with requests.Session() as s:
            headers = {'Content-Type': 'application/json'}
            payload = json.dumps({'email': email or f'{input(f"Email: ")}',
                                'password': f'{getpass.getpass(prompt="Password: ")}'})
            r = s.post(f'{self.server}/auth/login',  headers=headers,  data=payload)
            r.raise_for_status()
            data = r.json().get('data', None)
        
        if data:
            self._id = data.get('_id', None)
            self.createdAt = data.get('createdAt', None)
            self.email = data.get('email', None)
            self.apps = data.get('extraUserData', {}).get('apps', [])
            self.id = data.get('id', None)
            self.name = data.get('name', None)
            self.provider = data.get('provider', None)
            self.role = data.get('role', None)
            self.token = data.get('token', None)
            self.updatedAt = data.get('updatedAt', None)

    def register(self, name=None, email=None):

        with requests.Session() as s:
            headers = {'Content-Type': 'application/json'}
            payload = json.dumps({'name': name or f'{input(f"name: ")}',
                                'email': email or f'{input(f"email: ")}'})
            r = s.post(f'{self.server}/auth/sign-up',  headers=headers,  data=payload)
            r.raise_for_status()
            if r.status_code == 200:
                print("Registration successful!\nWe've sent you an email. Click the link in it to confirm your account.")
            
            return

    def generateToken(self):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        r = requests.get(f"{self.server}/auth/generate-token", headers=headers)
        print(r.url)
        token = r.json().get('token', None)
        if token: self.token = token

        return

    def getUserById(self, user_id, token=None):
        if not token: token = self.token

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        r = requests.get(f'{self.server}/auth/user/{user_id}',  headers = headers)
        print(r.url)
        r.raise_for_status()
            
        return r.json()

    def updateUser(self, user_id, token=None, payload={}):
        if not token: token = self.token

        if not payload:
            print('Payload required')
            return None
        if 'apps' in payload.keys():
            apps = payload['apps']
            payload['extraUserData'] = {
                'apps': apps
            }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        r = requests.patch(f'{self.server}/auth/user/{user_id}',  headers=headers, data=json.dumps(payload))
        print(r.url)
        r.raise_for_status()
        return r.json().get('data')

    def getUserByEmail(self, user_email, env='production', token=None):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        r = requests.get(f'{self.server}/auth/user?app=all&email={user_email}',  headers = headers)
        print(r.url)
        r.raise_for_status()
            
        return r.json().get('data')
