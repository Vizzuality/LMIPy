import os.path

from LMIPy import Dataset, Widget

try:
    API_TOKEN = os.environ.get("API_TOKEN", None)
except:
    raise ValueError(f"Failed to access keys for test.")


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
    deleted_widget = w.delete(token=API_TOKEN)
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
    staging_widget = Widget(id_hash='66de77eb-dee3-4c56-9ad4-cf68d8b107fd',
                            server='https://staging-api.globalforestwatch.org')
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
    merged_atts = {k: v for k, v in merged_widget.attributes.items() if k in whitelist}
    production_atts = {k: v for k, v in production_widget.attributes.items() if k in whitelist}
    assert merged_atts == production_atts
