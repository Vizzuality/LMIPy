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
from .user import User

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
    def __init__(self, id_hash=None, attributes=None, s=None, parameters=None, server='https://api.skydipper.com'):
        self.server = server
        self.User = User()
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
        """
        raise ValueError(f'Params functionality not supported in Skydipper.')

    def create_geostore_from_geojson(self, attributes):
        """Parse valid geojson into a geostore object and register it to a
        Gestore object on a server. Return the object, and instantiate a
        Geometry.
        """
        try:
            body = json.loads(json.dumps(attributes))
        except:
            raise ValueError(f"Unable to pass attributes. Expected valid geojson, recieved: {attributes}")
        url = self.server + '/v1/geostore'
        r = requests.post(url, headers=self.User.headers, json=body)
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
        r = requests.get(url, headers=self.User.headers)
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
        params = {"lon": centroid[1],
                  "lat": centroid[0],
                  "start": start,
                  "end": end,
                  "band_viz": json.dumps(band_viz)
                  }
        url = "https://api.skydipper.com/v1/recent-imagery"
        r = requests.get(url, params=params, headers=self.User.headers)
        if r.status_code == 200:
            tile_url = r.json().get('data').get('tiles')[0].get('attributes').get('tile_url')
            return tile_url
        else:
            return None

    def get_composite_url(self, centroid, band_viz, instrument, date_range):
        valid_servers = ["https://api.skydipper.com"]
        if self.server in valid_servers:
            params = {"geostore": self.id,
                      "instrument": instrument,
                      "date_range": date_range,
                      "band_viz": json.dumps(band_viz)
                     }
            url = "/v1/composite-service"
            url = self.server + url
            r = requests.get(url, params=params, headers=self.User.headers)
            if r.status_code == 200:
                tile_url = r.json().get('attributes').get('tile_url')
                return tile_url
        else:
            url = "https://api.skydipper.com/v1/composite-service/geom"
            payload = json.dumps(self.attributes)
            params = {"instrument": instrument,
                      "date_range": date_range,
                      "band_viz": json.dumps(band_viz)
                     }
            r = requests.request("POST", url, data=payload, headers=self.User.headers, params=params)
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
        result_map = folium.Map(location=centroid, tiles='OpenStreetMap', zoom_start=6)
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
        valid_servers = ["https://api.skydipper.com"]
        if self.server in valid_servers:
            params = {"geostore": self.id,
                      "lang": lang,
                      "app": app}
            url = f"{self.server}/v1/geodescriber"
            r = requests.get(url, params=params, headers=self.User.headers)
            if r.status_code == 200:
                if self.server == 'https://api.skydipper.com':
                    tmp = r.json().get('attributes')
                else:
                    tmp = r.json().get('data')
                d = {'title': tmp.get('title'),
                    'description': tmp.get('description'),
                    'lang': tmp.get('lang')}
                self.description = d
                print(f"Title: {d.get('title')}")
                return
            else:
                print(f"Description attempt failed: response: {r.status_code}, \n {r.json()}")
                return None
        else:
            url = "https://api.skydipper.com/v1/geodescriber/geom"
            payload = json.dumps(self.attributes)
            querystring = {"lang": lang, "app": app}
            r = requests.request("POST", url, data=payload, headers=self.User.headers, params=querystring)
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

    def simplify(self, tolerance, preserve_topology=True):
        """
        Returns a simplified geometry produced by the Douglas-Peucker
        algorithm. Coordinates of the simplified geometry will be no more than the
        tolerance distance from the original. Unless the topology preserving
        option is used, the algorithm may produce self-intersecting or
        otherwise invalid geometries. Returns a Geostore object.

        Parameters
        ----------
        tolerance: int
            Tolerance value
        preserve_topology: bool
            Should the topology be presevered, True or False.
        """
        s = self.shape()[0]
        tmp_s = s.simplify(tolerance=tolerance, preserve_topology=True)
        return Geometry(s=tmp_s)