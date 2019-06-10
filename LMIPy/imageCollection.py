import requests
from .image import Image

class ImageCollection:
    """
    Returns a list of Image objects based on search criteria.

    This function searches all available images in sentinel and landsat
    and returns an image.

    Parameters
    ----------
    lat: float
        A decimal latitude.

    lon: float
        A decimal longitude.

    band_viz: dic
        A dictionary of bands and visulisation (e.g. {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 0.4}).

    instrument: str
        A string indicating the satellite platform ('sentinel', 'landsat', 'all').

    start: str
        Start date ('YYYY-MM-DD') to bound the search for the satellite images.

    end: str
        End date ('YYYY-MM-DD') to bound the search for the satellite images.
    """

    def __init__(self, lat, lon, start, end, band_viz={'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 0.4},
                    server='https://production-api.globalforestwatch.org'):
        self.lat = lat
        self.lon = lon
        self.start = start
        self.end = end
        self.band_viz = band_viz
        self.server = server
        self.collection = self.get_collection()
        self.iter_position = 0

    def _repr_html_(self):
        str_html = ""
        for n, c in enumerate(self.collection):
            str_html += show(c, n)
            if n < len(self.collection)-1:
                str_html += '<p></p>'
        return str_html

    def __repr__(self):
        rep_string = "["
        for n, c in enumerate(self.collection):
            rep_string += str(f"{n}. {c['type']} {c['id']} {c['attributes']['name']}")
            if n < len(self.collection)-1:
                rep_string += ',\n '
        rep_string += ']'
        return rep_string

    def __iter__(self):
        return self

    def __next__(self):
        if self.iter_position >= len(self.collection):
            self.iter_position = 0
            raise StopIteration
        else:
            self.iter_position += 1
            return self.collection[self.iter_position - 1]

    def __getitem__(self, key):
        items = self.collection[key]
        if type(items) == list:
            return [create_class(item) for item in items]
        else:
            return create_class(items)

    def __len__(self):
        return len(self.collection)

    def get_collection(self):
        """Returns a list of Image objects."""
        url = 'https://production-api.globalforestwatch.org/recent-tiles'
        params = {'lat':self.lat,
                  'lon':self.lon,
                  'start':self.start,
                  'end':self.end,
                  'bands': self.bands}
        r = requests.get(url=url, params=params)
        if(r.status_code != 200):
            raise ValueError(f'Bad response from recent-tiles service: {r.status_code}, {r.json()}')
        try:
            image_list = []
            for item in r.json().get('data').get('tiles'):
                tmp = {'instrument': item.get('attributes').get('instrument'),
                        'date_time': item.get('attributes').get('date_time'),
                        'cloud_score': item.get('attributes').get('cloud_score'),
                        'source': item.get('attributes').get('source'),
                        'bands': self.bands,
                        'server': self.server
                    }
                image_list.append(Image(**tmp))
            return image_list
        except:
            raise ValueError(f'Failed attempting to work with {item}')