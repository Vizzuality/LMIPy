from .lmipy import Auth
from .vocabulary import Vocabulary
from .metadata import Metadata
from .widget import Widget
from .layer import Layer
from .image import Image
from .imageCollection import ImageCollection
from .dataset import Dataset
from .geometry import Geometry
from .collection import Collection
from .table import Table
from pkg_resources import get_distribution

__version__ = get_distribution('LMIPy').version