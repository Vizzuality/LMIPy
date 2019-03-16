import LMIPy

def test_intilize():
    token = 'token'
    LMIPy.initilize('token')
    assert token == LMIPy.token
