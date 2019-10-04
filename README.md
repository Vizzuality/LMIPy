# LMIPy
## The Vizzuality Ecosystem Python Interface

[![Build Status](https://travis-ci.org/Vizzuality/LMIPy.svg?branch=master)](https://travis-ci.org/Vizzuality/LMIPy) [![codecov](https://codecov.io/gh/Vizzuality/LMIPy/branch/master/graph/badge.svg)](https://codecov.io/gh/Vizzuality/LMIPy) [![PyPI](https://img.shields.io/pypi/v/LMIPy.svg?style=flat)](https://pypi.org/project/LMIPy/) ![](https://img.shields.io/pypi/pyversions/LMIPy.svg?style=flat)  ![](https://img.shields.io/pypi/wheel/LMIPy.svg?style=flat) [![Documentation Status](https://readthedocs.org/projects/lmipy/badge/?version=latest)](https://lmipy.readthedocs.io/en/latest/?badge=latest) [![License](https://img.shields.io/badge/License-MIT-brightgreen.svg)](https://github.com/Vizzuality/LMIPy/blob/master/LICENSE)

LMIPy is a Python library with hooks to Jupyter, backed by the [Skydipper API](https://github.com/Skydipper).
It provides many functions related to adding, analysing and working with open geospatial datasets.

## Read the Docs

[Read the docs pages](https://lmipy.readthedocs.io/en/latest/).

## Installation

`pip install LMIPy`

## Use


```
$ python
>>> import LMIPy
```

Create a Dataset object based on an existing ID on default (RW) server.
```
>>> ds = Dataset('044f4af8-be72-4999-b7dd-13434fc4a394')
>>> print(ds)
Dataset 044f4af8-be72-4999-b7dd-13434fc4a394
```

Create a Layer object based on an existing ID on default (RW) server.
```
>>> ly = Layer(id_hash='dc6f6dd2-0718-4e41-81d2-109866bb9edd')
>>> print(ly)
Layer dc6f6dd2-0718-4e41-81d2-109866bb9edd
```

Create a Table object based on an existing ID.
```
>>> table = Table('fbf159d7-a462-4af3-8228-43ee3e3391e7')
# return the head of the table as a geopandas dataframe
>>> df = table.head(5)
# return a query of the table as a geopandas dataframe
>>> result = table.query(sql='SELECT count(*) as my_count FROM data WHERE year > 1991 and year < 1995' )
```

Obtain a collection of objects using a search term.
```
>>> col = Collection(search='tree',object_type=['dataset'], app=['gfw'],limit=5)
>>> print(col)
[Dataset 70e2549c-d722-44a6-a8d7-4a385d78565e, Dataset 897ecc76-2308-4c51-aeb3-495de0bdca79, Dataset 89755b9f-df05-4e22-a9bc-05217c8eafc8, Dataset 83f8365b-f40b-4b91-87d6-829425093da1, Dataset 044f4af8-be72-4999-b7dd-13434fc4a394]
```
Check the docs for more info!
