import os.path

from LMIPy import Layer

try:
    API_TOKEN = os.environ.get("API_TOKEN", None)
except:
    raise ValueError(f"Failed to access keys for test.")


def test_clone_and_delete_layer():
    l = Layer(id_hash='25dcb710-6b85-4bfa-b09b-e4c70c33f381')
    ds_id = '7cf3fab2-3fbe-4980-b572-712207b2c8c7'
    cloned = l.clone(token=API_TOKEN, layer_params={
        'name': f'Template Layer CLONED',
        'published': False
    }, target_dataset_id=ds_id)
    assert cloned.attributes['name'] == f'Template Layer CLONED'
    assert cloned.id is not '25dcb710-6b85-4bfa-b09b-e4c70c33f381'
    assert cloned.delete(token=API_TOKEN, force=True) == None


def test_create_and_delete_layer():
    ds_id = '7cf3fab2-3fbe-4980-b572-712207b2c8c7'
    l_payload = {
        "name": f'Created Layer TEST',
        "dataset": ds_id,
        "description": "",
        "application": [
            "gfw"
        ],
        "iso": [],
        "provider": "gee",
        "published": False,
        "default": False,
        "env": "production",
        "layerConfig": {},
        "legendConfig": {},
        "interactionConfig": {},
        "applicationConfig": {}
    }
    new = Layer(token=API_TOKEN, attributes=l_payload)
    assert new.attributes['name'] == f'Created Layer TEST'
    assert new.delete(token=API_TOKEN, force=True) == None


def test_update_layer():
    l = Layer(id_hash='25dcb710-6b85-4bfa-b09b-e4c70c33f381')
    updated = l.update(token=API_TOKEN, update_params={'name': f'Template Layer UPDATED'})
    assert updated.attributes['name'] == f'Template Layer UPDATED'
    updated = l.update(token=API_TOKEN, update_params={'name': f'Template Layer'})
    assert updated.attributes['name'] == 'Template Layer'


def test_merge_layer():
    staging_layer = Layer('626e08ed-15b5-499a-8a46-9a5cb52d0a30', server='https://staging-api.globalforestwatch.org')
    staging_layer.update(token=API_TOKEN, update_params={
        'name': 'Template Layer Staging',
        'iso': [],
        'layerConfig': {},
        'legendConfig': {},
        'applicationConfig': {},
        'interactionConfig': {}
    })
    production_layer = Layer('25dcb710-6b85-4bfa-b09b-e4c70c33f381')
    whitelist = [
        'layerConfig',
        'legendConfig',
        'applicationConfig',
        'interactionConfig',
        'description',
        'iso',
        'application',
        'provider',
        'published'
    ]
    merged_layer = production_layer.merge(token=API_TOKEN,
                                          target_layer=None,
                                          target_layer_id='626e08ed-15b5-499a-8a46-9a5cb52d0a30',
                                          target_server='https://staging-api.globalforestwatch.org',
                                          key_whitelist=whitelist,
                                          force=True)
    merged_atts = {k: v for k, v in merged_layer.attributes.items() if k in whitelist}
    production_atts = {k: v for k, v in production_layer.attributes.items() if k in whitelist}
    assert merged_atts == production_atts
