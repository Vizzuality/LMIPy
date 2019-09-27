import os.path

from LMIPy import Dataset, Geometry

try:
    API_TOKEN = os.environ.get("API_TOKEN", None)
except:
    raise ValueError(f"Failed to access keys for test.")


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

# ----- Geometry Tests -----#

def test_geometry_create_and_describe():
    atts = {'geojson': {'type': 'FeatureCollection',
                        'features': [{'type': 'Feature',
                                      'properties': {},
                                      'geometry': {'type': 'Polygon',
                                                   'coordinates': [[[28.00004197633704, 49.710191987352424],
                                                                    [28.00004197633704, 48.18737001395745],
                                                                    [27.750103011493355, 48.18737001395745],
                                                                    [27.50016404664967, 48.18737001395745],
                                                                    [27.25022508180598, 48.18737001395745],
                                                                    [26.99982835329041, 48.18737001395745],
                                                                    [26.99982835329041, 49.710191987352424],
                                                                    [27.25022508180598, 49.710191987352424],
                                                                    [27.50016404664967, 49.710191987352424],
                                                                    [27.750103011493355, 49.710191987352424],
                                                                    [28.00004197633704, 49.710191987352424]]]}}]}}
    g = Geometry(attributes=atts)
    g.describe()
    assert g.description.get('title') is not None
