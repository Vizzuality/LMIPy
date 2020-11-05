import os
import os.path

from LMIPy import Layer, Geometry

try:
    API_TOKEN = os.environ.get("API_TOKEN", None)
except:
    raise ValueError(f"Failed to access keys for test.")


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
    assert os.path.exists(save_path + f"/{ds.id}.json") == True


def test_layer_load():
    l = Layer(id_hash='25dcb710-6b85-4bfa-b09b-e4c70c33f381')
    ds = l.dataset()
    load_path = f'./tests'
    loaded = l.load(path=load_path, check=True)
    assert loaded.id == '25dcb710-6b85-4bfa-b09b-e4c70c33f381'
    os.remove(load_path + f"/{ds.id}.json")
