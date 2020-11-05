import copy
import json
import os.path
import re

import requests_mock

from LMIPy import Dataset, Widget

try:
    API_TOKEN = os.environ.get("API_TOKEN", None)
except:
    raise ValueError(f"Failed to access keys for test.")


### Widget Tests
def test_create_widget():
    w = Widget(id_hash='8571b2c4-9478-4b63-8444-d308b191df92')
    assert w.id == '8571b2c4-9478-4b63-8444-d308b191df92'
    assert type(w.attributes) == dict
    assert len(w.attributes) > 0


### Delete Widget
@requests_mock.mock(kw='mock')
def test_delete_widget(**kwargs):
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

    kwargs['mock'].delete('https://api.resourcewatch.org/dataset/7cf3fab2-3fbe-4980-b572-712207b2c8c7/widget/e1436fc4-6118-4097-b022-981ca94bbd3b',
                       [
                           {
                               'status_code': 200,
                               'json': {}
                           }
                       ])
    ds = Dataset(id_hash='7cf3fab2-3fbe-4980-b572-712207b2c8c7')
    w = ds.widget[0]
    assert type(w.id) == str
    deleted_widget = w.delete(token=API_TOKEN)
    assert deleted_widget == None


### Add Widget
@requests_mock.mock(kw='mock')
def test_add_widget(**kwargs):
    dataset_matcher = re.compile(
        'https://api.resourcewatch.org/v1/dataset/7cf3fab2-3fbe-4980-b572-712207b2c8c7\?includes=layer,widget,vocabulary,metadata&hash=(\w*)'
    )

    working_directory = os.getcwd()
    with open(working_directory + "/tests/test_assets/datasets/GET_7cf3fab2-3fbe-4980-b572-712207b2c8c7.json") as json_file:
        dataset = json.load(json_file)
        updated_dataset = copy.deepcopy(dataset)
    
    widget = updated_dataset['data']['attributes']['widget'][0]
    dataset['data']['attributes']['widget'] = []

    widget['attributes'] = {
        'name': 'Template Widget',
        'widgetConfig': {'key': 'val'},
        'application': ['gfw']
    }

    updated_dataset['data']['attributes']['widget'][0] = widget

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
    
    kwargs['mock'].post('https://api.resourcewatch.org/v1/dataset/7cf3fab2-3fbe-4980-b572-712207b2c8c7/widget',
                       [
                           {
                               'status_code': 200,
                               'json': {}
                           }
                       ])
    d = Dataset(id_hash='7cf3fab2-3fbe-4980-b572-712207b2c8c7')
    w = d.add_widget(widget_params={
        'name': 'Template Widget',
        'widgetConfig': {'key': 'val'},
        'application': ['gfw']
    }, token=API_TOKEN)
    assert type(w.id) == str
    assert type(w.attributes) == dict
    assert len(w.attributes) > 0


### Update Widget
@requests_mock.mock(kw='mock')
def test_update_widget(**kwargs):
    dataset_matcher = re.compile(
        'https://api.resourcewatch.org/v1/dataset/7cf3fab2-3fbe-4980-b572-712207b2c8c7\?includes=layer,widget,vocabulary,metadata&hash=(\w*)'
    )
    widget_matcher = re.compile(
        'https://api.resourcewatch.org/v1/widget/e1436fc4-6118-4097-b022-981ca94bbd3b&hash=(\w*)'
    )

    working_directory = os.getcwd()
    with open(working_directory + "/tests/test_assets/datasets/GET_7cf3fab2-3fbe-4980-b572-712207b2c8c7.json") as json_file:
        dataset = json.load(json_file)
        updated_dataset = copy.deepcopy(dataset)
    
    widget = updated_dataset['data']['attributes']['widget'][0]
    widget['attributes'] = {
        'name': 'Widget UPDATED',
        'widgetConfig': {'updated': True}
    }
    
    updated_dataset['data']['attributes']['widget'][0] = widget

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
    
    kwargs['mock'].patch('https://api.resourcewatch.org/v1/dataset/7cf3fab2-3fbe-4980-b572-712207b2c8c7/widget/e1436fc4-6118-4097-b022-981ca94bbd3b',
                       [
                           {
                               'status_code': 200,
                               'json': {
                                   'data': widget
                               }
                           }
                       ])

    kwargs['mock'].get(widget_matcher,
                       [
                           {
                               'status_code': 200,
                               'json': widget
                           }
                       ])            

    ds = Dataset(id_hash='7cf3fab2-3fbe-4980-b572-712207b2c8c7')
    w = ds.widget[0]
    assert type(w.id) == str
    payload = {
        'name': 'Widget UPDATED',
        'widgetConfig': {'updated': True}
    }
    updated_w = w.update(update_params=payload, token=API_TOKEN)
    assert updated_w.attributes['name'] == 'Widget UPDATED'
    assert updated_w.attributes['widgetConfig'].get('updated', None) == True


### Merge Widget
@requests_mock.mock(kw='mock')
def test_merge_widget(**kwargs):
    widget_matcher = re.compile(
        'https://api.resourcewatch.org/v1/widget/25dcb710-6b85-4bfa-b09b-e4c70c33f381\?hash=(\w*)'
    )
    staging_widget_matcher = re.compile(
        'https://staging-api.globalforestwatch.org/v1/widget/66de77eb-dee3-4c56-9ad4-cf68d8b107fd\?hash=(\w*)'
    )

    working_directory = os.getcwd()
    with open(working_directory + "/tests/test_assets/datasets/GET_7cf3fab2-3fbe-4980-b572-712207b2c8c7.json") as json_file:
        widget = json.load(json_file)['data']['attributes']['widget'][0]
        merged_widget = copy.deepcopy(widget)
        merged_widget['id'] = "626e08ed-15b5-499a-8a46-9a5cb52d0a30"
        merged_widget['attributes']['name'] = 'Template Widget Staging'
        merged_widget['attributes']['widgetConfig'] = {}
        merged_widget['attributes']['dataset'] = '66de77eb-dee3-4c56-9ad4-cf68d8b107fd'

    whitelist = [
        'widgetConfig',
        'legendConfig',
        'applicationConfig',
        'interactionConfig',
        'description',
        'iso',
        'application',
        'provider',
        'published'
    ]

    kwargs['mock'].get(widget_matcher,
                       [
                           {
                               'status_code': 200,
                               'json': {
                                   'data': widget
                               }
                           }
                       ])
    
    kwargs['mock'].get(staging_widget_matcher,
                       [
                           {
                               'status_code': 200,
                               'json': {
                                   'data': merged_widget
                               }
                            }
                       ])

    kwargs['mock'].patch('https://staging-api.globalforestwatch.org/v1/dataset/66de77eb-dee3-4c56-9ad4-cf68d8b107fd/widget/66de77eb-dee3-4c56-9ad4-cf68d8b107fd',
                         [
                             {
                                 'status_code': 200,
                                 'json': {
                                     'data': widget
                                 }
                             }
                         ]
                         )

    staging_widget = Widget(id_hash='66de77eb-dee3-4c56-9ad4-cf68d8b107fd',
                            server='https://staging-api.globalforestwatch.org')
    production_widget = Widget(id_hash='25dcb710-6b85-4bfa-b09b-e4c70c33f381')
    whitelist = ['name', 'widgetConfig']
    merged_widget = production_widget.merge(token=API_TOKEN,
                                            target_widget=None,
                                            target_widget_id=staging_widget.id,
                                            target_server='https://staging-api.globalforestwatch.org',
                                            key_whitelist=whitelist,
                                            force=True)
    merged_atts = {k: v for k, v in merged_widget.attributes.items() if k in whitelist}
    production_atts = {k: v for k, v in production_widget.attributes.items() if k in whitelist}
    assert merged_atts == production_atts