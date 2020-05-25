import python_jsonschema_objects as pjs
from datetime import datetime
import iso8601
import json



class ImageManifest():
    """
    An image manifest object.

    This function builds an object that can be serialized as an earthengine manifest JSON.

    FIXME add uri_prefix as standard

    Parameters
    ----------
    name: string
        Path of the earthengine asset.
    uris_list: list of list of str
        List of list of asset file paths. Only google cloud storage is supported. 
    dt_list: list of str
        A list of tileset data types; "DATA_TYPE_UNSPECIFIED","INT8","UINT8","INT16","UINT16","INT32","UINT32","FLOAT32","FLOAT64".
    crs_list: str
        A list of tileset CRS codes; "EPSG:<code>".
    id_list: str
        List of band (and potentially tileset) names.
    md_list: list of list num
        List of list of band list missing data values.
    pp_list: list str
        List of band pyramiding policy codes; "MEAN", "MODE", "SAMPLE".
    tsbi_list: list int
        List of tileset band indexes to use for creating asset.
    props: dict
        A dictionary of properties to add to the asset. A selection from schema.org/DataSet
    start_time: str
        The image aquisition start time as ISO8601 string.
    end_time: str
        The image aquisition end time as ISO8601 string.                 
    footprint: dict
        Footprint.
    uri_prefix: str
        Prefix to add to uris path.    

    Returns
    -------
    A ImageManifest object

    Examples
    --------
    # General metadata
    name = "projects/earthengine-legacy/assets/projects/some_projects/some_asset/data-folder/my-asset"
    props_dict = {"name": "my-dataset", "alternateName": "MDS",
             "description": "A short description"}
    start_time = "2009-06-24T08:00:00"
    end_time = "2009-06-25T08:00:00"
    uri_prefix = ""gs://my-bucket"

    # Single uri, single band
    id_list = ["band1"]
    uris_list = [[my-image-1.tif"]]
    md_list = [[-999]]
    pp_list = ["MEAN"]
    tsbi_list = [0]
    dt_list = ["FLOAT32"]
    crs_list = ["EPSG:4326"]
    m = create_image_manifest(name, uris_list, dt_list, crs_list, id_list, md_list,
                          pp_list, tsbi_list, props_dict, start_time, end_time,
                          footprint=None, uri_prefix=uri_prefix)
    print(m.serialize())

    # Single uri, multiple bands
    id_list = ["band1", "band2"]
    uris_list = [[my-image-1.tif"]]
    md_list = [[-999], [0]]
    pp_list = ["MEAN", "MODE"]
    tsbi_list = [0, 1]
    dt_list = ["FLOAT32", "UINT32"]
    crs_list = ["EPSG:4326", "EPSG:4326"]
    m = create_image_manifest(name, uris_list, dt_list, crs_list, id_list, md_list,
                          pp_list, tsbi_list, props_dict, start_time, end_time,
                          footprint=None, uri_prefix=uri_prefix)
    print(m.serialize())

    # One uri, per band
    id_list = ["band1", "band2"]
    uris_list = [["my-image-band-1.tif"],
             ["my-image-band-2.tif"]]  # each image is a band
    md_list = [[-999], [0]]  # apply different NA values
    pp_list = ["MEAN", "MODE"]  # apply different pyramiding policy
    tsbi_list = [0, 0]  # first band of each image
    dt_list = ["FLOAT32", "UINT32"]
    crs_list = ["EPSG:4326", "EPSG:4326"]
    m = create_image_manifest(name, uris_list, dt_list, crs_list, id_list, md_list,
                          pp_list, tsbi_list, props_dict, start_time, end_time,
                          footprint=None, uri_prefix=uri_prefix)
    print(m.serialize())
    """

    def __init__(self, name,
                 uris_list, dt_list, crs_list,
                 id_list, md_list, pp_list, tsbi_list,
                 props_dict,
                 start_time, end_time,
                 uri_prefix,
                 footprint=None, manifest_path="ee-manifest-schema.json"
                 ):
        self.manifest_path = manifest_path
        self.name = name
        self.manifest = self.create_manifest()
        self.bands = self.create_bands(id_list, md_list, pp_list, tsbi_list)
        self.start_time = self.create_timestamp(start_time)
        self.end_time = self.create_timestamp(end_time)
        if len(uris_list) == 1:
            self.tilesets = self.create_tilesets(
                uris_list, dt_list, crs_list, id_list=None)
        else:
            self.tilesets = self.create_tilesets(
                uris_list, dt_list, crs_list, id_list=id_list)

        self.properties = self.create_properties(props_dict)
        self.uri_prefix = uri_prefix
        #if footprint:
          #self.footprint = self.create_footprint(footprint)

    def as_dict(self):
        return self.manifest.ImageManifest(**{
            'name': self.name,
            'bands': self.bands,
            'tilesets': self.tilesets,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'properties': self.properties,
            'uri_prefix': self.uri_prefix
            #'footprint': self.footprint
            }).as_dict()
    
    def serialize(self):
        return self.manifest.ImageManifest(**{
            'name': self.name,
            'bands': self.bands,
            'tilesets': self.tilesets,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'properties': self.properties,
            'uri_prefix': self.uri_prefix
            #'footprint': self.footprint
            }).serialize()       

    def create_manifest(self):
        with open(self.manifest_path, "r") as f:
            image_manifest_schema = json.load(f)
        return pjs.ObjectBuilder(image_manifest_schema).build_classes(
            named_only=False, standardize_names=False)

    def create_footprint(self, band_id, points):
        """
        Create a Footprint object

        https://developers.google.com/earth-engine/image_manifest#footprint

        Parameters
        ----------
        band_id : str
            The band id that contains the CRS to use for the points.
        points : dict
            A list of dictionaries with the x,y values that define describe a 
            ring which forms the exterior of a simple polygon that must contain the 
            centers of all valid pixels of the image.

        Returns
        -------
        object
            A Footprint object

        Examples
        --------
        band_id = "test"
        points = [{"x": 0.5,"y": 0.5},{"x": 0.5,"y": 1.5},{"x": 1.5,"y": 1.5},{"x": 1.5,"y": 0.5},{"x": 0.5,"y": 0.5}]
        print(create_footprint(band_id, points).serialize())
        """
        return(self.manifest.Footprint(band_id=band_id, points=points))

    def create_affine_transform(self, args):
        """
        Create and AffineTransform object

        Parameters
        ----------
        args : dict
            A dictionary with affine transformation properties; "scale_x", "shear_x", "translate_x", "shear_y", "scale_y", "translate_y".
        """
        return(self.manifest.AffineTransform(**args))

    def create_mask_bands(self, tileset_id_list, band_ids_list=None):
        """
        Create MaskBands object

        Can be used for 2 cases; 
            + To use a tileset as a mask for all bands, band_ids_list = None
            + To use a tileset as a mask for specific bands, band_ids_list = None
        see https://developers.google.com/earth-engine/image_self.manifest#mask_bands

        Parameters
        ----------
        tileset_id_list : list of str
            List of tileset ids that contain the mask (note only last band is used), e.g., ["mask1", "mask2"].
        band_ids_list : list of list of str, optional
            list of list of bands to apply the mask too, e.g., [["band1"]], ["band2", "band3"]], by default None

        Examples
        --------
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
        return(self.manifest.MaskBands(out))

    def create_bands(self, id_list, md_list, pp_list, tsbi_list):
        """
        Create Bands object

        Parameters
        ----------
        id_list : list of str
            List of band id strings
        md_list : list of list of num
            List of list with missing_data numbers
        pp_list : list of str
            List of pyramiding policy strings ("MEAN", "MODE", or "SAMPLE")
        tsbi_list : list of int
            List of tileset band index integers

        Returns
        -------
        A Bands object        

        Examples
        --------
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
            out = [self.manifest.Band(**{
                "id": self.manifest.ID(tmp1),
                "missing_data": self.manifest.MissingData(values=tmp2),
                "pyramiding_policy": self.manifest.PyramidingPolicy(tmp3),
                "tileset_band_index": self.manifest.TilesetBandIndex(tmp4)
            })
                for tmp1, tmp2, tmp3, tmp4 in zip(id_list, md_list, pp_list, tsbi_list)]

        # Many bands single property
        if many_ids & single_props:
            #print(f"Creating {idl} bands with {ppl} properties")
            out = [self.manifest.Band(**{
                "id": self.manifest.ID(tmp1),
                "missing_data": self.manifest.MissingData(values=md_list[0]),
                "pyramiding_policy": self.manifest.PyramidingPolicy(pp_list[0]),
                "tileset_band_index": self.manifest.TilesetBandIndex(tsbi_list[0])
            })
                for tmp1 in id_list]

        # Return bands_list object
        return(self.manifest.Bands(out))

    def create_sources(self, uris_list):
        """
        Create Sources object

        Parameters
        ----------
        uris_list : list of str
            List of list of file asset uris. At present only Google Cloud Storage is supported.

        Examples
        --------
        uris_list = ["gs://my-bucket/my-image-1.tif", "gs://my-bucket/my-image-2.tif"]
        print(create_source_list(uris_list).serialize())
        """
        return(self.manifest.Sources(
            [{"uris": self.manifest.Uris([tmp1])} for tmp1 in uris_list]
        ))

    def create_tilesets(self, uris_list, dt_list, crs_list, id_list=None):
        """
        Create Tilesets object



        Parameters
        ----------
        uris_list : list of list of str
            List of list of file asset uris, for each tileset (band)
        dt_list : list of str
            List of tileset data types; "DATA_TYPE_UNSPECIFIED","INT8","UINT8","INT16","UINT16","INT32","UINT32","FLOAT32","FLOAT64". 
        crs_list : list of str
            List of tileset CRS codes, as 'EPSG:<code>'.
        id_list : list of str, optional
            Optional list of tileset id names linked to band ids, by default None

        Returns
        -------
        A Tilesets object

        Can be used for 2 cases; 
            + To make a single tileset with sources (uris) where the tileset is treated as a mosaic, do not provide id_list.
            + To make a multiple tilesets with sources (uris) where the tileset is treated as a band, provide id_list.
        see https://developers.google.com/earth-engine/image_manifest#mask_bands

        Examples
        --------
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
        """
        if id_list:
            out = [{"id": self.manifest.ID(tmp1),
                    "sources": self.create_sources(tmp2),
                    "data_type": self.manifest.DataType(tmp3),
                    "crs": self.manifest.CRS(tmp4)}
                   for tmp1, tmp2, tmp3, tmp4
                   in zip(id_list, uris_list, dt_list, crs_list)]
        else:
            out = [{"sources": self.create_sources(tmp2),
                    "data_type": self.manifest.DataType(tmp3),
                    "crs": self.manifest.CRS(tmp4)}
                   for tmp2, tmp3, tmp4
                   in zip(uris_list, dt_list, crs_list)]
        return(self.manifest.Tilesets(out))

    def create_properties(self, props_dict=None):
        """
        Creates a Properties object

        Parameters
        ----------
        props_dict : dict, optional
            Flat dictionary of properties, by default None

        Returns
        -------
        A Properties object, if prop_dict is None, an empty object with common keys.

        Example
        -------
        properties_dict = {"name": "my-dataset",
                   "alternateName": "MDS", "description": "A short description"}
        print(create_properties_dict(properties_dict).serialize())
        print(create_properties_dict().serialize())
        """
        if props_dict:
            out = self.manifest.Properties(**props_dict)
        else:
            out = self.manifest.Properties()
        return out

    def create_timestamp(self, timestamp):
        """
        Create Timestamp object

        Parameters
        ----------
        timestamp : str
            Timestamp (UTC) string in iso8601 format, see package iso8601 for details.

        Returns
        -------
        A Timestamp object

        Examples
        --------
        ts = "20180813T141403"
        print(create_timestamp(ts).serialize())
        ts = "2018-08-13T14:14:03"
        print(create_timestamp(ts).serialize())
        ts = "2018-08-13 14:14:03"
        print(create_timestamp(ts).serialize())
        # see https://www.epochconverter.com/
        # correct answer is 1534169643
        # note in gee values returned as usec!    
        """
        t = int(iso8601.parse_date(timestamp).timestamp())
        return(self.manifest.Timestamp(seconds=t))



