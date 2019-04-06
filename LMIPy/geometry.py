import requests
import folium
import urllib
import json
import random
import geopandas as gpd
from shapely.geometry import shape
from .utils import html_box


class Geometry:
    """
    This is the main Layer class.

    Parameters
    ----------
    id_hash: int
        An ID hash.
    attributes: dic
        A dictionary holding the attributes of a dataset.
    server: str
        A string of the server URL.
    """
    def __init__(self, id_hash=None, attributes=None, server='http://production-api.globalforestwatch.org'):
        self.server = server
        if not id_hash:
            if attributes:
                self.id = attributes.get('id', None)
                self.attributes = attributes.get('attributes', None)
            else:
                self.id = None
                self.attributes = None
        else:
            self.id = id_hash
            self.attributes = self.get_geometry()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Geometry {self.id}"

    def _repr_html_(self):
        return html_box(item=self)

    def get_geometry(self, simplify=False):
        """
        Returns a layer from a Vizzuality API.
        """
        hash = random.getrandbits(16)
        url = (f'{self.server}/v2/geostore/{self.id}?simplify={simplify}&hash={hash}')
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

    def map(self):
        """
        Returns a folim choropleth map with styles applied via attributes
        """
        geojson = self.attributes['geojson']
        geometry = geojson['features'][0]['geometry']
        fields = [
            *list(self.attributes['info'].keys()),
            'areaHa',
            'bbox',
            'id'
        ]

        bbox = self.attributes['bbox']
        shapely_geometry = shape(geometry)
        centroid = list(shapely_geometry.centroid.coords)[0][::-1]
        bounds = [bbox[2:][::-1], bbox[:2][::-1]]

        map = folium.Map(
            location=centroid,
            tiles='Mapbox Bright',
        )

        folium.GeoJson(
            data=self.table(),
            ).add_to(map)

        map.fit_bounds(bounds)

        return map