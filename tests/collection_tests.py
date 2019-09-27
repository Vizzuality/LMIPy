import os
import os.path

from LMIPy import Collection

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
    _ = [os.remove(save_path + f"/{f}") for f in os.listdir(save_path)]
    os.rmdir(save_path)
