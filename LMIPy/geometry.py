import requests
import folium
import urllib
import json
import random
import geopandas as gpd
from shapely.geometry import shape
import shapely.wkt
import geojson
from .utils import html_box


class Geometry:
    """
    This is the main geometry class.

    Parameters
    ----------
    id_hash: int
        An ID hash of a Geostore from a Vizzuality endpoint.
    attributes: dic
        A valid geojson representation.
    server: str
        The string of the server URL.
    s: obj
        A shapely object.
    """
    def __init__(self, id_hash=None, attributes=None, s=None, parameters=None, server='https://production-api.globalforestwatch.org'):
        self.server = server
        if s:
            attributes = self.create_attributes_from_shapely(s)
        if attributes:
            self.attributes = self.create_geostore_from_geojson(attributes)
        elif parameters:
            self.attributes = self.create_attributes_from_table(parameters)
        else:
            self.id = id_hash
            self.attributes = self.get_geometry()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Geometry {self.id}"

    def _repr_html_(self):
        return html_box(item=self)

    def create_attributes_from_shapely(self, s):
        """Using a Shapely object, we should build a Geometry object."""
        if s.geom_type in ['Polygon', 'Point', 'MultiPoint','MultiPolygon']:
            atts={'geojson': {'type': 'FeatureCollection',
                            'features': [{'type': 'Feature',
                                'properties': {},
                                'geometry': geojson.Feature(geometry=s, properties={}).get('geometry')
                                        }]}}
            return atts
        else:
            raise ValueError('shape object was not of suitable geometry type')

    def create_attributes_from_table(self, parameters=None):
        if not parameters:
            raise ValueError(f'parameters requires!')
        iso = parameters.get('iso', None)
        id1 = parameters.get('adm1', None)
        id2 = parameters.get('adm2', None)
        gadm = parameters.get('gadm', None)
        cartodb_id = parameters.get('id', None)
        table = parameters.get('table', None)
        gadm_ver = {
            '2.7': 'v1',
            '3.6': 'v2'
        }
        if not gadm:
            gadm = '3.6'
        elif gadm not in ['2.7', '3.6']:
            raise ValueError(f'GADM must be 2.7 (v1) or 3.6 (v2)')
        version = gadm_ver[gadm]
        if iso:
            if id2 and id1 and iso:
                url = f'/{version}/geostore/admin/{iso}/{id1}/{id2}'
            elif id1 and iso:
                url = f'/{version}/geostore/admin/{iso}/{id1}'
            elif iso:
                url = f'/{version}/geostore/admin/{iso}'
            else:
                raise ValueError(f'Invalid admin parameters. Requires: iso, adm1, adm2 keys')
        elif table:
            if table and cartodb_id:
                url = f'/{version}/geostore/use/{table}/{int(cartodb_id)}'
            else:
                raise ValueError(f'Invalid table parameters. Requires: table and cartodb_id keys')
        else:
            raise ValueError(f'Invalid parameters! Valid keys: [iso, adm1, adm2] or [table, cartodb_id]')
        header= {
                'Content-Type':'application/json'
                }
        url = self.server + url
        r = requests.get(url, headers=header)
        if r.status_code == 200:
            self.id = r.json().get('data').get('id')
            return r.json().get('data').get('attributes')
        else:
            raise ValueError(f'Recieved response of {r.status_code} from {r.url} when posting to geostore.')

    def create_geostore_from_geojson(self, attributes):
        """Parse valid geojson into a geostore object and register it to a
        Gestore object on a server. Return the object, and instantiate a
        Geometry.
        """
        try:
            body = json.loads(json.dumps(attributes))
        except:
            raise ValueError(f"Unable to pass attributes. Expected valid geojson, recieved: {attributes}")
        header= {
                'Content-Type':'application/json'
                }
        url = self.server + '/v1/geostore'
        r = requests.post(url, headers=header, json=body)
        if r.status_code == 200:
            self.id = r.json().get('data').get('id')
            return r.json().get('data').get('attributes')
        else:
            raise ValueError(f'Recieved response of {r.status_code} from {r.url} when posting to geostore.')

    def get_geometry(self, simplify=False, version='v2'):
        """
        Returns a geostore object by ID from a Vizzuality endpoint.
        """
        hash = random.getrandbits(16)
        url = (f'{self.server}/{version}/geostore/{self.id}?simplify={simplify}&hash={hash}')
        r = requests.get(url)
        if r.status_code == 200:
            return r.json().get('data').get('attributes')
        else:
            raise ValueError(f'Unable to get dataset {self.id} from {r.url}')

    def table(self):
        """
        Returns features as GeoDataFrame
        """
        attributes = self.attributes
        props = {
            **attributes['info'],
            'areaHa': attributes['areaHa'],
            'bbox': attributes['bbox'],
            'id': attributes['hash']
         }
        features = attributes['geojson']['features']
        if len(features) > 0:
            gdf = gpd.GeoDataFrame([{**props, 'geometry': shape(feature['geometry'])} for feature in features]).set_geometry('geometry')
            gdf.crs = {'init' :'epsg:4326'}
            return gdf
        return []

    def shape(self):
        """
        Returns features as a list of Shapely geometries
        """
        features = self.attributes['geojson']['features']
        if len(features) > 0:
            return [shape(feature['geometry']) for feature in features]

    def map(self, image=False):
        """
        Returns a folium choropleth map with styles applied via attributes
        """
        geojson = self.attributes['geojson']
        geometry = geojson['features'][0]['geometry']
        bbox = self.attributes['bbox']
        shapely_geometry = shape(geometry)
        centroid = list(shapely_geometry.centroid.coords)[0][::-1]
        bounds = [bbox[2:][::-1], bbox[:2][::-1]]
        map = folium.Map(
            location=centroid,
            tiles='Mapbox Bright',
        )
        if geometry['type'] == 'Point':
            folium.Marker(
                centroid
            ).add_to(map)
        else:
            folium.GeoJson(
                data=self.table()
                ).add_to(map)
            map.fit_bounds(bounds)
        if image:
            url = f"https://production-api.globalforestwatch.org/v1/recent-tiles?lat={centroid[1]}&lon={centroid[0]}&start=2019-01-01&end=2019-04-01"
            r = requests.get(url)
            if r.status_code == 200:
                image_attributes = r.json()['data']['tiles'][0]['attributes']
                tile_url = image_attributes['tile_url']
                print(f"Image taken {image_attributes['date_time']}\nSource: {image_attributes['instrument']}\nid: {image_attributes['source']}")
                map.add_tile_layer(
                    tiles=tile_url,
                    attr="Live EE tiles"
                )
        return map