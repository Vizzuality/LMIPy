import os.path

from LMIPy import Dataset

try:
    API_TOKEN = os.environ.get("API_TOKEN", None)
except:
    raise ValueError(f"Failed to access keys for test.")


### Delete Vocab
def test_delete_vocab():
    ds = Dataset(id_hash='7cf3fab2-3fbe-4980-b572-712207b2c8c7')
    v = ds.vocabulary[0]
    assert type(v.id) == str
    deleted_vocab = v.delete(token=API_TOKEN)
    assert deleted_vocab == None


### Add Vocab
def test_add_vocab():
    ds = Dataset(id_hash='7cf3fab2-3fbe-4980-b572-712207b2c8c7')
    payload = {
        'name': 'categoryTab',
        'tags': ['forestChange', 'treeCoverChange'],
        'application': 'gfw'
    }
    ds.add_vocabulary(vocab_params=payload, token=API_TOKEN)
    updated_ds = Dataset(id_hash='7cf3fab2-3fbe-4980-b572-712207b2c8c7')
    assert len(updated_ds.vocabulary) > 0


### Update Vocab
def test_update_vocab():
    ds = Dataset(id_hash='7cf3fab2-3fbe-4980-b572-712207b2c8c7')
    v = ds.vocabulary[0]
    assert type(v.id) == str
    payload = {
        'name': 'categoryTab',
        'tags': ['forestChange', 'treeCoverChange']
    }
    updated_v = v.update(update_params=payload, token=API_TOKEN)
    assert updated_v[0].attributes['name'] == 'categoryTab'
    assert updated_v[0].attributes['tags'] == ['forestChange', 'treeCoverChange']
