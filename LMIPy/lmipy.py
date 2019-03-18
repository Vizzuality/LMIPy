import requests


class LMI(object):
    def __init__(self, token=None, server='http://production-api.globalforestwatch.org/'):
        self.token = token
        self.server = server

    def set_token(self, token):
        """Set the API token"""
        try:
            token = str(token)
            self.token = token
        except:
            raise ValueError('API token invalid')

    def set_server(self, server):
        """Set the targert server"""
        try:
            server = str(server)
            self.server = server
        except:
            raise ValueError('Server not valid')

