import pytest
from LMIPy import LMI


def test_set_token():
    token = 'token'
    lmi = LMI()
    lmi.set_token('token')
    assert token == lmi.token


def test_set_server():
    server = 'https:/production-api.globalforestwatch.org'
    lmi = LMI()
    lmi.set_server(server)
    assert server == lmi.set_server

