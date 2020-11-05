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


### Delete Meta
@requests_mock.mock(kw='mock')
def test_delete_meta(**kwargs):
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

    kwargs['mock'].delete('https://api.resourcewatch.org/dataset/7cf3fab2-3fbe-4980-b572-712207b2c8c7/metadata?application=gfw&language=en',
                       [
                           {
                               'status_code': 200,
                               'json': {}
                           }
                       ])

    ds = Dataset(id_hash='7cf3fab2-3fbe-4980-b572-712207b2c8c7')
    m = ds.metadata[0]
    assert type(m.id) == str
    deleted_meta = m.delete(token=API_TOKEN)
    assert deleted_meta == None


### Add Meta
@requests_mock.mock(kw='mock')
def test_add_meta(**kwargs):
    dataset_matcher = re.compile(
        'https://api.resourcewatch.org/v1/dataset/7cf3fab2-3fbe-4980-b572-712207b2c8c7\?includes=layer,widget,vocabulary,metadata&hash=(\w*)'
    )

    working_directory = os.getcwd()
    with open(working_directory + "/tests/test_assets/datasets/GET_7cf3fab2-3fbe-4980-b572-712207b2c8c7.json") as json_file:
        dataset = json.load(json_file)
        updated_dataset = copy.deepcopy(dataset)
    
    meta = updated_dataset['data']['attributes']['metadata'][0]
    dataset['data']['attributes']['metadata'] = []

    meta['attributes']['info'] = {'citation': 'Example citation',
                 'color': '#fe6598',
                 'description': 'This is an example dataset.',
                 'isLossLayer': True,
                 'name': 'Template Layer'}
    
    updated_dataset['data']['attributes']['metadata'][0] = meta

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
    
    kwargs['mock'].post('https://api.resourcewatch.org/v1/dataset/7cf3fab2-3fbe-4980-b572-712207b2c8c7/metadata',
                       [
                           {
                               'status_code': 200,
                               'json': {}
                           }
                       ])

    ds = Dataset(id_hash='7cf3fab2-3fbe-4980-b572-712207b2c8c7')
    payload = {
        'application': 'gfw',
        'info': {'citation': 'Example citation',
                 'color': '#fe6598',
                 'description': 'This is an example dataset.',
                 'isLossLayer': True,
                 'name': 'Template Layer'},
        'language': 'en'
    }
    ds.add_metadata(meta_params=payload, token=API_TOKEN)
    updated_ds = Dataset(id_hash='7cf3fab2-3fbe-4980-b572-712207b2c8c7')
    assert len(updated_ds.metadata) > 0


### Update Meta
@requests_mock.mock(kw='mock')
def test_update_meta(**kwargs):
    dataset_matcher = re.compile(
        'https://api.resourcewatch.org/v1/dataset/7cf3fab2-3fbe-4980-b572-712207b2c8c7\?includes=layer,widget,vocabulary,metadata&hash=(\w*)'
    )

    working_directory = os.getcwd()
    with open(working_directory + "/tests/test_assets/datasets/GET_7cf3fab2-3fbe-4980-b572-712207b2c8c7.json") as json_file:
        dataset = json.load(json_file)
        updated_dataset = copy.deepcopy(dataset)
    
    meta = updated_dataset['data']['attributes']['metadata'][0]
    meta['attributes']['info'] = {'citation': 'TEST',
                 'color': '#fe6598',
                 'description': 'TEST',
                 'isLossLayer': False,
                 'name': 'Template Layer'}
    
    updated_dataset['data']['attributes']['metadata'][0] = meta

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
    
    kwargs['mock'].patch('https://api.resourcewatch.org/v1/dataset/7cf3fab2-3fbe-4980-b572-712207b2c8c7/metadata',
                       [
                           {
                               'status_code': 200,
                               'json': {}
                           }
                       ])

    ds = Dataset(id_hash='7cf3fab2-3fbe-4980-b572-712207b2c8c7')
    m = ds.metadata[0]
    assert type(m.id) == str
    payload = {
        'application': 'gfw',
        'info': {'citation': 'TEST',
                 'color': '#fe6598',
                 'description': 'TEST',
                 'isLossLayer': False,
                 'name': 'Template Layer'},
        'language': 'en'}
    m.update(update_params=payload, token=API_TOKEN)
    ds = Dataset(id_hash='7cf3fab2-3fbe-4980-b572-712207b2c8c7')
    updated_m = ds.metadata[0]
    assert updated_m.attributes['info']['description'] == 'TEST'
    assert updated_m.attributes['info']['isLossLayer'] == False


### Merge Meta

# ----- Geometry Tests -----#

def test_geometry_create_and_describe():
    atts = {'geojson': {'type': 'FeatureCollection',
                        'features': [{'type': 'Feature',
                                      'properties': {},
                                      'geometry': {'type': 'Polygon',
                                                   'coordinates': [[[28.00004197633704, 49.710191987352424],
                                                                    [28.00004197633704, 48.18737001395745],
                                                                    [27.750103011493355, 48.18737001395745],
                                                                    [27.50016404664967, 48.18737001395745],
                                                                    [27.25022508180598, 48.18737001395745],
                                                                    [26.99982835329041, 48.18737001395745],
                                                                    [26.99982835329041, 49.710191987352424],
                                                                    [27.25022508180598, 49.710191987352424],
                                                                    [27.50016404664967, 49.710191987352424],
                                                                    [27.750103011493355, 49.710191987352424],
                                                                    [28.00004197633704, 49.710191987352424]]]}}]}}
    g = Geometry(attributes=atts)
    g.describe()
    assert g.description.get('title') is not None
