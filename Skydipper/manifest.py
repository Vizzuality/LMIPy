import python_jsonschema_objects as pjs
from datetime import datetime
import iso8601


class ImageManifest:
    """
    Returns an image manifest object.

    This function builds an object that can be serialized as an earthengine manifest JSON.

    Parameters
    ----------
    name: string
        Path of the earthengine asset.

    uris_list: list of list of str
        List of list of google cloud storage image paths.

    dt_list: list of str
        A list of tileset data types; "DATA_TYPE_UNSPECIFIED","INT8","UINT8","INT16","UINT16","INT32","UINT32","FLOAT32","FLOAT64"

    crs_list: str
        A list of tileset CRS codes; "EPSG:<code>"

    id_list: str
        List of band (and potentially tileset) names.

    md_list: list of list num
        List of band list of missing data values.    

    pp_list: list str
        List of band pyramiding policy codes; "MEAN", "MODE", "SAMPLE".

    tsbi_list: list int
        List of tileset band indexes to use for creating asset.

    properties: dict
        A dictionary of (free) properties to add to the asset.

    start_time: str
        The image aquisition start time (ISO8601)
    end_time: str
        The image aquisition end time (ISO8601)                 
    footprint: dict
        Footprint.
    """

    def __init__(self, name,
                 uris_list, dt_list, crs_list,
                 id_list, md_list, pp_list, tsbi_list,
                 properties_dict,
                 start_time, end_time,
                 footprint=None
                 ):
        self.name = name
        self.bands = create_band_list(id_list, md_list, pp_list, tsbi_list)
        self.start_time = create_timestamp(start_time)
        self.end_time = create_timestamp(end_time)
        if len(uris_list) == 1:
            self.tilesets = create_tilesets_list(
                uris_list, dt_list, crs_list, id_list=None)
        else:
            self.tilesets = create_tilesets_list(
                uris_list, dt_list, crs_list, id_list=id_list)

        self.properties = create_properties_dict(properties_dict)
        self.footprint = footprint

    # Define the earthengine manifest schema
# See https://developers.google.com/earth-engine/image_manifest
# Common objects
# Timestamp
# https://developers.google.com/earth-engine/image_manifest#time_start
# https://developers.google.com/earth-engine/image_manifest#time_end
timestamp_schema = {
    "type": "object",
    "title": "Timestamp",
    "required": [
        "seconds"
    ],
    "properties": {
        "seconds": {
            "type": "integer",
            "default": 0,
            "examples": [
                123
            ]
        }
    }
}

# PyramidingPolicy
# https://developers.google.com/earth-engine/image_manifest#bands%5Bi%5D.pyramiding_policy
pyramiding_policy_schema = {
    "type": "string",
    "title": "PyramidingPolicy",
    "enum": ["MEAN", "MODE", "SAMPLE"],
    "default": None,
    "examples": [
        "<string>"
    ],
    "pattern": "^(.*)$"
}

# MissingData
# https://developers.google.com/earth-engine/image_manifest#missing_data.values
missing_data_schema = {
    "type": "object",
    "title": "MissingData",
    "required": [
        "values"
    ],
    "properties": {
        "values": {
            "type": "array",
            "items": {
                "type": "number",
                "default": None,
                "examples": [
                    -999
                ]
            }
        }
    }
}

# ID
# A tileset or band ID
# https://developers.google.com/earth-engine/image_manifest#bands%5Bi%5D.id
# https://developers.google.com/earth-engine/image_manifest#tilesets%5Bi%5D.id
id_schema = {
    "type": "string",
    "title": "ID",
    "default": "",
    "examples": [
        "<string>"
    ],
    "pattern": "^(.*)$"
}

# Sources
# Uris
# https://developers.google.com/earth-engine/image_manifest#tilesets%5Bi%5D.sources%5Bj%5D.uris
uris_schema = {
    "type": "array",
    "title": "Uris",
    "items": {
        "type": "string",
        "default": "",
        "examples": [
            "<string>"
        ],
        "pattern": "^(.*)$"
    }
}

# AffineTransform
# https://developers.google.com/earth-engine/image_manifest#tilesets%5Bi%5D.sources%5Bj%5D.affine_transform
affine_transform_schema = {
    "type": "object",
    "title": "AffineTransform",
    "required": [
        "scale_x",
        "shear_x",
        "translate_x",
        "shear_y",
        "scale_y",
        "translate_y"
    ],
    "properties": {
        "scale_x": {
            "type": "number",
            "default": 0.0,
            "examples": [
                0.1
            ]
        },
        "shear_x": {
            "type": "number",
            "default": 0.0,
            "examples": [
                0.1
            ]
        },
        "translate_x": {
            "type": "number",
            "default": 0.0,
            "examples": [
                0.1
            ]
        },
        "shear_y": {
            "type": "number",
            "default": 0.0,
            "examples": [
                0.1
            ]
        },
        "scale_y": {
            "type": "number",
            "default": 0.0,
            "examples": [
                0.1
            ]
        },
        "translate_y": {
            "type": "number",
            "default": 0.0,
            "examples": [
                0.1
            ]
        }
    }
}

sources_schema = {
    "type": "array",
    "title": "Sources",
    "items": {
        "type": "object",
        "required": [
            "uris"
        ],
        "properties": {
            "uris": uris_schema,
            "affine_transform": affine_transform_schema
        }
    }
}

# Tilesets
# https://developers.google.com/earth-engine/image_manifest#tilesets_1
# DataType
# https://developers.google.com/earth-engine/image_manifest#tilesets%5Bi%5D.data_type
data_type_schema = {
    "type": "string",
    "title": "DataType",
    "enum": ["DATA_TYPE_UNSPECIFIED", "INT8", "UINT8", "INT16", "UINT16", "INT32", "UINT32", "FLOAT32", "FLOAT64"],
    "default": None,
    "examples": [
        "<string>"
    ],
    "pattern": "^(.*)$"
}

# CRS
# https://developers.google.com/earth-engine/image_manifest#tilesets%5Bi%5D.crs
crs_schema = {
    "type": "string",
    "title": "CRS",
    "default": "",
    "examples": [
        "<string>"
    ],
    "pattern": "^(.*)$"
}

tilesets_schema = {
    "type": "array",
    "title": "Tilesets",
    "items": {
        "type": "object",
        "required": [
            "sources"
        ],
        "properties": {
            "data_type": data_type_schema,
            "id": id_schema,
            "crs": crs_schema,
            "sources": sources_schema
        }
    }
}

# MaskBands
# https://developers.google.com/earth-engine/image_manifest#mask_bands
# BandIds
# https://developers.google.com/earth-engine/image_manifest#mask_bands%5Bi%5D.band_ids
band_ids_schema = {
    "type": "array",
    "title": "BandIds",
    "items": id_schema
}

mask_bands_schema = {
    "type": "array",
    "title": "MaskBands",
    "items": {
        "type": "object",
        "required": [
            "tileset_id"
        ],
        "properties": {
            "tileset_id": id_schema,
            "band_ids": band_ids_schema
        }
    }
}

# Footprint
# A dictionary defining the properties of the footprint of all valid pixels in an image.
# If empty, the default footprint is the entire image.
# https://developers.google.com/earth-engine/image_manifest#footprint
footprint_schema = {
    "type": "object",
    "title": "Footprint",
    "required": [
        "points",
        "band_id"
    ],
    "properties": {
        "points": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "x",
                    "y"
                ],
                "properties": {
                    "x": {
                        "type": "number",
                        "default": 0.0,
                        "examples": [
                            0.1
                        ]
                    },
                    "y": {
                        "type": "number",
                        "default": 0.0,
                        "examples": [
                            0.1
                        ]
                    }
                }
            }
        },
        "band_id": id_schema
    }
}

# Bands
# https://developers.google.com/earth-engine/image_manifest#bands_1
# TilesetBandIndex
# https://developers.google.com/earth-engine/image_manifest#bands%5Bi%5D.tileset_band_index
tileset_band_index_schema = {
    "type": "integer",
    "title": "TilesetBandIndex",
    "default": 0,
    "examples": [
        0
    ]
}

bands_schema = {
    "type": "array",
    "title": "Bands",
    "items": {
        "type": "object",
        "title": "Band",
        "required": [
            "id",
            "tileset_band_index",
            "missing_data",
            "pyramiding_policy"
        ],
        "properties": {
            "id": id_schema,
            "tileset_id": id_schema,
            "tileset_band_index": tileset_band_index_schema,
            "missing_data": missing_data_schema,
            "pyramiding_policy": pyramiding_policy_schema
        }
    }
}

# Properties
# https://developers.google.com/earth-engine/image_manifest#properties
# An arbitrary flat dictionary of key-value pairs.
# Keys must be strings and values can be either numbers or strings.
# List values are not yet supported for user-uploaded assets.
# We define a number of properties based on https://schema.org/Dataset
properties_schema = {
    "type": "object",
    "title": "Properties",
    "properties": {
        "name": {
            "type": "string",
            "default": "",
            "examples": [
                "<string>"
            ],
            "pattern": "^(.*)$"
        },
        "alternateName": {
            "type": "string",
            "default": "",
            "examples": [
                "<string>"
            ],
            "pattern": "^(.*)$"
        },
        "description": {
            "type": "string",
            "default": "",
            "examples": [
                "<string>"
            ],
            "pattern": "^(.*)$"
        },
        "provider": {
            "type": "string",
            "default": "",
            "examples": [
                "<string>"
            ],
            "pattern": "^(.*)$"
        },
        "citation": {
            "type": "string",
            "default": "",
            "examples": [
                "<string>"
            ],
            "pattern": "^(.*)$"
        },
        "creator": {
            "type": "string",
            "default": "",
            "examples": [
                "<string>"
            ],
            "pattern": "^(.*)$"
        },
        "keywords": {
            "type": "string",
            "default": "",
            "examples": [
                "<string>; <string>; <string>"
            ],
            "pattern": "^(.*)$"
        },
        "temporalCoverage": {
            "type": "string",
            "default": "",
            "examples": [
                "<string>"
            ],
            "pattern": "^(.*)$"
        },
        "variableMeasured": {
            "type": "string",
            "default": "",
            "examples": [
                "<string>"
            ],
            "pattern": "^(.*)$"
        },
        "unitText": {
            "type": "string",
            "default": "",
            "examples": [
                "<string>"
            ],
            "pattern": "^(.*)$"
        },
        "measurementTechnique": {
            "type": "string",
            "default": "",
            "examples": [
                "<string>"
            ],
            "pattern": "^(.*)$"
        },
        "version": {
            "type": "string",
            "default": "",
            "examples": [
                "<string>"
            ],
            "pattern": "^(.*)$"
        },
        "url": {
            "type": "string",
            "default": "",
            "examples": [
                "<string>"
            ],
            "pattern": "^(.*)$"
        },
        "sameAs": {
            "type": "string",
            "default": "",
            "examples": [
                "<string>"
            ],
            "pattern": "^(.*)$"
        },
        "identifier": {
            "type": "string",
            "default": "",
            "examples": [
                "<string>"
            ],
            "pattern": "^(.*)$"
        },
        "license": {
            "type": "string",
            "default": "",
            "examples": [
                "<string>"
            ],
            "pattern": "^(.*)$"
        }
    }
}

# ImageManifest
# https://developers.google.com/earth-engine/image_manifest#manifest-field-definitions
# Note docs use time_end, time_start, but start_time and end_time are required?
# Name
name_schema = {
    "type": "string",
    "title": "Name",
    "default": "",
    "examples": [
        "<string>"
    ],
    "pattern": "^(.*)$"
}

# UriPrefix
uri_prefix_schema = {
    "type": "string",
    "title": "UriPrefix",
    "default": "",
    "examples": [
        "<string>"
    ],
    "pattern": "^(.*)$"
}

image_manifest_schema = {
    "type": "object",
    "title": "ImageManifest",
    "definitions": {
        "Timestamp": timestamp_schema,
        "PyramidingPolicy": pyramiding_policy_schema,
        "MissingData": missing_data_schema,
        "ID": id_schema,
        "Uris": uris_schema,
        "AffineTransform": affine_transform_schema,
        "Sources": sources_schema,
        "DataType": data_type_schema,
        "CRS": crs_schema,
        "Tilesets": tilesets_schema,
        "BandIds": band_ids_schema,
        "MaskBands": mask_bands_schema,
        "Bands": bands_schema,
        "TilesetBandIndex": tileset_band_index_schema,
        "Footprint": footprint_schema,
        "Properties": properties_schema,
        "Name": name_schema,
        "UriPrefix": uri_prefix_schema
    },
    "required": [
        "name",
        "tilesets",
        "bands",
        "start_time",
        "end_time",
        "properties"
    ],
    "properties": {
        "name": {"$ref": "#/definitions/Name"},
        "tilesets": {"$ref": "#/definitions/Tilesets"},
        "bands": {"$ref": "#/definitions/Bands"},
        "mask_bands": {"$ref": "#/definitions/MaskBands"},
        "footprint": {"$ref": "#/definitions/Footprint"},
        "missing_data": {"$ref": "#/definitions/MissingData"},
        "pyramiding_policy": {"$ref": "#/definitions/PyramidingPolicy"},
        "uri_prefix": {"$ref": "#/definitions/UriPrefix"},
        "start_time": {"$ref": "#/definitions/Timestamp"},
        "end_time": {"$ref": "#/definitions/Timestamp"},
        "properties": {"$ref": "#/definitions/Properties"}
    }
}

# Build classes


manifest = pjs.ObjectBuilder(image_manifest_schema).build_classes(
    named_only=False, standardize_names=False)

"""# Constructor methods"""

# Build footprint


def create_footprint(band_id, points):
    """
    Create a footprint object

    https://developers.google.com/earth-engine/image_manifest#footprint.points

    @arg band_id The band id that contains the CRS to define the points
    @arg args A list of dictionaries with the x,y values that define describe a 
    ring which forms the exterior of a simple polygon that must contain the 
    centers of all valid pixels of the image

    @return A footprint object

    @example
    band_id = "test"
    points = [{"x": 0.5,"y": 0.5},{"x": 0.5,"y": 1.5},{"x": 1.5,"y": 1.5},{"x": 1.5,"y": 0.5},{"x": 0.5,"y": 0.5}]
    print(create_footprint(band_id, points).serialize())
    """
    return(manifest.Footprint(band_id=band_id, points=points))


# Example:
band_id = "test"
points = [{"x": 0.5, "y": 0.5}, {"x": 0.5, "y": 1.5}, {
    "x": 1.5, "y": 1.5}, {"x": 1.5, "y": 0.5}, {"x": 0.5, "y": 0.5}]
print(create_footprint(band_id, points).serialize())

# Build affine transform


def create_affine_transform(args):
    """
    Create an affine_transfom object

    @arg args A dictionary with affine transformation properties; "scale_x", "shear_x", "translate_x", "shear_y", "scale_y", "translate_y"

    @return An affine transform object

    @example
    args = {"scale_x": 0.0, "shear_x": 0.0, "translate_x": 0.0, "shear_y": 0.0, "scale_y": 0.0, "translate_y": 0.0}
    print(create_affine_transform(args).serialize())
    """
    return(manifest.AffineTransform(**args))


# Example:
args = {"scale_x": 0.0, "shear_x": 0.0, "translate_x": 0.0,
        "shear_y": 0.0, "scale_y": 0.0, "translate_y": 0.0}
print(create_affine_transform(args).serialize())

# Build mask_bands


def create_mask_bands(tileset_id_list, band_ids_list=None):
    """
    Create a mask_bands object

    Can be used for 2 cases; 
    + To use a geotiff as a mask for all bands, band_ids_list = None
    + To use a geotiff as a mask for specific bands, band_ids_list = None
    https://developers.google.com/earth-engine/image_manifest#mask_bands  

    @arg tileset_id_list List of tileset ids that contain the mask (note only last band is used), e.g., ["mask1", "mask2"]
    @arg band_ids_list Optional list of list of bands to apply the mask too, e.g., [["band1"]], ["band2", "band3"]] 

    @returns A mask_bands object
    @example
    tileset_id_list = ["mask1"]  
    print(create_mask_bands(tileset_id_list, band_ids_list=None).serialize())
    tileset_id_list = ["mask1", "mask2"]  
    print(create_mask_bands(tileset_id_list, band_ids_list=None).serialize())
    band_ids_list = [["band1"], ["band2"]]  
    print(create_mask_bands(tileset_id_list, band_ids_list=band_ids_list).serialize())
    band_ids_list = [["band1", "band2"], ["band3"]]  
    print(create_mask_bands(tileset_id_list, band_ids_list=band_ids_list).serialize())
    """

    if band_ids_list:
        out = [{"tileset_id": tmp1, "band_ids": tmp2}
               for tmp1, tmp2 in zip(tileset_id_list, band_ids_list)]
    else:
        out = [{"tileset_id": tmp1} for tmp1 in tileset_id_list]
    return(manifest.MaskBands(out))


# Example:
tileset_id_list = ["mask1"]
print(create_mask_bands(tileset_id_list, band_ids_list=None).serialize())
tileset_id_list = ["mask1", "mask2"]
print(create_mask_bands(tileset_id_list, band_ids_list=None).serialize())
band_ids_list = [["band1"], ["band2"]]
print(create_mask_bands(tileset_id_list, band_ids_list=band_ids_list).serialize())
band_ids_list = [["band1", "band2"], ["band3"]]
print(create_mask_bands(tileset_id_list, band_ids_list=band_ids_list).serialize())

# Build band_list


def create_band_list(id_list, md_list, pp_list, tsbi_list):
    """
    Create a bands_list object

    Can be used for 2 cases; when id_list and the properties lists have equal length
    band objects are created using the elements from each list in order. When id_list
    is > the properties lists, the first property is added to each band.  

    @arg id_list List of band id strings
    @arg md_list List of list with missing_data numbers
    @arg pp_list List of pyramiding policy strings ("MEAN", "MODE", or "SAMPLE")
    @arg tsbi_list List of tileset band index integers

    @returns A band_list object

    @example
    id_list = ["band1"]; md_list = [[-999]]; pp_list = ["MEAN"]; tsbi_list = [3]   
    print(create_band_list(id_list, md_list, pp_list, tsbi_list).serialize())
    id_list = ["band1", "band2"]; md_list = [[-999]]; pp_list = ["MEAN"]; tsbi_list = [3]
    print(create_band_list(id_list, md_list, pp_list, tsbi_list).serialize())
    id_list = ["band1", "band2"]; md_list = [[-999], [0]]; pp_list = ['MEAN', 'MODE']; tsbi_list = [3, 1]
    print(create_band_list(id_list, md_list, pp_list, tsbi_list).serialize())
    """

    # Check number of list elements
    idl = len(id_list)
    mdl = len(md_list)
    ppl = len(pp_list)
    tsbil = len(tsbi_list)

    # Check case
    # should be all equal OR exactly 1 of md, pp, and tsbi
    all_equal = idl == mdl == ppl == tsbil
    #print("All_equal", all_equal)
    many_ids = idl > 1
    #print("Many_ids", many_ids)
    single_props = mdl == 1 & ppl == 1 & tsbil == 1
    #print("Single_props", single_props)

    # Equal number of bands and properties
    if all_equal:
        #print(f"Creating {idl} band(s) with {ppl} properties")
        out = [manifest.Band(**{
            "id": manifest.ID(tmp1),
            "missing_data": manifest.MissingData(values=tmp2),
            "pyramiding_policy": manifest.PyramidingPolicy(tmp3),
            "tileset_band_index": manifest.TilesetBandIndex(tmp4)
        })
            for tmp1, tmp2, tmp3, tmp4 in zip(id_list, md_list, pp_list, tsbi_list)]

    # Many bands single property
    if many_ids & single_props:
        #print(f"Creating {idl} bands with {ppl} properties")
        out = [manifest.Band(**{
            "id": manifest.ID(tmp1),
            "missing_data": manifest.MissingData(values=md_list[0]),
            "pyramiding_policy": manifest.PyramidingPolicy(pp_list[0]),
            "tileset_band_index": manifest.TilesetBandIndex(tsbi_list[0])
        })
            for tmp1 in id_list]

    # Return bands_list object
    return(manifest.Bands(out))


# Example:
id_list = ["band1"]
md_list = [[-999]]
pp_list = ["MEAN"]
tsbi_list = [3]
print(create_band_list(id_list, md_list, pp_list, tsbi_list).serialize())
id_list = ["band1", "band2"]
md_list = [[-999]]
pp_list = ["MEAN"]
tsbi_list = [3]
print(create_band_list(id_list, md_list, pp_list, tsbi_list).serialize())
id_list = ["band1", "band2"]
md_list = [[-999], [0]]
pp_list = ['MEAN', 'MODE']
tsbi_list = [3, 1]
print(create_band_list(id_list, md_list, pp_list, tsbi_list).serialize())

# Build sources_list
# can be multiple uris for image mosaicing


def create_source_list(uris_list):
    """
    Create a source_list object

    Adds list of uris to soure_list object.  

    @arg uris_list List of list of GCS uris

    @returns A source_list object
    @example
    uris_list = [["gs://my-bucket/my-image-1.tif"], ["gs://my-bucket/my-image-2.tif"]]
    print(create_source_list(uris_list).serialize())
    """
    return(manifest.Sources(
        [{"uris": manifest.Uris([tmp1])} for tmp1 in uris_list]
    ))


# Example:
uris_list = ["gs://my-bucket/my-image-1.tif", "gs://my-bucket/my-image-2.tif"]
print(create_source_list(uris_list).serialize())

# Build tilesets_list


def create_tilesets_list(uris_list, dt_list, crs_list, id_list=None):
    """
    Create a tilesets_list object

    Adds lists of ids and uris to tilesets_list object.  

    @arg uris_list List of lists of GCS uris, for each tileset (band) e.g., [[["gs://my-bucket/my-image-1.tif"], ["gs://my-bucket/my-image-2.tif"]]]
    @arg id_list Optional list of tileset id names, these link to band names? e.g., ["band1", "band2"]


    @returns A source_list object
    @example
    # Single tileset (mosaic)
    dt_list = ["FLOAT32"]
    crs_list = ["EPSG:4326"]
    uris_list = [["gs://my-bucket/my-image-1.tif", "gs://my-bucket/my-image-2.tif"]]
    print(create_tilesets_list(uris_list, dt_list, crs_list).serialize())

    # Multiple tilesets (bands)
    id_list = ["band1", "band2"]
    dt_list = ["FLOAT32", "UINT32"]
    crs_list = ["EPSG:4326", "EPSG:4326"]
    uris_list = [["gs://my-bucket/my-image-1.tif"], ["gs://my-bucket/my-image-2.tif"]]
    print(create_tilesets_list(uris_list, dt_list, crs_list, id_list).serialize())
    """
    if id_list:
        out = [{"id": manifest.ID(tmp1),
                "sources": create_source_list(tmp2),
                "data_type": manifest.DataType(tmp3),
                "crs": manifest.CRS(tmp4)}
               for tmp1, tmp2, tmp3, tmp4
               in zip(id_list, uris_list, dt_list, crs_list)]
    else:
        out = [{"sources": create_source_list(tmp2),
                "data_type": manifest.DataType(tmp3),
                "crs": manifest.CRS(tmp4)}
               for tmp2, tmp3, tmp4
               in zip(uris_list, dt_list, crs_list)]
    return(manifest.Tilesets(out))


# Example:
# Single tileset (mosaic)
dt_list = ["FLOAT32"]
crs_list = ["EPSG:4326"]
uris_list = [["gs://my-bucket/my-image-1.tif",
              "gs://my-bucket/my-image-2.tif"]]
print(create_tilesets_list(uris_list, dt_list, crs_list).serialize())

# Multiple tilesets (bands)
id_list = ["band1", "band2"]
dt_list = ["FLOAT32", "UINT32"]
crs_list = ["EPSG:4326", "EPSG:4326"]
uris_list = [["gs://my-bucket/my-image-1.tif"],
             ["gs://my-bucket/my-image-2.tif"]]
print(create_tilesets_list(uris_list, dt_list, crs_list, id_list).serialize())

# Build properties


def create_properties_dict(properties_dict=None):
    """
    Create a properties dictionary object

    Populates and validates a properties object.  

    @arg properties_dict Flat dictionary of properties, if none given an empty dict with common keys supplied 

    @returns A properties object populated by properties_dict if none given an empty dict with common keys.
    @example
    properties_dict = {"name": "my-dataset", "alternateName": "MDS", "description": "A short description"}
    print(create_properties_dict(properties_dict).serialize())
    """
    if properties_dict:
        out = manifest.Properties(**properties_dict)
    else:
        out = manifest.Properties()
    return out


# Example
properties_dict = {"name": "my-dataset",
                   "alternateName": "MDS", "description": "A short description"}
print(create_properties_dict(properties_dict).serialize())
print(create_properties_dict().serialize())

# Build time


def create_timestamp(timestamp):
    """
    Create a time object

    Convert a timestamp in iso8601 format to seconds from epoch  

    @arg timestamp Timestamp (UTC) string in iso8601 format, see package iso8601 for details

    @returns A Timestamp object
    @example
    print(create_timestamp("2009-06-24T08:00:00").serialize())
    """
    t = int(iso8601.parse_date(timestamp).timestamp())
    #datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S')
    return(manifest.Timestamp(seconds=t))


# Example:
ts = "20180813T141403"
print(create_timestamp(ts).serialize())
ts = "2018-08-13T14:14:03"
print(create_timestamp(ts).serialize())
ts = "2018-08-13 14:14:03"
print(create_timestamp(ts).serialize())
# see https://www.epochconverter.com/
# correct answer is 1534169643
# note in gee values returned as usec!

"""### create_image_manifest"""

# Build manifest object


def create_image_manifest(name,
                          uris_list, dt_list, crs_list,
                          id_list, md_list, pp_list, tsbi_list,
                          properties_dict,
                          start_time, end_time,
                          footprint=None, pyramiding_policy=None, uri_prefix=None,
                          missing_data=None
                          ):
    """
    Create a ImageManifest object  

    @arg name Path string for earthengine Image asset
    @arg id_list List of tileset id names, these link to band names? e.g., ["band1", "band2"]
    @arg uris_list List of lists of GCS uris, for each tileset (band) e.g., [[["gs://my-bucket/my-image-1.tif"], ["gs://my-bucket/my-image-2.tif"]]]
    @arg md_list List of missing_data values lists, e.g., [[-999]]
    @arg pp_list List of pyramiding policy strings; "MEAN", "MODE", or "SAMPLE", e.g., ["MEAN"]
    @arg tsbi_list List of tileset band index integers, e.g., [0]
    @arg properties_dict A dictionary of properties

    @returns A source_list object
    @example
    # Single uri, single band
    name = "projects/earthengine-legacy/assets/users/username/some_folder/some_asset_id" 
    id_list = ["band1"]
    uris_list = [[["gs://my-bucket/my-image-1.tif"]]]
    md_list = [[-999]]
    pp_list = ["MEAN"]
    tsbi_list = [0] 
    print(create_manifest(name, uris_list, id_list, md_list, pp_list, tsbi_list).serialize())

    # Single uri, multiple bands
    name = "projects/earthengine-legacy/assets/users/username/some_folder/some_asset_id" 
    id_list = ["band1", "band2"]
    uris_list = [[["gs://my-bucket/my-image-1.tif"]]]
    md_list = [[-999], [0]]
    pp_list = ["MEAN", "MODE"]
    tsbi_list = [0, 1] 
    print(create_manifest(name, uris_list, id_list, md_list, pp_list, tsbi_list).serialize())

    # One uri, per band
    name = "projects/earthengine-legacy/assets/users/username/some_folder/some_asset_id" 
    id_list = ["band1", "band2"]
    uris_list = [[["gs://my-bucket/my-image-band-1.tif"]], [["gs://my-bucket/my-image-band-2.tif"]]] # each image is a band
    md_list = [[-999], [0]] # apply different NA values
    pp_list = ["MEAN", "MODE"] # apply different pyramiding policy
    tsbi_list = [0, 0] # first band of each image 
    print(create_manifest(name, uris_list, id_list, md_list, pp_list, tsbi_list).serialize())
    """

    # Check case (mosaic or band per tileset?)
    uril = len(uris_list)
    print("Number of tilesets", uril)
    bl = len(id_list)
    print("Number of bands", bl)

    # Create timestamps
    st = create_timestamp(start_time)
    et = create_timestamp(end_time)

    # Create bands
    bands = create_band_list(id_list, md_list, pp_list, tsbi_list)

    # Create tilesets
    if uril == 1:
        tilesets = create_tilesets_list(
            uris_list, dt_list, crs_list, id_list=None)
    else:
        tilesets = create_tilesets_list(
            uris_list, dt_list, crs_list, id_list=id_list)

    # Create properties
    props = create_properties_dict(properties_dict)

    # Name
    name = manifest.Name(name)

    # Create manifest
    out = manifest.ImageManifest(**{
        "name": name,
        "bands": bands,
        "tilesets": tilesets,
        "properties": props,
        "start_time": st,
        "end_time": et,
        "footprint": footprint,
        "pyramiding_policy": pyramiding_policy,
        "uri_prefix": uri_prefix,
        "missing_data": missing_data
    })

    return(out)


# Example:
# General metadata
name = "projects/earthengine-legacy/assets/projects/some_projects/some_asset/data-folder/my-asset"
prop_dict = {"name": "my-dataset", "alternateName": "MDS",
             "description": "A short description"}
start_time = "2009-06-24T08:00:00"
end_time = "2009-06-25T08:00:00"

# Single uri, single band
id_list = ["band1"]
uris_list = [["gs://my-bucket/my-image-1.tif"]]
md_list = [[-999]]
pp_list = ["MEAN"]
tsbi_list = [0]
dt_list = ["FLOAT32"]
crs_list = ["EPSG:4326"]
m = create_image_manifest(name, uris_list, dt_list, crs_list, id_list, md_list,
                          pp_list, tsbi_list, properties_dict, start_time, end_time,
                          footprint=None, pyramiding_policy=None, uri_prefix=None)
print(m.serialize())

# Single uri, multiple bands
id_list = ["band1", "band2"]
uris_list = [["gs://my-bucket/my-image-1.tif"]]
md_list = [[-999], [0]]
pp_list = ["MEAN", "MODE"]
tsbi_list = [0, 1]
dt_list = ["FLOAT32", "UINT32"]
crs_list = ["EPSG:4326", "EPSG:4326"]
m = create_image_manifest(name, uris_list, dt_list, crs_list, id_list, md_list,
                          pp_list, tsbi_list, properties_dict, start_time, end_time,
                          footprint=None, pyramiding_policy=None, uri_prefix=None)
print(m.serialize())

# One uri, per band
id_list = ["band1", "band2"]
uris_list = [["gs://my-bucket/my-image-band-1.tif"],
             ["gs://my-bucket/my-image-band-2.tif"]]  # each image is a band
md_list = [[-999], [0]]  # apply different NA values
pp_list = ["MEAN", "MODE"]  # apply different pyramiding policy
tsbi_list = [0, 0]  # first band of each image
dt_list = ["FLOAT32", "UINT32"]
crs_list = ["EPSG:4326", "EPSG:4326"]
m = create_image_manifest(name, uris_list, dt_list, crs_list, id_list, md_list,
                          pp_list, tsbi_list, properties_dict, start_time, end_time,
                          footprint=None, pyramiding_policy=None, uri_prefix=None)
print(m.serialize())


