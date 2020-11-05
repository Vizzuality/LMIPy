import os.path

from LMIPy import Table, utils

try:
    API_TOKEN = os.environ.get("API_TOKEN", None)
except:
    raise ValueError(f"Failed to access keys for test.")


# ----- Table Tests -----#

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


# ----- Utils Tests -----#

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
