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


### Delete Vocab
@requests_mock.mock(kw='mock')
def test_delete_vocab(**kwargs):
    dataset_matcher = re.compile(
        'https://api.resourcewatch.org/v1/dataset/7cf3fab2-3fbe-4980-b572-712207b2c8c7\?includes=layer,widget,vocabulary,metadata&hash=(\w*)'
    )

    working_directory = os.getcwd()
    with open(working_directory + "/tests/test_assets/datasets/GET_7cf3fab2-3fbe-4980-b572-712207b2c8c7.json") as json_file:
        dataset = json.load(json_file)

    kwargs['mock'].get(dataset_matcher,
                       [
                           {
                               'status_code': 200,
                               'json': dataset
                           }
                       ])

    kwargs['mock'].delete('https://api.resourcewatch.org/dataset/7cf3fab2-3fbe-4980-b572-712207b2c8c7/vocabulary/categoryTab?app=gfw',
                       [
                           {
                               'status_code': 200,
                               'json': {}
                           }
                       ])
    ds = Dataset(id_hash='7cf3fab2-3fbe-4980-b572-712207b2c8c7')
    v = ds.vocabulary[0]
    assert type(v.id) == str
    deleted_vocab = v.delete(token=API_TOKEN)
    assert deleted_vocab == None


### Add Vocab
@requests_mock.mock(kw='mock')
def test_add_vocab(**kwargs):
    dataset_matcher = re.compile(
        'https://api.resourcewatch.org/v1/dataset/7cf3fab2-3fbe-4980-b572-712207b2c8c7\?includes=layer,widget,vocabulary,metadata&hash=(\w*)'
    )

    working_directory = os.getcwd()
    with open(working_directory + "/tests/test_assets/datasets/GET_7cf3fab2-3fbe-4980-b572-712207b2c8c7.json") as json_file:
        dataset = json.load(json_file)
        updated_dataset = copy.deepcopy(dataset)
    
    vocab = updated_dataset['data']['attributes']['vocabulary'][0]
    dataset['data']['attributes']['vocabulary'] = []

    vocab['attributes'] = {
            "resource": {
              "id": "7cf3fab2-3fbe-4980-b572-712207b2c8c7",
              "type": "dataset"
            },
            "tags": [
              "forestChange",
              "treeCoverChange"
            ],
            "name": "categoryTab",
            "application": "gfw"
          }
    
    updated_dataset['data']['attributes']['vocabulary'][0] = vocab

    kwargs['mock'].get(dataset_matcher,
                       [
                           {
                               'status_code': 200,
                               'json': dataset
                           },
                           {
                               'status_code': 200,
                               'json': updated_dataset
                           }
                       ])
    
    kwargs['mock'].post('https://api.resourcewatch.org/v1/dataset/7cf3fab2-3fbe-4980-b572-712207b2c8c7/vocabulary/categoryTab',
                       [
                           {
                               'status_code': 200,
                               'json': {}
                           }
                       ])

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
@requests_mock.mock(kw='mock')
def test_update_vocab(**kwargs):
    dataset_matcher = re.compile(
        'https://api.resourcewatch.org/v1/dataset/7cf3fab2-3fbe-4980-b572-712207b2c8c7\?includes=layer,widget,vocabulary,metadata&hash=(\w*)'
    )

    working_directory = os.getcwd()
    with open(working_directory + "/tests/test_assets/datasets/GET_7cf3fab2-3fbe-4980-b572-712207b2c8c7.json") as json_file:
        dataset = json.load(json_file)
        updated_dataset = copy.deepcopy(dataset)
    
    vocab = updated_dataset['data']['attributes']['vocabulary'][0]

    vocab['attributes'] = {
            "resource": {
              "id": "7cf3fab2-3fbe-4980-b572-712207b2c8c7",
              "type": "dataset"
            },
            "tags": [
              "forestChange",
              "treeCoverChange"
            ],
            "name": "categoryTab",
            "application": "gfw"
          }
    updated_vocab = copy.deepcopy(vocab)
    updated_vocab['attributes']['tags'] = ['test2', 'test1']

    updated_dataset['data']['attributes']['vocabulary'][0] = updated_vocab

    kwargs['mock'].get(dataset_matcher,
                       [
                           {
                               'status_code': 200,
                               'json': dataset
                           },
                           {
                               'status_code': 200,
                               'json': updated_dataset
                           }
                       ])

    kwargs['mock'].delete('https://api.resourcewatch.org/dataset/7cf3fab2-3fbe-4980-b572-712207b2c8c7/vocabulary/categoryTab?app=gfw',
                       [
                           {
                               'status_code': 200,
                               'json': {}
                           }
                       ])
        
    kwargs['mock'].post('https://api.resourcewatch.org/v1/dataset/7cf3fab2-3fbe-4980-b572-712207b2c8c7/vocabulary/categoryTab',
                       [
                           {
                               'status_code': 200,
                               'json': updated_vocab
                           }
                       ])
    

    ds = Dataset(id_hash='7cf3fab2-3fbe-4980-b572-712207b2c8c7')
    v = ds.vocabulary[0]
    assert type(v.id) == str
    payload = {
        'name': 'categoryTab',
        'tags': ['test2', 'test1']
    }
    updated_v = v.update(update_params=payload, token=API_TOKEN)
    assert updated_v[0].attributes['name'] == 'categoryTab'
    assert updated_v[0].attributes['tags'] == ['test2', 'test1']
