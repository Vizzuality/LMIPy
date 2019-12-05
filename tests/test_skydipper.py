import pytest
import random
import os
import os.path
from Skydipper import Dataset, Table, Collection, Layer, Metadata, Vocabulary, Widget, Image, ImageCollection, Geometry, utils

try:
    SKYDIPPER_API_TOKEN = os.environ.get("SKYDIPPER_API_TOKEN", None)
except:
    raise ValueError(f"Failed to access keys for test.")


### Collection Tests

def test_search_collection():
    """Search all gfw collection for an object"""
    col = Collection('', object_type=['layer','dataset'], app=['skydipper'], limit=30)
    assert len(col) > 1

def test_search_collection_object_type():
    """Search all gfw collection for an object"""
    col = Collection(search='', object_type=['dataset'], app=['skydipper'])
    assert len(col) > 1

def test_search_collection_filters():
    """Search all gfw collection for an object"""
    col = Collection(search='', object_type=['dataset'], filters={'provider': 'gee'}, app=['skydipper'])
    assert len(col) > 1

def test_collection_save():
    col = Collection(search='biodiversity', object_type=['dataset'], filters={'provider': 'gee'}, app=['skydipper'])
    ds = col[0]
    save_path = './tests/collection'
    col.save(path=save_path)
    assert os.path.exists(save_path) == True
    assert f"{ds.id}.json" in os.listdir(save_path)
    _ = [os.remove(save_path+f"/{f}") for f in os.listdir(save_path)]
    os.rmdir(save_path)

#----- Dataset Tests -----#

def test_create_dataset():
    ds = Dataset(id_hash='94241cb4-9e91-4a1a-9fcc-993b8ac9c2b7')
    assert ds.id == '94241cb4-9e91-4a1a-9fcc-993b8ac9c2b7'
    assert type(ds.attributes) == dict
    assert len(ds.attributes) > 0

# Test deactivated for now until we add Carto or PostGIS to Skydipper
# def test_queries_on_datasets():
#     ds = Dataset(id_hash='94241cb4-9e91-4a1a-9fcc-993b8ac9c2b7')
#     df = ds.query()
#     assert len(df) > 0
#     df = ds.query('SELECT fid, ST_ASGEOJSON(the_geom_webmercator) FROM data LIMIT 5')
#     assert len(df) == 5


# Metadata tests and Class object will have to be re-written as the metadata service is defined

def test_access_meta():
    ds = Dataset(id_hash='94241cb4-9e91-4a1a-9fcc-993b8ac9c2b7')
    assert type(ds.metadata) == list
    assert ds.metadata is not None

# def test_access_meta_attributes():
#     ds = Dataset('94241cb4-9e91-4a1a-9fcc-993b8ac9c2b7')
#     meta = ds.metadata[0].attributes
#     assert type(meta) is dict

def test_dataset_save():
    ds = Dataset(id_hash='94241cb4-9e91-4a1a-9fcc-993b8ac9c2b7')
    save_path = './tests'
    ds.save(path=save_path)
    assert os.path.exists(save_path+f"/{ds.id}.json") == True

def test_dataset_load():
    ds = Dataset(id_hash='94241cb4-9e91-4a1a-9fcc-993b8ac9c2b7')
    load_path = f'./tests'
    loaded = ds.load(path=load_path, check=True)
    assert loaded.id == '94241cb4-9e91-4a1a-9fcc-993b8ac9c2b7'
    os.remove(load_path+f"/{ds.id}.json")

### Update Dataset
# def test_update_dataset():
#     ds = Dataset(id_hash='94241cb4-9e91-4a1a-9fcc-993b8ac9c2b7')
#     updated = ds.update(token=API_TOKEN, update_params={'name': f'Template Dataset UPDATED'})
#     assert updated.attributes['name'] == f'Template Dataset UPDATED'
#     updated = ds.update(token=API_TOKEN, update_params={'name': f'Template Dataset'})
#     assert updated.attributes['name'] == 'Template Dataset'

### Clone and Delete Dataset
# def test_clone_and_delete_dataset():
#     d = Dataset(id_hash='7cf3fab2-3fbe-4980-b572-712207b2c8c7')
#     cloned = d.clone(token=API_TOKEN, env='production', dataset_params={
#         'name': 'Template Dataset CLONED',
#         'published': False
#         }, clone_children=True)
#     assert cloned.attributes['name'] == f'Template Dataset CLONED'
#     assert cloned.id is not '7cf3fab2-3fbe-4980-b572-712207b2c8c7'
#     vocabulary = cloned.vocabulary
#     metadata = cloned.metadata
#     widget = cloned.widget
#     layer = cloned.layers
#     assert len(vocabulary) > 0
#     assert len(metadata) > 0
#     assert len(widget) > 0
#     assert len(layer) > 0
#     assert vocabulary[0].delete(token=API_TOKEN) == None
#     assert metadata[0].delete(token=API_TOKEN) == None
#     assert widget[0].delete(token=API_TOKEN) == None
#     assert layer[0].delete(token=API_TOKEN, force=True) == None
#     assert cloned.delete(token=API_TOKEN, force=True) == None

### Create and Delete Dataset
# def test_create_new_dataset():
#     atts = {
#         "name": "NEW Template Dataset",
#         "application": ["gfw"],
#         "connectorType": "rest",
#         "provider": "cartodb",
#         "connectorUrl": "https://wri-01.carto.com/tables/gfw_land_rights/public_map",
#         "tableName": "gfw_land_rights",
#         "published": False,
#         "env": "staging",
#     }
#     new = Dataset(attributes=atts, token=API_TOKEN)
#     assert new.attributes['name'] == 'NEW Template Dataset'
#     assert new.delete(token=API_TOKEN, force=True) == None

### Intersect dataset

def test_dataset_intersect():
    ds = Dataset(id_hash='94241cb4-9e91-4a1a-9fcc-993b8ac9c2b7')
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
    i = ds.intersect(g)
    assert i != None

#----- Layer Tests -----#

def test_layer_creation():
    ly = Layer(id_hash='e7070d5f-3d38-46b1-86eb-e98782da55dd')
    assert ly is not None

# def test_layer_query():
#     ly = Layer(id_hash='2942c28e-e5b4-4003-83ad-93a2566dc6cd')
#     df = ly.query()
#     assert len(df) > 0
#     df = ly.query("SELECT * FROM data LIMIT 10")
#     assert len(df) == 10

def test_get_layer_dataset():
    l = Layer(id_hash='e7070d5f-3d38-46b1-86eb-e98782da55dd')
    ds = l.dataset()
    assert ds.id == '94241cb4-9e91-4a1a-9fcc-993b8ac9c2b7'

def test_layer_intersect():
    l = Layer(id_hash='e7070d5f-3d38-46b1-86eb-e98782da55dd')
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
    i = l.intersect(g)
    assert type(i) == dict

def test_layer_save():
    l = Layer(id_hash='e7070d5f-3d38-46b1-86eb-e98782da55dd')
    ds = l.dataset()
    save_path = './tests'
    l.save(path=save_path)
    assert os.path.exists(save_path+f"/{ds.id}.json") == True

def test_layer_load():
    l = Layer(id_hash='e7070d5f-3d38-46b1-86eb-e98782da55dd')
    ds = l.dataset()
    load_path = f'./tests'
    loaded = l.load(path=load_path, check=True)
    assert loaded.id == 'e7070d5f-3d38-46b1-86eb-e98782da55dd'
    os.remove(load_path+f"/{ds.id}.json")

### Clone and Delete Layer
def test_clone_and_delete_layer():
    l = Layer(id_hash='e7070d5f-3d38-46b1-86eb-e98782da55dd')
    ds_id = '94241cb4-9e91-4a1a-9fcc-993b8ac9c2b7'
    cloned = l.clone(token=SKYDIPPER_API_TOKEN, layer_params={
        'name': f'Template Layer CLONED',
        'published': False
        }, target_dataset_id=ds_id)
    assert cloned.attributes['name'] == f'Template Layer CLONED'
    assert cloned.id is not '94241cb4-9e91-4a1a-9fcc-993b8ac9c2b7'
    assert cloned.delete(token=SKYDIPPER_API_TOKEN, force=True) == None

### Create and Delete Layer
# def test_create_and_delete_layer():
#     ds_id = '94241cb4-9e91-4a1a-9fcc-993b8ac9c2b7'
#     l_payload = {
#         "name": f'Created Layer TEST',
#         "dataset": ds_id,
#         "description": "",
#         "application": [
#             "skydipper"
#         ],
#         "iso": [],
#         "provider": "gee",
#         "published": False,
#         "default": False,
#         "env": "production",
#         "layerConfig": {},
#         "legendConfig": {},
#         "interactionConfig": {},
#         "applicationConfig": {}
#     }
#     new = Layer(token=SKYDIPPER_API_TOKEN, attributes=l_payload)
#     assert new.attributes['name'] == f'Created Layer TEST'
#     assert new.delete(token=SKYDIPPER_API_TOKEN, force=True) == None

### Update Layer
# def test_update_layer():
#     l = Layer(id_hash='25dcb710-6b85-4bfa-b09b-e4c70c33f381')
#     updated = l.update(token=API_TOKEN, update_params={'name': f'Template Layer UPDATED'})
#     assert updated.attributes['name'] == f'Template Layer UPDATED'
#     updated = l.update(token=API_TOKEN, update_params={'name': f'Template Layer'})
#     assert updated.attributes['name'] == 'Template Layer'

### Merge Layer
# def test_merge_layer():
#     staging_layer = Layer('626e08ed-15b5-499a-8a46-9a5cb52d0a30', server='https://staging-api.globalforestwatch.org')
#     staging_layer.update(token=API_TOKEN, update_params={
#         'name': 'Template Layer Staging',
#         'iso': [],
#         'layerConfig': {},
#         'legendConfig': {},
#         'applicationConfig': {},
#         'interactionConfig': {}
#     })
#     production_layer = Layer('25dcb710-6b85-4bfa-b09b-e4c70c33f381')
#     whitelist = [
#             'layerConfig',
#             'legendConfig',
#             'applicationConfig',
#             'interactionConfig',
#             'description',
#             'iso',
#             'application',
#             'provider',
#             'published'
#             ]
#     merged_layer = production_layer.merge(token=API_TOKEN,
#         target_layer=None,
#         target_layer_id='626e08ed-15b5-499a-8a46-9a5cb52d0a30',
#         target_server='https://staging-api.globalforestwatch.org',
#         key_whitelist=whitelist,
#         force=True)
#     merged_atts = {k:v for k,v in merged_layer.attributes.items() if k in whitelist}
#     production_atts =  {k:v for k,v in production_layer.attributes.items() if k in whitelist}
#     assert merged_atts ==  production_atts


#----- Meta Tests -----#

### Delete Meta
# def test_delete_meta():
#     ds = Dataset(id_hash='7cf3fab2-3fbe-4980-b572-712207b2c8c7')
#     m = ds.metadata[0]
#     assert type(m.id) == str
#     deleted_meta = m.delete(token=API_TOKEN)
#     assert deleted_meta == None

### Add Meta
# def test_add_meta():
#     ds = Dataset(id_hash='7cf3fab2-3fbe-4980-b572-712207b2c8c7')
#     payload = {
#     'application': 'gfw',
#     'info': {'citation': 'Example citation',
#         'color': '#fe6598',
#         'description': 'This is an example dataset.',
#         'isLossLayer': True,
#         'name': 'Template Layer'},
#         'language': 'en'
#     }
#     ds.add_metadata(meta_params=payload, token=API_TOKEN)
#     updated_ds = Dataset(id_hash='7cf3fab2-3fbe-4980-b572-712207b2c8c7')
#     assert len(updated_ds.metadata) > 0

### Update Meta
# def test_update_meta():
#     ds = Dataset(id_hash='7cf3fab2-3fbe-4980-b572-712207b2c8c7')
#     m = ds.metadata[0]
#     assert type(m.id) == str
#     payload = {
#     'application': 'gfw',
#     'info': {'citation': 'TEST',
#         'color': '#fe6598',
#         'description': 'TEST',
#         'isLossLayer': False,
#         'name': 'Template Layer'},
#     'language': 'en'}
#     m.update(update_params=payload, token=API_TOKEN)
#     ds = Dataset(id_hash='7cf3fab2-3fbe-4980-b572-712207b2c8c7')
#     updated_m = ds.metadata[0]
#     assert updated_m.attributes['info']['description'] == 'TEST'
#     assert updated_m.attributes['info']['isLossLayer'] == False

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

# def test_create_table():
#     t = Table(id_hash='97546f05-3dce-4dd0-9abf-80fd1bff9cee')
#     assert t.id == '97546f05-3dce-4dd0-9abf-80fd1bff9cee'

# def test_table_head():
#     t = Table(id_hash='97546f05-3dce-4dd0-9abf-80fd1bff9cee')
#     df = t.head()
#     assert len(df) > 0

# def test_table_query():
#     t = Table(id_hash='97546f05-3dce-4dd0-9abf-80fd1bff9cee')
#     df = t.query()
#     assert len(df) == 5

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
