import copy
import json
import os.path
import re

import requests_mock

from LMIPy import Dataset

try:
    API_TOKEN = os.environ.get("API_TOKEN", None)
except:
    raise ValueError(f"Failed to access keys for test.")

@requests_mock.mock(kw='mock')
def test_create_dataset(**kwargs):
    working_directory = os.getcwd()
    with open(working_directory + "/tests/test_assets/datasets/GET_7cf3fab2-3fbe-4980-b572-712207b2c8c7.json") as json_file:
        dataset = json.load(json_file)

    dataset_matcher = re.compile(
        'https://api.resourcewatch.org/v1/dataset/7cf3fab2-3fbe-4980-b572-712207b2c8c7\?includes=layer,widget,vocabulary,metadata&hash=(\w*)'
    )

    kwargs['mock'].get(dataset_matcher,
                       [
                           {
                               'status_code': 200,
                               'json': dataset
                           }
                       ])

    ds = Dataset(id_hash='7cf3fab2-3fbe-4980-b572-712207b2c8c7')
    assert ds.id == '7cf3fab2-3fbe-4980-b572-712207b2c8c7'
    assert type(ds.attributes) == dict
    assert len(ds.attributes) > 0

@requests_mock.mock(kw='mock')
def test_queries_on_datasets(**kwargs):
    working_directory = os.getcwd()
    with open(working_directory + "/tests/test_assets/datasets/GET_bd5d7924-611e-4302-9185-8054acb0b44b.json") as json_file:
        dataset = json.load(json_file)
    with open(working_directory + "/tests/test_assets/carto/QUERY_bd5d7924-611e-4302-9185-8054acb0b44b_1.json") as json_file:
        query_1 = json.load(json_file)
    with open(working_directory + "/tests/test_assets/carto/QUERY_bd5d7924-611e-4302-9185-8054acb0b44b_2.json") as json_file:
        query_2 = json.load(json_file)

    dataset_matcher = re.compile(
        'https://api.resourcewatch.org/v1/dataset/bd5d7924-611e-4302-9185-8054acb0b44b\?includes=layer,widget,vocabulary,metadata&hash=(\w*)'
    )

    kwargs['mock'].get(dataset_matcher,
                       [
                           {
                               'status_code': 200,
                               'json': dataset
                           }
                       ])

    kwargs['mock'].get("https://wri-01.carto.com/api/v2/sql?q=select+%2A+FROM+mangroves_1996+limit+5",
                       [
                           {
                               'status_code': 200,
                               'json': query_1
                           }
                       ])

    kwargs['mock'].get("https://wri-01.carto.com/api/v2/sql?q=select+fid%2C+st_asgeojson%28the_geom_webmercator%29+FROM+mangroves_1996+limit+5",
                       [
                           {
                               'status_code': 200,
                               'json': query_2
                           }
                       ])


    ds = Dataset(id_hash='bd5d7924-611e-4302-9185-8054acb0b44b')
    df = ds.query()
    assert len(df) > 0
    df = ds.query('SELECT fid, ST_ASGEOJSON(the_geom_webmercator) FROM data LIMIT 5')
    assert len(df) == 5

@requests_mock.mock(kw='mock')
def test_access_vocab(**kwargs):
    working_directory = os.getcwd()
    with open(working_directory + "/tests/test_assets/datasets/GET_7cf3fab2-3fbe-4980-b572-712207b2c8c7.json") as json_file:
        dataset = json.load(json_file)

    dataset_matcher = re.compile(
        'https://api.resourcewatch.org/v1/dataset/7cf3fab2-3fbe-4980-b572-712207b2c8c7\?includes=layer,widget,vocabulary,metadata&hash=(\w*)'
    )

    kwargs['mock'].get(dataset_matcher,
                       [
                           {
                               'status_code': 200,
                               'json': dataset
                           }
                       ])

    ds = Dataset(id_hash='7cf3fab2-3fbe-4980-b572-712207b2c8c7')
    assert type(ds.vocabulary) == list
    assert len(ds.vocabulary) > 0

@requests_mock.mock(kw='mock')
def test_access_meta(**kwargs):
    working_directory = os.getcwd()
    with open(working_directory + "/tests/test_assets/datasets/GET_7cf3fab2-3fbe-4980-b572-712207b2c8c7.json") as json_file:
        dataset = json.load(json_file)

    dataset_matcher = re.compile(
        'https://api.resourcewatch.org/v1/dataset/7cf3fab2-3fbe-4980-b572-712207b2c8c7\?includes=layer,widget,vocabulary,metadata&hash=(\w*)'
    )

    kwargs['mock'].get(dataset_matcher,
                       [
                           {
                               'status_code': 200,
                               'json': dataset
                           }
                       ])

    ds = Dataset(id_hash='7cf3fab2-3fbe-4980-b572-712207b2c8c7')
    assert type(ds.metadata) == list
    assert len(ds.metadata) > 0

@requests_mock.mock(kw='mock')
def test_access_meta_attributes(**kwargs):
    working_directory = os.getcwd()
    with open(working_directory + "/tests/test_assets/datasets/GET_7cf3fab2-3fbe-4980-b572-712207b2c8c7.json") as json_file:
        dataset = json.load(json_file)
    
    dataset_matcher = re.compile(
        'https://api.resourcewatch.org/v1/dataset/7cf3fab2-3fbe-4980-b572-712207b2c8c7\?includes=layer,widget,vocabulary,metadata&hash=(\w*)'
    )

    kwargs['mock'].get(dataset_matcher,
                       [
                           {
                               'status_code': 200,
                               'json': dataset
                           }
                       ])

    ds = Dataset('7cf3fab2-3fbe-4980-b572-712207b2c8c7')
    meta = ds.metadata[0].attributes
    assert type(meta) is dict

@requests_mock.mock(kw='mock')
def test_access_widget(**kwargs):
    working_directory = os.getcwd()
    with open(working_directory + "/tests/test_assets/datasets/GET_7cf3fab2-3fbe-4980-b572-712207b2c8c7.json") as json_file:
        dataset = json.load(json_file)

    dataset_matcher = re.compile(
        'https://api.resourcewatch.org/v1/dataset/7cf3fab2-3fbe-4980-b572-712207b2c8c7\?includes=layer,widget,vocabulary,metadata&hash=(\w*)'
    )

    kwargs['mock'].get(dataset_matcher,
                       [
                           {
                               'status_code': 200,
                               'json': dataset
                           }
                       ])

    ds = Dataset('7cf3fab2-3fbe-4980-b572-712207b2c8c7')
    assert type(ds.widget) == list
    assert len(ds.widget) > 0

@requests_mock.mock(kw='mock')
def test_dataset_save(**kwargs):
    working_directory = os.getcwd()
    with open(working_directory + "/tests/test_assets/datasets/GET_7cf3fab2-3fbe-4980-b572-712207b2c8c7.json") as json_file:
        dataset = json.load(json_file)

    dataset_matcher = re.compile(
        'https://api.resourcewatch.org/v1/dataset/7cf3fab2-3fbe-4980-b572-712207b2c8c7\?includes=layer,widget,vocabulary,metadata&hash=(\w*)'
    )

    kwargs['mock'].get(dataset_matcher,
                       [
                           {
                               'status_code': 200,
                               'json': dataset
                           },
                           {
                               'status_code': 200,
                               'json': dataset
                           }
                       ])

    ds = Dataset('7cf3fab2-3fbe-4980-b572-712207b2c8c7')
    save_path = './tests'
    ds.save(path=save_path)
    assert os.path.exists(save_path + f"/{ds.id}.json") == True

@requests_mock.mock(kw='mock')
def test_dataset_load(**kwargs):
    working_directory = os.getcwd()
    with open(working_directory + "/tests/test_assets/datasets/GET_7cf3fab2-3fbe-4980-b572-712207b2c8c7.json") as json_file:
        dataset = json.load(json_file)

    dataset_matcher = re.compile(
        'https://api.resourcewatch.org/v1/dataset/7cf3fab2-3fbe-4980-b572-712207b2c8c7\?includes=layer,widget,vocabulary,metadata&hash=(\w*)'
    )

    kwargs['mock'].get(dataset_matcher,
                       [
                           {
                               'status_code': 200,
                               'json': dataset
                           }
                       ])
                       
    ds = Dataset(id_hash='7cf3fab2-3fbe-4980-b572-712207b2c8c7')
    load_path = f'./tests'
    loaded = ds.load(path=load_path, check=True)
    assert loaded.id == '7cf3fab2-3fbe-4980-b572-712207b2c8c7'
    os.remove(load_path + f"/{ds.id}.json")
