import copy
import json
import os.path
import re

import requests_mock

from LMIPy import Layer

try:
    API_TOKEN = os.environ.get("API_TOKEN", None)
except:
    raise ValueError(f"Failed to access keys for test.")

@requests_mock.mock(kw='mock')
def test_clone_and_delete_layer(**kwargs):
    working_directory = os.getcwd()
    with open(working_directory + "/tests/test_assets/layers/GET_25dcb710-6b85-4bfa-b09b-e4c70c33f381.json") as json_file:
        layer = json.load(json_file)

    cloned_layer = copy.deepcopy(layer)
    cloned_layer['data']['id'] = "18f3fab2-3fbe-4980-b572-712207b2c8c7"
    cloned_layer['data']['attributes']['name'] = "Template Layer CLONED"
    
    layer_matcher = re.compile(
        'https://api.resourcewatch.org/v1/layer/25dcb710-6b85-4bfa-b09b-e4c70c33f381\?hash=(\w*)'
    )

    kwargs['mock'].post('https://api.resourcewatch.org/dataset/7cf3fab2-3fbe-4980-b572-712207b2c8c7/layer',
                        [
                            {
                                'status_code': 200,
                                'json': cloned_layer
                            }
                        ]
                        )

    kwargs['mock'].get(layer_matcher,
                       [
                           {
                               'status_code': 200,
                               'json': cloned_layer
                           }
                       ])

    kwargs['mock'].delete('https://api.resourcewatch.org/dataset/7cf3fab2-3fbe-4980-b572-712207b2c8c7/layer/18f3fab2-3fbe-4980-b572-712207b2c8c7',
                       [
                           {
                               'status_code': 200,
                               'json': {}
                           }
                       ])
                       

    l = Layer(id_hash='25dcb710-6b85-4bfa-b09b-e4c70c33f381')
    ds_id = '7cf3fab2-3fbe-4980-b572-712207b2c8c7'
    cloned = l.clone(token=API_TOKEN, layer_params={
        'name': f'Template Layer CLONED',
        'published': False
    }, target_dataset_id=ds_id)
    assert cloned.attributes['name'] == f'Template Layer CLONED'
    assert cloned.id is not '25dcb710-6b85-4bfa-b09b-e4c70c33f381'
    assert cloned.delete(token=API_TOKEN, force=True) == None

@requests_mock.mock(kw='mock')
def test_create_and_delete_layer(**kwargs):
    working_directory = os.getcwd()
    with open(working_directory + "/tests/test_assets/layers/GET_25dcb710-6b85-4bfa-b09b-e4c70c33f381.json") as json_file:
        layer = json.load(json_file)    

    created_layer = copy.deepcopy(layer)
    created_layer['data']['id'] = "18f3fab2-3fbe-4980-b572-712207b2c8c7"
    created_layer['data']['attributes']['name'] = "Created Layer TEST"

    layer_matcher = re.compile(
        'https://api.resourcewatch.org/v1/layer/18f3fab2-3fbe-4980-b572-712207b2c8c7\?hash=(\w*)'
    )

    kwargs['mock'].post('https://api.resourcewatch.org/v1/dataset/7cf3fab2-3fbe-4980-b572-712207b2c8c7/layer',
                        [
                            {
                                'status_code': 200,
                                'json': created_layer
                            }
                        ]
                        )

    kwargs['mock'].get(layer_matcher,
                       [
                           {
                               'status_code': 200,
                               'json': created_layer
                           }
                       ])

    kwargs['mock'].delete('https://api.resourcewatch.org/dataset/7cf3fab2-3fbe-4980-b572-712207b2c8c7/layer/18f3fab2-3fbe-4980-b572-712207b2c8c7',
                       [
                           {
                               'status_code': 200,
                               'json': {}
                           }
                       ])

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


@requests_mock.mock(kw='mock')
def test_update_layer(**kwargs):
    layer_matcher = re.compile(
        'https://api.resourcewatch.org/v1/layer/25dcb710-6b85-4bfa-b09b-e4c70c33f381\?hash=(\w*)'
    )

    working_directory = os.getcwd()
    with open(working_directory + "/tests/test_assets/layers/GET_25dcb710-6b85-4bfa-b09b-e4c70c33f381.json") as json_file:
        layer = json.load(json_file)
        updated_layer = copy.deepcopy(layer)
        updated_layer['data']['attributes']['name'] = "Template Layer UPDATED"

    kwargs['mock'].get(layer_matcher,
                       [
                           {
                               'status_code': 200,
                               'json': layer
                           },
                           {
                               'status_code': 200,
                               'json': updated_layer
                           },
                           {
                               'status_code': 200,
                               'json': layer
                           }
                       ])

    kwargs['mock'].patch('https://api.resourcewatch.org/dataset/7cf3fab2-3fbe-4980-b572-712207b2c8c7/layer/25dcb710-6b85-4bfa-b09b-e4c70c33f381',
                         [
                             {
                                 'status_code': 200,
                                 'json': updated_layer
                             },
                             {
                                 'status_code': 200,
                                 'json': {
                                     "data": layer
                                 }
                             }
                         ]
                         )
    l = Layer(id_hash='25dcb710-6b85-4bfa-b09b-e4c70c33f381')
    updated = l.update(token=API_TOKEN, update_params={'name': f'Template Layer UPDATED'})
    assert updated.attributes['name'] == f'Template Layer UPDATED'

@requests_mock.mock(kw='mock')
def test_merge_layer(**kwargs):
    layer_matcher = re.compile(
        'https://api.resourcewatch.org/v1/layer/25dcb710-6b85-4bfa-b09b-e4c70c33f381\?hash=(\w*)'
    )
    staging_layer_matcher = re.compile(
        'https://staging-api.globalforestwatch.org/v1/layer/626e08ed-15b5-499a-8a46-9a5cb52d0a30\?hash=(\w*)'
    )

    working_directory = os.getcwd()
    with open(working_directory + "/tests/test_assets/layers/GET_25dcb710-6b85-4bfa-b09b-e4c70c33f381.json") as json_file:
        layer = json.load(json_file)
        merged_layer = copy.deepcopy(layer)
        merged_layer['data']['id'] = "626e08ed-15b5-499a-8a46-9a5cb52d0a30"

        merged_layer['data']['attributes']['name'] = 'Template Layer Staging',
        merged_layer['data']['attributes']['iso'] = [],
        merged_layer['data']['attributes']['layerConfig'] = {},
        merged_layer['data']['attributes']['legendConfig'] = {},
        merged_layer['data']['attributes']['applicationConfig'] = {},
        merged_layer['data']['attributes']['interactionConfig'] = {}

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

    kwargs['mock'].get(layer_matcher,
                       [
                           {
                               'status_code': 200,
                               'json': layer
                           }
                       ])
    
    kwargs['mock'].get(staging_layer_matcher,
                       [
                           {
                               'status_code': 200,
                               'json': layer
                           }
                       ])

    kwargs['mock'].patch('https://staging-api.globalforestwatch.org/dataset/7cf3fab2-3fbe-4980-b572-712207b2c8c7/layer/626e08ed-15b5-499a-8a46-9a5cb52d0a30',
                         [
                             {
                                 'status_code': 200,
                                 'json': merged_layer
                             }
                         ]
                         )

    staging_layer = Layer('626e08ed-15b5-499a-8a46-9a5cb52d0a30', server='https://staging-api.globalforestwatch.org')
    merged_layer = staging_layer.merge(token=API_TOKEN,
                                          target_layer=None,
                                          target_layer_id='626e08ed-15b5-499a-8a46-9a5cb52d0a30',
                                          target_server='https://staging-api.globalforestwatch.org',
                                          key_whitelist=whitelist,
                                          force=True)
    merged_atts = {k: v for k, v in merged_layer.attributes.items() if k in whitelist}
    production_atts = {k: v for k, v in merged_layer.attributes.items() if k in whitelist}
    assert merged_atts == production_atts
