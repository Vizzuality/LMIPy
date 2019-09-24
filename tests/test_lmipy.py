import pytest
import random
import os
import os.path
from LMIPy import Dataset, Table, Collection, Layer, Metadata, Vocabulary, Widget, Image, ImageCollection, Geometry, utils

try:
    API_TOKEN = os.environ.get("API_TOKEN", None)
except:
    raise ValueError(f"Failed to access keys for test.")


### Collection Tests

def test_search_collection():
    """Search all gfw collection for an object"""
    col = Collection(search='forest', app=['gfw'])
    assert len(col) > 1

def test_search_collection_object_type():
    """Search all gfw collection for an object"""
    col = Collection(search='forest', object_type=['layer', 'dataset', 'widget'], app=['gfw'])
    assert len(col) > 1

def test_search_collection_filters():
    """Search all gfw collection for an object"""
    col = Collection(search='forest', object_type=['layer'], filters={'provider': 'gee'}, app=['gfw'])
    assert len(col) > 1

def test_collection_save():
    col = Collection(search='template', object_type=['dataset'], app=['gfw'], env='staging')
    ds = col[0]
    save_path = './tests/collection'
    col.save(path=save_path)
    assert os.path.exists(save_path) == True
    assert f"{ds.id}.json" in os.listdir(save_path)
    _ = [os.remove(save_path+f"/{f}") for f in os.listdir(save_path)] 
    os.rmdir(save_path)  

#----- Dataset Tests -----#

def test_create_dataset():
    ds = Dataset(id_hash='bb1dced4-3ae8-4908-9f36-6514ae69713f')
    assert ds.id == 'bb1dced4-3ae8-4908-9f36-6514ae69713f'
    assert type(ds.attributes) == dict
    assert len(ds.attributes) > 0

def test_queries_on_datasets():
    ds = Dataset(id_hash='bd5d7924-611e-4302-9185-8054acb0b44b')
    df = ds.query()
    assert len(df) > 0
    df = ds.query('SELECT fid, ST_ASGEOJSON(the_geom_webmercator) FROM data LIMIT 5')
    assert len(df) == 5

def test_access_vocab():
    ds = Dataset(id_hash='bb1dced4-3ae8-4908-9f36-6514ae69713f')
    assert type(ds.vocabulary) == list
    assert len(ds.vocabulary) > 0

def test_access_meta():
    ds = Dataset(id_hash='bb1dced4-3ae8-4908-9f36-6514ae69713f')
    assert type(ds.metadata) == list
    assert len(ds.metadata) > 0

def test_access_meta_attributes():
    ds = Dataset('7cf3fab2-3fbe-4980-b572-712207b2c8c7')
    meta = ds.metadata[0].attributes
    assert type(meta) is dict

def test_access_widget():
    ds = Dataset(id_hash='dcd1e9c7-1370-404e-8816-eaa51d4b1a39')
    assert type(ds.widget) == list
    assert len(ds.widget) > 0

def test_dataset_save():
    ds = Dataset(id_hash='897ecc76-2308-4c51-aeb3-495de0bdca79')
    save_path = './tests'
    ds.save(path=save_path)
    assert os.path.exists(save_path+f"/{ds.id}.json") == True

def test_dataset_load():
    ds = Dataset(id_hash='897ecc76-2308-4c51-aeb3-495de0bdca79')
    load_path = f'./tests'
    loaded = ds.load(path=load_path, check=True)
    assert loaded.id == '897ecc76-2308-4c51-aeb3-495de0bdca79'
    os.remove(load_path+f"/{ds.id}.json")

### Update Dataset
def test_update_dataset():
    ds = Dataset(id_hash='7cf3fab2-3fbe-4980-b572-712207b2c8c7')
    updated = ds.update(token=API_TOKEN, update_params={'name': f'Template Dataset UPDATED'})
    assert updated.attributes['name'] == f'Template Dataset UPDATED'
    updated = ds.update(token=API_TOKEN, update_params={'name': f'Template Dataset'})
    assert updated.attributes['name'] == 'Template Dataset'

### Clone and Delete Dataset
def test_clone_and_delete_dataset():
    d = Dataset(id_hash='7cf3fab2-3fbe-4980-b572-712207b2c8c7')
    cloned = d.clone(token=API_TOKEN, env='production', dataset_params={
        'name': 'Template Dataset CLONED',
        'published': False
        }, clone_children=True)
    assert cloned.attributes['name'] == f'Template Dataset CLONED'
    assert cloned.id is not '7cf3fab2-3fbe-4980-b572-712207b2c8c7'
    vocabulary = cloned.vocabulary
    metadata = cloned.metadata
    widget = cloned.widget
    layer = cloned.layers
    assert len(vocabulary) > 0
    assert len(metadata) > 0
    assert len(widget) > 0
    assert len(layer) > 0
    assert vocabulary[0].delete(token=API_TOKEN) == None
    assert metadata[0].delete(token=API_TOKEN) == None
    assert widget[0].delete(token=API_TOKEN) == None
    assert layer[0].delete(token=API_TOKEN, force=True) == None
    assert cloned.delete(token=API_TOKEN, force=True) == None

### Create and Delete Dataset
def test_create_new_dataset():
    atts = {
        "name": "NEW Template Dataset",
        "application": ["gfw"],
        "connectorType": "rest",
        "provider": "cartodb",
        "connectorUrl": "https://wri-01.carto.com/tables/gfw_land_rights/public_map",
        "tableName": "gfw_land_rights",
        "published": False,
        "env": "staging",
    }
    new = Dataset(attributes=atts, token=API_TOKEN)
    assert new.attributes['name'] == 'NEW Template Dataset'
    assert new.delete(token=API_TOKEN, force=True) == None

### Intersect dataset

def test_dataset_intersect():
    ds = Dataset(id_hash='fee5fc38-7a62-49b8-8874-dfa31cbb1ef6')
    g = Geometry(parameters={'iso': 'BRA', 'adm1': 1, 'adm2': 1})
    i = ds.intersect(g)
    assert i == None

#----- Layer Tests -----#

def test_layer_creation():
    ly = Layer(id_hash='dc6f6dd2-0718-4e41-81d2-109866bb9edd')
    assert ly is not None

def test_layer_query():
    ly = Layer(id_hash='2942c28e-e5b4-4003-83ad-93a2566dc6cd')
    df = ly.query()
    assert len(df) > 0
    df = ly.query("SELECT * FROM data LIMIT 10")
    assert len(df) == 10

def test_get_layer_dataset():
    l = Layer(id_hash='25dcb710-6b85-4bfa-b09b-e4c70c33f381')
    ds = l.dataset()
    assert ds.id == '7cf3fab2-3fbe-4980-b572-712207b2c8c7'

def test_layer_intersect():
    l = Layer(id_hash='f13f86cb-08b5-4e6c-bb8d-b4782052f9e5')
    g = Geometry(parameters={'iso': 'BRA', 'adm1': 1, 'adm2': 1})
    i = l.intersect(g)
    assert type(i) == dict

def test_layer_save():
    l = Layer(id_hash='25dcb710-6b85-4bfa-b09b-e4c70c33f381')
    ds = l.dataset()
    save_path = './tests'
    l.save(path=save_path)
    assert os.path.exists(save_path+f"/{ds.id}.json") == True

def test_layer_load():
    l = Layer(id_hash='25dcb710-6b85-4bfa-b09b-e4c70c33f381')
    ds = l.dataset()
    load_path = f'./tests'
    loaded = l.load(path=load_path, check=True)
    assert loaded.id == '25dcb710-6b85-4bfa-b09b-e4c70c33f381'
    os.remove(load_path+f"/{ds.id}.json")

### Clone and Delete Layer
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

### Create and Delete Layer
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

### Update Layer
def test_update_layer():
    l = Layer(id_hash='25dcb710-6b85-4bfa-b09b-e4c70c33f381')
    updated = l.update(token=API_TOKEN, update_params={'name': f'Template Layer UPDATED'})
    assert updated.attributes['name'] == f'Template Layer UPDATED'
    updated = l.update(token=API_TOKEN, update_params={'name': f'Template Layer'})
    assert updated.attributes['name'] == 'Template Layer'

### Merge Layer
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
    merged_atts = {k:v for k,v in merged_layer.attributes.items() if k in whitelist}
    production_atts =  {k:v for k,v in production_layer.attributes.items() if k in whitelist}
    assert merged_atts ==  production_atts

### Widget Tests

def test_create_widget():
    w = Widget(id_hash='8571b2c4-9478-4b63-8444-d308b191df92')
    assert w.id == '8571b2c4-9478-4b63-8444-d308b191df92'
    assert type(w.attributes) == dict
    assert len(w.attributes) > 0

### Delete Widget

def test_delete_widget():
    ds = Dataset(id_hash='7cf3fab2-3fbe-4980-b572-712207b2c8c7')
    w = ds.widget[0]
    assert type(w.id) == str
    deleted_widget= w.delete(token=API_TOKEN)
    assert deleted_widget == None

### Add Widget

def test_add_widget():
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

def test_update_widget():
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

def test_merge_widget():
    staging_widget = Widget(id_hash='66de77eb-dee3-4c56-9ad4-cf68d8b107fd', server='https://staging-api.globalforestwatch.org')
    staging_widget.update(update_params={
        'name': 'Template Widget Staging',
        'widgetConfig': {}
    }, token=API_TOKEN)
    production_widget = Dataset(id_hash='7cf3fab2-3fbe-4980-b572-712207b2c8c7').widget[0]
    whitelist = ['name', 'widgetConfig']
    merged_widget = production_widget.merge(token=API_TOKEN,
        target_widget=None,
        target_widget_id=staging_widget.id,
        target_server='https://staging-api.globalforestwatch.org',
        key_whitelist=whitelist,
        force=True)
    merged_atts = {k:v for k,v in merged_widget.attributes.items() if k in whitelist}
    production_atts =  {k:v for k,v in production_widget.attributes.items() if k in whitelist}
    assert merged_atts ==  production_atts


#----- Vocab Tests -----#

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

#----- Meta Tests -----#

### Delete Meta
def test_delete_meta():
    ds = Dataset(id_hash='7cf3fab2-3fbe-4980-b572-712207b2c8c7')
    m = ds.metadata[0]
    assert type(m.id) == str
    deleted_meta = m.delete(token=API_TOKEN)
    assert deleted_meta == None

### Add Meta
def test_add_meta():
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
def test_update_meta():
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

#----- Geometry Tests -----#

def test_geometry_create_and_describe():
    atts={'geojson': {'type': 'FeatureCollection',
                        'features': [{'type': 'Feature',
                            'properties': {},
                            'geometry': {'type': 'Polygon',
                            'coordinates': [[[28.00004197633704,49.710191987352424],
                            [28.00004197633704,48.18737001395745],
                            [27.750103011493355,48.18737001395745],
                            [27.50016404664967,48.18737001395745],
                            [27.25022508180598,48.18737001395745],
                            [26.99982835329041,48.18737001395745],
                            [26.99982835329041,49.710191987352424],
                            [27.25022508180598,49.710191987352424],
                            [27.50016404664967,49.710191987352424],
                            [27.750103011493355,49.710191987352424],
                            [28.00004197633704,49.710191987352424]]]}}]}}
    g = Geometry(attributes=atts)
    g.describe()
    assert g.description.get('title') is not None

#----- ImageCollection Tests -----#

def test_image_collection_search():
    ic = ImageCollection(lon=28.271979, lat=-16.457814, start='2018-06-01', end='2018-06-20')
    assert len(ic) > 0

#----- Image Tests -----#

def test_create_image():
    ic = ImageCollection(lon=28.271979, lat=-16.457814, start='2018-06-01', end='2018-06-20')
    im = ic[0]
    assert im.attributes['provider'] is not None

#----- Table Tests -----#

def test_create_table():
    t = Table(id_hash='97546f05-3dce-4dd0-9abf-80fd1bff9cee')
    assert t.id == '97546f05-3dce-4dd0-9abf-80fd1bff9cee'

def test_table_head():
    t = Table(id_hash='97546f05-3dce-4dd0-9abf-80fd1bff9cee')
    df = t.head()
    assert len(df) > 0

def test_table_query():
    t = Table(id_hash='97546f05-3dce-4dd0-9abf-80fd1bff9cee')
    df = t.query()
    assert len(df) == 5

#----- Utils Tests -----#

def test_sld_functions():
    sld_obj = {
        'extended': 'false',
        'items': [
            {'color': '#F8EBFF', 'quantity': -40},
            {'color': '#ECCAFC', 'quantity': -20.667},
            {'color': '#DFA4FF', 'quantity': -14.667},
            {'color': '#C26DFE', 'quantity': -10},
            {'color': '#9D36F7', 'quantity': -3.333},
            {'color': '#6D00E1', 'quantity': -0.667},
            {'color': '#3C00AB', 'quantity': 0}
        ],
        'type': 'ramp'
    }

    test_sld = {
        'extended': 'false',
        'items': [
            {'color': '#F8EBFF', 'quantity': '-40'},
            {'color': '#ECCAFC', 'quantity': '-20.667'},
            {'color': '#DFA4FF', 'quantity': '-14.667'},
            {'color': '#C26DFE', 'quantity': '-10'},
            {'color': '#9D36F7', 'quantity': '-3.333'},
            {'color': '#6D00E1', 'quantity': '-0.667'},
            {'color': '#3C00AB'}
        ],
        'type': 'ramp'
        }

    sld_str = utils.sldDump(sld_obj)
    assert sld_str == '<RasterSymbolizer> <ColorMap type="ramp" extended="false"> <ColorMapEntry color="#F8EBFF" quantity="-40" /> + <ColorMapEntry color="#ECCAFC" quantity="-20.667" /> + <ColorMapEntry color="#DFA4FF" quantity="-14.667" /> + <ColorMapEntry color="#C26DFE" quantity="-10" /> + <ColorMapEntry color="#9D36F7" quantity="-3.333" /> + <ColorMapEntry color="#6D00E1" quantity="-0.667" /> + <ColorMapEntry color="#3C00AB" /> + </ColorMap> </RasterSymbolizer>'
    assert utils.sldParse(sld_str) == test_sld
