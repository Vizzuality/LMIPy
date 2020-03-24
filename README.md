# Skydipper
## The Vizzuality Ecosystem Python Interface

[![Build Status](https://travis-ci.org/Skydipper/Skydipper.svg?branch=master)](https://travis-ci.org/Skydipper/Skydipper) [![codecov](https://codecov.io/gh/Skydipper/Skydipper/branch/master/graph/badge.svg)](https://codecov.io/gh/Skydipper/Skydipper) [![PyPI](https://img.shields.io/pypi/v/Skydipper.svg?style=flat)](https://pypi.org/project/Skydipper/) ![](https://img.shields.io/pypi/pyversions/Skydipper.svg?style=flat)  ![](https://img.shields.io/pypi/wheel/Skydipper.svg?style=flat) [![Documentation Status](https://readthedocs.org/projects/skydipper/badge/?version=latest)](https://skydipper.readthedocs.io/en/latest/?badge=latest) [![License](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://github.com/Vizzuality/Skydipper/blob/master/LICENSE)

Skydipper is a Python library with hooks to Jupyter, backed by the [Skydipper API](https://github.com/Skydipper).
It provides many functions related to adding, analysing and working with open geospatial datasets.

## Read the Docs

[Read the docs pages](https://skydipper.readthedocs.io/en/latest/).

## Installation

`pip install Skydipper`

## Use


```
$ python
>>> import Skydipper
```

Access a Dataset object based on an existing ID on the Skydipper server.
```
>>> ds = Dataset('044f4af8-be72-4999-b7dd-13434fc4a394')
>>> print(ds)
Dataset 044f4af8-be72-4999-b7dd-13434fc4a394
```

Access a Layer object based on an existing ID on default server.
```
>>> ly = Layer(id_hash='dc6f6dd2-0718-4e41-81d2-109866bb9edd')
>>> print(ly)
Layer dc6f6dd2-0718-4e41-81d2-109866bb9edd
```

Obtain a collection of objects using a search term.
```
>>> col = Collection(name='tree', app=['skydipper','test'],limit=5)
>>> print(col)
[Dataset 70e2549c-d722-44a6-a8d7-4a385d78565e, Dataset 897ecc76-2308-4c51-aeb3-495de0bdca79, Dataset 89755b9f-df05-4e22-a9bc-05217c8eafc8, Dataset 83f8365b-f40b-4b91-87d6-829425093da1, Dataset 044f4af8-be72-4999-b7dd-13434fc4a394]
```
Check the docs for more info!
