from .utils import html_box

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
                 server='https://production-api.globalforestwatch.org',
                 band_viz={'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 0.4}):
        self.source = source
        self.instrument = instrument
        self.cloud_score = cloud_score
        self.date_time = date_time
        self.server = server
        self.band_viz = band_viz
        self.attributes = get_attributes()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Image {self.source}"

    def _repr_html_(self):
        return html_box(item=self)

    def get_attributes(self):
        return 'my attributes'