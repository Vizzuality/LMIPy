import copy
import json
import os.path
import re

import requests_mock

from LMIPy import Dataset, Geometry

try:
    API_TOKEN = os.environ.get("API_TOKEN", None)
except:
    raise ValueError(f"Failed to access keys for test.")


# Update Dataset
@requests_mock.mock(kw='mock')
def test_update_dataset(**kwargs):
    dataset_matcher = re.compile(
        'https://api.resourcewatch.org/v1/dataset/7cf3fab2-3fbe-4980-b572-712207b2c8c7\?includes=layer,widget,vocabulary,metadata&hash=(\w*)'
    )

    working_directory = os.getcwd()
    with open(working_directory + "/tests/test_assets/datasets/GET_7cf3fab2-3fbe-4980-b572-712207b2c8c7.json") as json_file:
        dataset = json.load(json_file)
        updated_dataset = copy.deepcopy(dataset)
        updated_dataset['data']['attributes']['name'] = "Template Dataset UPDATED"

    kwargs['mock'].get(dataset_matcher,
                       [
                           {
                               'status_code': 200,
                               'json': dataset
                           },
                           {
                               'status_code': 200,
                               'json': updated_dataset
                           },
                           {
                               'status_code': 200,
                               'json': dataset
                           }
                       ])

    kwargs['mock'].patch('https://api.resourcewatch.org/dataset/7cf3fab2-3fbe-4980-b572-712207b2c8c7',
                         [
                             {
                                 'status_code': 200,
                                 'json': updated_dataset
                             },
                             {
                                 'status_code': 200,
                                 'json': {
                                     "data": dataset
                                 }
                             }
                         ]
                         )

    ds = Dataset(id_hash='7cf3fab2-3fbe-4980-b572-712207b2c8c7')
    updated = ds.update(token=API_TOKEN, update_params={'name': 'Template Dataset UPDATED'})
    assert updated.attributes['name'] == 'Template Dataset UPDATED'


# Clone Dataset
@requests_mock.mock(kw='mock')
def test_clone_dataset(**kwargs):
    working_directory = os.getcwd()
    with open(working_directory + "/tests/test_assets/datasets/GET_7cf3fab2-3fbe-4980-b572-712207b2c8c7.json") as json_file:
        dataset = json.load(json_file)
        
    cloned_dataset = copy.deepcopy(dataset)
    cloned_dataset['data']['id'] = "18f3fab2-3fbe-4980-b572-712207b2c8c7"
    cloned_dataset['data']['attributes']['name'] = "Template Dataset CLONED"
    cloned_layer = cloned_dataset['data']['attributes']['layer'][0]
    cloned_layer['id'] = '25dcb710-6b85-4bfa-b09b-e4c70c33f381'
    cloned_widget = dataset['data']['attributes']['widget'][0]
    cloned_meta = dataset['data']['attributes']['metadata'][0]
    cloned_vocab = dataset['data']['attributes']['vocabulary'][0]

    dataset_matcher = re.compile(
        'https://api.resourcewatch.org/v1/dataset/{}\?includes=layer,widget,vocabulary,metadata&hash=(\w*)'.format(
            dataset['data']['id']))
    cloned_dataset_matcher = re.compile(
        'https://api.resourcewatch.org/v1/dataset/{}\?includes=layer,widget,vocabulary,metadata&hash=(\w*)'.format(
            cloned_dataset['data']['id']))
    layer_matcher = re.compile(
        'https://api.resourcewatch.org/v1/layer/25dcb710-6b85-4bfa-b09b-e4c70c33f381\?hash=(\w*)'
    )

    kwargs['mock'].get(dataset_matcher,
                       [
                           {
                               'status_code': 200,
                               'json': dataset
                           }
                       ])

    kwargs['mock'].get(cloned_dataset_matcher,
                       [
                           {
                               'status_code': 200,
                               'json': cloned_dataset
                           }
                       ])

    kwargs['mock'].get('https://api.resourcewatch.org/v1/dataset/',
                       [
                           {
                               'status_code': 200,
                               'json': cloned_dataset
                           }
                       ])

    kwargs['mock'].post('https://api.resourcewatch.org/dataset/',
                        [
                            {
                                'status_code': 200,
                                'json': cloned_dataset
                            }
                        ]
                        )

    kwargs['mock'].post('https://api.resourcewatch.org/dataset/18f3fab2-3fbe-4980-b572-712207b2c8c7/layer',
                        [
                            {
                                'status_code': 200,
                                'json': {
                                    'data': cloned_layer
                                }
                            }
                        ]
                        )

    kwargs['mock'].get(layer_matcher,
                        [
                            {
                                'status_code': 200,
                                'json': {
                                    'data': cloned_layer
                                }
                            }
                        ]
                        )
        
    kwargs['mock'].post('https://api.resourcewatch.org/v1/dataset/18f3fab2-3fbe-4980-b572-712207b2c8c7/widget',
                        [
                            {
                                'status_code': 200,
                                'json': {
                                    'data': cloned_widget
                                }
                            }
                        ]
                        )
            
    kwargs['mock'].post('https://api.resourcewatch.org/v1/dataset/18f3fab2-3fbe-4980-b572-712207b2c8c7/metadata',
                        [
                            {
                                'status_code': 200,
                                'json': {
                                    'data': cloned_meta
                                }
                            }
                        ]
                        )
            
    kwargs['mock'].post('https://api.resourcewatch.org/v1/dataset/18f3fab2-3fbe-4980-b572-712207b2c8c7/vocabulary/categoryTab',
                        [
                            {
                                'status_code': 200,
                                'json': {
                                    'data': cloned_vocab
                                }
                            }
                        ]
                        )

    d = Dataset(id_hash='7cf3fab2-3fbe-4980-b572-712207b2c8c7')
    cloned = d.clone(token=API_TOKEN, env='production', dataset_params={
        'name': 'Template Dataset CLONED',
        'published': False
    }, clone_children=True)
    assert cloned.attributes['name'] == f'Template Dataset CLONED'
    assert cloned.id is not '7cf3fab2-3fbe-4980-b572-712207b2c8c7'
    vocabulary = d.vocabulary
    metadata = d.metadata
    widgets = d.widget
    layers = d.layers
    cloned_vocabulary = cloned.vocabulary
    cloned_metadata = cloned.metadata
    cloned_widgets = cloned.widget
    cloned_layers = cloned.layers
    assert len(vocabulary) == len(cloned_vocabulary)
    assert len(metadata) == len(cloned_metadata)
    assert len(widgets) == len(cloned_widgets)
    assert len(layers) == len(cloned_layers)


### Create new Dataset
@requests_mock.mock(kw='mock')
def test_create_new_dataset(**kwargs):
    new_dataset_attributes = {
        "name": "NEW Template Dataset",
        "application": ["gfw"],
        "connectorType": "rest",
        "provider": "cartodb",
        "connectorUrl": "https://wri-01.carto.com/tables/gfw_land_rights/public_map",
        "tableName": "gfw_land_rights",
        "published": False,
        "env": "staging",
    }

    working_directory = os.getcwd()
    with open(working_directory + "/tests/test_assets/datasets/GET_7cf3fab2-3fbe-4980-b572-712207b2c8c7.json") as json_file:
        dataset = json.load(json_file)
        dataset['data']['attributes'] = {**dataset['data']['attributes'], **new_dataset_attributes}

    dataset_matcher = re.compile(
        'https://api.resourcewatch.org/v1/dataset/{}\?includes=layer,widget,vocabulary,metadata&hash=(\w*)'.format(
            dataset['data']['id']))

    kwargs['mock'].get(dataset_matcher,
                       [
                           {
                               'status_code': 200,
                               'json': dataset
                           }
                       ])

    kwargs['mock'].post('https://api.resourcewatch.org/dataset',
                        [
                            {
                                'status_code': 200,
                                'json': dataset
                            }
                        ]
                        )

    new = Dataset(attributes=new_dataset_attributes, token=API_TOKEN)
    assert new.attributes['name'] == 'NEW Template Dataset'


### Intersect dataset

# def test_dataset_intersect():
#     ds = Dataset(id_hash='fee5fc38-7a62-49b8-8874-dfa31cbb1ef6')
#     g = Geometry(parameters={'iso': 'BRA', 'adm1': 1, 'adm2': 1})
#     i = ds.intersect(g)
#     assert i == None
