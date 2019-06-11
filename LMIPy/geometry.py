import requests
import folium
import urllib
import json
import random
import geopandas as gpd
from shapely.geometry import shape
import shapely.wkt
import geojson
from .utils import html_box, get_geojson_string
import json

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
        if parameters:
            id_hash = self.get_id_from_params(parameters)
        if attributes:
            self.attributes = self.create_geostore_from_geojson(attributes)
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

    def get_id_from_params(self, parameters):
        """
            If you are using this method, you need to use the GFW production server.
        """
        server = "https://production-api.globalforestwatch.org"
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
                raise ValueError(f'Invalid admin parameters: Requires: iso, adm1, adm2 keys')
        elif table:
            if table and cartodb_id:
                url = f'/{version}/geostore/use/{table}/{int(cartodb_id)}'
            else:
                raise ValueError(f'Invalid table parameters. Requires: table and cartodb_id keys')
        else:
            raise ValueError(f'Invalid parameters. Valid keys: [iso, adm1, adm2] or [table, cartodb_id]')
        header= {
                'Content-Type':'application/json'
                }
        url = server + url
        r = requests.get(url, headers=header)
        if r.status_code == 200:
            self.server = server
            return r.json().get('data').get('id')
        else:
            raise ValueError(f'Response of {r.status_code} from {r.url} when calling Geostore.')

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
        else:
            return None

    @staticmethod
    def get_image_url(centroid, band_viz, start, end):
        params = {"lat": centroid[1],
                  "lon": centroid[0],
                  "start": start,
                  "end": end,
                  "band_viz": json.dumps(band_viz)
                  }
        url = "https://production-api.globalforestwatch.org/v1/recent-tiles"
        r = requests.get(url, params=params)
        if r.status_code == 200:
            tile_url = r.json().get('data').get('tiles')[0].get('attributes').get('tile_url')
            return tile_url
        else:
            return None

    def get_composite_url(self, centroid, band_viz, instrument, date_range):
        valid_servers = ['https://production-api.globalforestwatch.org',
                         'https://staging-api.globalforestwatch.org']
        if self.server in valid_servers:
            params = {"geostore": self.id,
                      "instrument": instrument,
                      "date_range": date_range,
                      "band_viz": json.dumps(band_viz)
                     }
            url = "/v1/composite-service"
            url = self.server + url
            r = requests.get(url, params=params)
            if r.status_code == 200:
                tile_url = r.json().get('attributes').get('tile_url')
                return tile_url
        else:
            #url = 'http://localhost:4500/api/v1/composite-service/geom'
            url = "https://production-api.globalforestwatch.org/v1/composite-service/geom"
            payload = json.dumps(self.attributes)
            params = {"instrument": instrument,
                      "date_range": date_range,
                      "band_viz": json.dumps(band_viz)
                     }
            headers = {
                        'Content-Type': "application/json",
                        'cache-control': "no-cache",
                        }
            r = requests.request("POST", url, data=payload, headers=headers, params=params)
            if r.status_code == 200:
                tile_url = r.json().get('attributes').get('tile_url')
                return tile_url

    def map(self, image=False, instrument='sentinel', start='2017-01-01', end='2018-01-01', color='#64D1B8', weight=4):
        """
        Returns a folium map with styles applied via attributes.

        Parameters
        ----------
        image: bool
            If true, a satellite image will be returned related to your geometry.
        instrument: str
            Either landsat or sentinel. Depending on the string a different satellite
            instrument will be used.
        start: str
            Start date for the composite time-range of the satellite image. If point
            data the best intersecting image will be returned within the specified
            time-range. If polygon-type data a cloud-free composite within the
            time-range will be returned.
        end: str
            End date for the composite time-range. If point
            data the best intersecting image will be returned within the specified
            time-range. If polygon-type data a cloud-free composite within the
            time-range will be returned.
        weight: int
            Weight of geom outline. Default = 4.
        color: str
            Hex code for geom outline. Default = #64D1B8.
        """
        if instrument == 'sentinel':
            band_viz = {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 0.4}
        else:
            band_viz = {'bands': ['B4', 'B3', 'B2'], 'min':0, 'max':0.2, 'gamma':[1.3, 1.3, 1.3]}
        geojson = self.attributes['geojson']
        geometry = geojson['features'][0]['geometry']
        bbox = self.attributes['bbox']
        centroid = list(self.shape()[0].centroid.coords)[0][::-1]
        bounds = [bbox[2:][::-1], bbox[:2][::-1]]
        result_map = folium.Map(location=centroid, tiles='OpenStreetMap')
        result_map.fit_bounds(bounds)
        if geometry['type'] == 'Point' or geometry['type'] == 'MultiPoint':
            folium.Marker(centroid).add_to(result_map)
            if image:
                tile_url = self.get_image_url(centroid=centroid, band_viz=band_viz,
                                              start=start, end=end)
                result_map.add_tile_layer(tiles=tile_url, attr=f"{instrument} image")
        else:
            if image:
                date_range = f'{start},{end}'
                tile_url = self.get_composite_url(centroid=centroid, band_viz=band_viz,
                                    instrument=instrument, date_range=date_range)
                result_map.add_tile_layer(tiles=tile_url, attr=f"{instrument} image")
            style_function = lambda x: {
                'fillOpacity': 0.0,
                    'weight': weight,
                    'color': color
                    }
            folium.GeoJson(data=get_geojson_string(geometry), style_function=style_function).add_to(result_map)
        return result_map

    def describe(self, lang='en', app='gfw'):
        """Returns an object with a title and description of a region. Running
        this function adds a property to the object of self.description.

        Parameters
        ----------
        lang: str
            A 2-character language string of the description output
        app: str
            An optional application id string (such as 'gfw') to tailor the description to.
        """
        # If the geostore exists on the right server, send the id, else send the valid geojson attributes
        valid_servers = ['https://production-api.globalforestwatch.org',
                         'https://staging-api.globalforestwatch.org']
        if self.server in valid_servers:
            params = {"geostore": self.id,
                      "lang": lang,
                      "app": app}
            url = "/v1/geodescriber"
            url = self.server + url
            r = requests.get(url, params=params)
            if r.status_code == 200:
                d = {'title': r.json().get('data').get('title'),
                     'description': r.json().get('data').get('description'),
                     'lang': r.json().get('data').get('lang')}
                self.description = d
                print(f"Title: {d.get('title')}")
                print(f"Description: {d.get('description')}")
                return
            else:
                print(f"Description attempt failed: response: {r.status_code}, \n {r.json()}")
                return None
        else:
            url = "https://production-api.globalforestwatch.org/v1/geodescriber/geom"
            payload = json.dumps(self.attributes)
            querystring = {"lang": lang, "app": app}
            headers = {
                        'Content-Type': "application/json",
                        'cache-control': "no-cache",
                        }
            r = requests.request("POST", url, data=payload, headers=headers, params=querystring)
            if r.status_code == 200:
                d = {'title': r.json().get('data').get('title'),
                     'description': r.json().get('data').get('description'),
                     'lang': r.json().get('data').get('lang')}
                self.description = d
                print(f"Title: {d.get('title')}")
                print(f"Description: {d.get('description')}")
                return
            else:
                print(f"Description attempt failed: response: {r.status_code}, \n {r.json()}")
                return None
        return None