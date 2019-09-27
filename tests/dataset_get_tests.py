import os
import os.path

from LMIPy import Dataset

try:
    API_TOKEN = os.environ.get("API_TOKEN", None)
except:
    raise ValueError(f"Failed to access keys for test.")


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
    assert os.path.exists(save_path + f"/{ds.id}.json") == True


def test_dataset_load():
    ds = Dataset(id_hash='897ecc76-2308-4c51-aeb3-495de0bdca79')
    load_path = f'./tests'
    loaded = ds.load(path=load_path, check=True)
    assert loaded.id == '897ecc76-2308-4c51-aeb3-495de0bdca79'
    os.remove(load_path + f"/{ds.id}.json")
