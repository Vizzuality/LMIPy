from .lmipy import Vocabulary, Metadata, Widget, User
from .layer import Layer
from .image import Image
from .imageCollection import ImageCollection
from .dataset import Dataset
from .geometry import Geometry
from .collection import Collection
from .table import Table
from .gfwDataset import GFWDataset, Auth
from pkg_resources import get_distribution

__version__ = get_distribution('LMIPy').version