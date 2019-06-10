from .utils import html_box
import requests
import json
import folium
from shapely.geometry.polygon import LinearRing

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
                 thumb_url = None, bbox=None,
                 server='https://production-api.globalforestwatch.org', type=None,
                 band_viz={'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 0.4}):
        self.source = source
        self.type = 'Image'
        self.instrument = instrument
        self.cloud_score = cloud_score
        self.date_time = date_time
        self.server = server
        self.band_viz = band_viz
        self.bbox = bbox
        self.ring = self.get_ring()
        if thumb_url:
            self.thumb_url = thumb_url
        else:
            self.thumb_url = self.get_thumbs()
        self.attributes = self.get_attributes()

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

    def get_ring(self):
        ring = LinearRing(self.bbox.get('geometry').get('coordinates'))
        return ring

    def get_attributes(self):
        return {'provider': self.source}

    def map(self):
        centroid = [self.ring.centroid.xy[0][0], self.ring.centroid.xy[1][0]]
        #centroid = [28.3, -16.6]
        result_map = folium.Map(location=centroid, tiles='OpenStreetMap')
        #tile_url = self.get_image_url(centroid=centroid, band_viz=band_viz,
        #                                      start=start, end=end)
        #result_map.add_tile_layer(tiles=tile_url, attr=f"{instrument} image")

        result_map.fit_bounds(list(self.ring.bounds))
        style_function = lambda x: {'fillOpacity': 0.0}
        folium.GeoJson(data=self.bbox, style_function=style_function).add_to(result_map)

        return result_map