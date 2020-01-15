from .Skydipper import Vocabulary, Metadata, Widget
from .layer import Layer
from .image import Image
from .imageCollection import ImageCollection
from .dataset import Dataset
from .geometry import Geometry
from .collection import Collection
from pkg_resources import get_distribution

__version__ = get_distribution('Skydipper').version