import pytest
import random
import os
import os.path
from Skydipper import Dataset, Collection, Layer, Metadata, Vocabulary, Widget, Image, ImageCollection, Geometry, utils

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
    _ = [os.remove(f"{save_path}/{f}") for f in os.listdir(save_path)]
    os.rmdir(save_path)

#----- Dataset Tests -----#

def test_create_dataset():
    ds = Dataset(id_hash='94241cb4-9e91-4a1a-9fcc-993b8ac9c2b7')
    assert ds.id == '94241cb4-9e91-4a1a-9fcc-993b8ac9c2b7'
    assert type(ds.attributes) == dict
    assert len(ds.attributes) > 0

# Test deactivated for now until we add
# Carto or PostGIS to Skydipper
# def test_queries_on_datasets():
#     ds = Dataset(id_hash='94241cb4-9e91-4a1a-9fcc-993b8ac9c2b7')
#     df = ds.query()
#     assert len(df) > 0
#     df = ds.query('SELECT fid, ST_ASGEOJSON(the_geom_webmercator) FROM data LIMIT 5')
#     assert len(df) == 5


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

def test_layer_restore():
    l = Layer(id_hash='e7070d5f-3d38-46b1-86eb-e98782da55dd')
    ds = l.dataset()
    restore_path = f'./tests'
    restored = l.restore(path=restore_path, check=True)
    assert restored.id == 'e7070d5f-3d38-46b1-86eb-e98782da55dd'
    os.remove(restore_path+f"/{ds.id}.json")

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
