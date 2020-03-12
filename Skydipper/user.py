import requests
import json
import random
import os
import datetime


class User:
    """
    This is the main User class.

    Parameters
    ----------
    id_hash: int
        An ID hash of the dataset in the API.
    attributes: dic
        A dictionary holding the attributes of a dataset.
    fname: str
        A path/file string pointing to the location of a file for upload.
    sever: str
        A URL string of the vizzuality server.
    """

    def __init__(self):
        self.home = os.path.expanduser('~')
        self.hidden_folder_path = f"{self.home}/.Skydipper"
        self.hidden_creds_file_path = f"{self.hidden_folder_path}/creds"
        try:
            os.stat(self.hidden_folder_path) #<-- Does the .Skydipper credential folder exist?
            #print(f"Hidden credential folder found at {self.hidden_folder_path}")
        except:
            os.mkdir(self.hidden_folder_path) # If not, create the folder in a users home dir
            #print(f"No hidden folder - generating one at {self.hidden_folder_path}")
        # At this point, a hidden folder definitley exists
        # Now it's time to get some authorization data...
        # First see if there is a credential file
        if not os.path.exists(self.hidden_creds_file_path):
            #print("No token file - Generating one now")
            self.gen_token()
        # At this point, there should be a cred file. Read the credential from the file and Test if it is valid
        self.token = self.read_token()
        if not self.token_valid():
            self.gen_token()
        #print(f"Authentication success: {self.token_valid()}")
        self.headers =  {
                        'Authorization': f'Bearer {self.token}',
                        'Content-Type': 'application/json',
                        'Cache-Control': 'no-cache'
                        }

    def gen_token(self):
        """
            Use the authorization endpoint to go to https://api.skydipper.com/auth
        """
        email = input("Please enter your the email address associated with your Skydipper account")
        password = input("Please enter your Skydipper password")
        payload = {
            "email": email,
            "password": password
        }
        url = 'https://api.skydipper.com/auth/login'
        headers = {'Content-Type': 'application/json'}
        r = requests.post(url, json=payload, headers=headers)
        if r.status_code == 200:
            self.user_id = r.json().get('data').get('id')
            self.createdAt = r.json().get('data').get('createdAt')
            self.role = r.json().get('data').get('role')
            self.extraUserData = r.json().get('data').get('extraUserData')
            self.token = r.json().get('data').get('token')
            self.save_creds()
        return

    def save_creds(self):
        with open(self.hidden_creds_file_path, 'w') as opened_file:
            opened_file.write(self.token)

    def read_token(self):
        """Read the token from the creds file"""
        with open(self.hidden_creds_file_path, 'r') as opened_file:
            tmp = opened_file.readlines()[0]
        return tmp

    def token_valid(self):
        url = "https://api.skydipper.com/api/v1/microservice"
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            return True
        else:
            return False
