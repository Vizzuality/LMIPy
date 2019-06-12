import pytest
from LMIPy import Dataset, Collection, Layer, Metadata, Vocabulary, Widget, Image, ImageCollection, Geometry

def test_create_dataset():
    ds = Dataset(id_hash='bb1dced4-3ae8-4908-9f36-6514ae69713f')
    assert ds.id == 'bb1dced4-3ae8-4908-9f36-6514ae69713f'
    assert type(ds.attributes) == dict
    assert len(ds.attributes) > 0

def test_queries_on_datasets():
    ds = Dataset(id_hash='bd5d7924-611e-4302-9185-8054acb0b44b')
    df = ds.query('SELECT fid, ST_ASGEOJSON(the_geom_webmercator) FROM data LIMIT 5')
    assert len(df) > 1

def test_search_collection():
    """Search all gfw collection for an object"""
    col = Collection(search='forest', app=['gfw'])
    assert len(col) > 1

def test_layer_creation():
    ly = Layer(id_hash='dc6f6dd2-0718-4e41-81d2-109866bb9edd')
    assert ly is not None

def test_access_vocab():
    ds = Dataset(id_hash='bb1dced4-3ae8-4908-9f36-6514ae69713f')
    assert type(ds.vocabulary) == list
    assert len(ds.vocabulary) > 0

def test_access_meta():
    ds = Dataset(id_hash='bb1dced4-3ae8-4908-9f36-6514ae69713f')
    assert type(ds.metadata) == list
    assert len(ds.metadata) > 0

def test_access_meta_attributes():
    ds = Dataset('044f4af8-be72-4999-b7dd-13434fc4a394')
    meta = ds.metadata[0].attributes
    assert type(meta) is dict

def test_access_widget():
    ds = Dataset(id_hash='dcd1e9c7-1370-404e-8816-eaa51d4b1a39')
    assert type(ds.widget) == list
    assert len(ds.widget) > 0

def test_image_collection_search():
    ic = ImageCollection(lon=28.271979, lat=-16.457814, start='2018-06-01', end='2018-06-20')
    assert len(ic) > 0

def test_geometry_create_and_describe():
    atts={'geojson': {'type': 'FeatureCollection',
                        'features': [{'type': 'Feature',
                            'properties': {},
                            'geometry': {'type': 'Polygon',
                            'coordinates': [[[-52.16308593749999, -1.669685500986571],
                            [-46.9775390625, -1.669685500986571],
                            [-46.9775390625, 0.7909904981540058],
                            [-52.16308593749999, 0.7909904981540058],
                            [-52.16308593749999, -1.669685500986571]]]}}]}}
    g = Geometry(attributes=atts)
    g.describe()
    assert g.description.get('title') is not None