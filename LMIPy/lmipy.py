import requests
import random
from .utils import html_box


class Metadata:
    """
    This is the main Metadata class.

    Parameters
    ----------
    attributes: dic
        A dictionary holding the attributes of a metadata (which are attached to a Dataset).
    """
    def __init__(self, attributes=None):
        if attributes.get('type') != 'metadata':
            raise ValueError(f"Non metadata attributes passed to Metadata class ({attributes.get('type')})")
        self.id = attributes.get('id')
        self.attributes = attributes.get('attributes')

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Metadata {self.id}"


class Vocabulary:
    """
    This is the main Vocabulary class.

    Parameters
    ----------
    attributes: dic
        A dictionary holding the attributes of a vocabulary (which are attached to a Dataset).
    """
    def __init__(self, attributes=None,):
        if attributes.get('type') != 'vocabulary':
            raise ValueError(f"Non vocabulary attributes passed to Vocabulary class ({attributes.get('type')})")
        self.attributes = attributes.get('attributes')
        self.id = self.attributes.get('resource').get('id')

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Vocabulary {self.id}"
