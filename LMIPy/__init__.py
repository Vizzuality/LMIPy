from .lmipy import Vocabulary, Metadata
from .layer import Layer
from .dataset import Dataset
from .collection import Collection
from .table import Table
from pkg_resources import get_distribution

__version__ = get_distribution('LMIPy').version