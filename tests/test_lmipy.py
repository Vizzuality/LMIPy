import pytest
from LMIPy import Dataset, Collection, Layer

def test_create_dataset():
    ds = Dataset(id_hash='bb1dced4-3ae8-4908-9f36-6514ae69713f')
    assert ds.id == 'bb1dced4-3ae8-4908-9f36-6514ae69713f'
    assert type(ds.attributes) == dict
    assert len(ds.attributes) > 0
    assert len(ds.vocabulary.attributes) > 0
    assert len(ds.metadata.attributes) > 0

def test_queries_on_datasets():
    ds = Dataset(id_hash='bd5d7924-611e-4302-9185-8054acb0b44b')
    df = ds.query('SELECT fid, ST_ASGEOJSON(the_geom_webmercator) FROM data LIMIT 5')
    assert len(df) > 1

def test_search_collection():
    """Search all gfw collection for an object"""
    col = Collection(search='forest', app=['gfw'])
    assert len(col) > 1