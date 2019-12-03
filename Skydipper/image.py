from .utils import html_box, get_geojson_string
import requests
import json
import folium
import numpy as np
import random
import png
import geopandas as gpd
from shapely.geometry.polygon import LinearRing
from shapely.geometry import shape

class Image:
    """
    Main Image Class

    Parameters
    ----------
    bbox: dict
        A dictionary describing the bounding box of the image.

    in: float
        A decimal longitude.

    bands: list
        A list of bands to visulise (e.g. ['b4','b3','b2']).

    instrument: str
        A string indicating the satellite platform ('sentinel', 'landsat', 'all').

    start: str
        Start date ('YYYY-MM-DD') to bound the search for the satellite images.

    end: str
        End date ('YYYY-MM-DD') to bound the search for the satellite images.

    """

    def __init__(self, source=None, instrument=None, date_time=None, cloud_score=None,
                 thumb_url = None, bbox=None, tile_url=None, ring=None,
                 server='https://production-api.globalforestwatch.org', type=None, np_array=None,
                 np_array_bounds=None, band_viz={'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 0.4}):
        self.source = source
        if type == None:
            self.type = 'Image'
        else:
            self.type = type
        self.instrument = instrument
        self.cloud_score = cloud_score
        self.date_time = date_time
        self.server = server
        self.band_viz = band_viz
        self.bbox = bbox
        if ring == None:
            self.ring = self.get_ring()
        else:
            self.ring = ring
        self.tile_url = tile_url
        if thumb_url:
            self.thumb_url = thumb_url
        else:
            self.thumb_url = self.get_thumbs()
        self.attributes = self.get_attributes()
        self.np_array = np_array
        self.np_array_bounds = np_array_bounds

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Image {self.source}"

    def _repr_html_(self):
        return html_box(item=self)

    def get_thumbs(self):
        payload = {'source_data': [{'source': self.source}], 'bands': self.band_viz.get('bands')}
        url = self.server + '/recent-tiles/thumbs'
        r = requests.post(url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
        if  r.status_code == 200:
            return r.json().get('data').get('attributes')[0].get('thumbnail_url')
        else:
            print(f'Failed to get tile {r.status_code}, {r.json()}')
            return None

    def get_image_url(self):
        payload = {'source_data': [{'source': self.source}], 'bands': self.band_viz.get('bands')}
        url = self.server + '/recent-tiles/tiles'
        r = requests.post(url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
        if  r.status_code == 200:
            return r.json().get('data').get('attributes')[0].get('tile_url')
        else:
            print(f'Failed to get tile {r.status_code}, {r.json()}')
            return None

    def get_ring(self):
            coords = self.bbox.get('geometry').get('coordinates', None)
            if coords and any(isinstance(i, list) for i in coords[0]):
                coords = coords[0]
            ring = LinearRing(coords)
            return ring

    def get_attributes(self):
        return {'provider': self.source}

    def map(self, color='#64D1B8', weight=6):
        """
        Returns a folim map of selected image with styles applied.

        Parameters
        ----------
        weight: int
            Weight of geom outline. Default = 6.
        color: str
            Hex code for geom outline. Default = #64D1B8.
        """
        centroid = [self.ring.centroid.xy[1][0], self.ring.centroid.xy[0][0]]
        result_map = folium.Map(location=centroid, tiles='OpenStreetMap')
        geojson_str = get_geojson_string(self.bbox['geometry'])
        folium.GeoJson(
                    data=geojson_str,
                    style_function=lambda x: {
                    'fillOpacity': 0,
                    'weight': weight,
                    'color': color
                    }
                ).add_to(result_map)
        w,s,e,n = list(self.ring.bounds)
        result_map.fit_bounds([[s, w], [n, e]])
        if self.np_array is not None:
            blist = [[self.np_array_bounds[1], self.np_array_bounds[0]],[self.np_array_bounds[3], self.np_array_bounds[2]]]
            image_overlay = folium.raster_layers.ImageOverlay(self.np_array, blist)
            result_map.add_child(image_overlay)
            return result_map
        elif not self.tile_url:
            self.tile_url = self.get_image_url()
        if self.tile_url:
            result_map.add_tile_layer(tiles=self.tile_url, attr=f"{self.instrument} image")
            return result_map

    def classify(self, model_type='random_forest', version=None):
        """
        Classify an Image Object with a selection of pre-trained models. Returns an Image Object.
        Models avaiable for use are Random Forest, Segnet, and Deepvel.

        Parameters
        ----------
        model_type: string
            A string ('random_forest', 'segnet', or 'deepvel') determining which type of classification will be done.

        version: string
            A string specifying the version of the model to use (e.g. 'v1', 'v2', 'v3'). If not provided, the latest
            version of the model will be used.
        """
        if model_type == 'random_forest':
            if self.type in ['Composite Image', 'Classified Image']:
                raise ValueError(f'Unable to perform {model_type} classification on a {self.type}.')
            url = self.server + '/recent-tiles-classifier'
            params = {'img_id': self.attributes.get('provider')}
            r = requests.get(url, params=params)
            if r.status_code == 200:
                classified_tiles = r.json().get('data').get('attributes').get('url')
                tmp = {'instrument': self.instrument,
                        'date_time': self.date_time,
                        'cloud_score': self.cloud_score,
                        'source': self.source,
                        'band_viz': None,
                        'ring': self.ring,
                        'server': self.server,
                        'thumb_url': self.thumb_url,
                        'tile_url': classified_tiles,
                        'type': 'Classified Image',
                        'bbox': self.bbox,
                        'np_array_bounds': self.np_array_bounds
                        }
                return Image(**tmp)
            else:
                raise ValueError(f'Classification failed ({r.status_code} response): {r.json()}')
            return None
        if model_type in ['segnet', 'deepvel']: #and self.type == 'Composite Image':
            if self.type in ['Classified Image']:
                raise ValueError(f"Unable to perform {model_type} classification on a {self.type}.")
            payload = {'thumb_url': self.thumb_url,
                        'model_name': 'deepvel',
                        'model_version': None}
            url = f'https://us-central1-skydipper-196010.cloudfunctions.net/classify'
            headers = {'Content-Type': 'application/json'}
            r = requests.post(url, data=json.dumps(payload), headers=headers)
            if r.status_code == 200:
                image = np.array(r.json().get('output'), dtype=np.uint8)
                hash_code = random.getrandbits(128)
                thumb_path = f"./{str(hash_code)[0:5]}.png"
                p = png.from_array(image, mode='RGB').save(thumb_path)
                tmp = {'instrument': self.instrument,
                    'date_time': self.date_time,
                    'cloud_score': self.cloud_score,
                    'source': self.source,
                    'band_viz': None,
                    'ring': self.ring,
                    'server': self.server,
                    'thumb_url': thumb_path,
                    'tile_url': None,
                    'type': 'Classified Image',
                    'bbox': self.bbox,
                    'np_array': image,
                    'np_array_bounds': self.np_array_bounds
                    }
                return Image(**tmp)
            else:
                raise ValueError(f"Classification service responded with {r.status_code}: {r.url}")
        else:
            raise ValueError(f"Model type {model_type} not reccognised. type property should be one of 'random_forest', 'segnet', or 'deepvel'")