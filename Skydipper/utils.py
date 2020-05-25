import json
import math
import ee
from time import sleep
from google.cloud import storage

def html_box(item):
    """Returns an HTML block with template strings filled-in based on item attributes."""
    is_layer = str(type(item)) == "<class 'Skydipper.layer.Layer'>"
    is_dataset = str(type(item)) == "<class 'Skydipper.dataset.Dataset'>"
    is_widget = str(type(item)) == "<class 'Skydipper.Skydipper.Widget'>"
    is_geometry = str(type(item)) == "<class 'Skydipper.geometry.Geometry'>"
    is_image = str(type(item)) == "<class 'Skydipper.image.Image'>"
    site_link = "<a href='https://skydipper.com/' target='_blank'>"
    site_logo = "<img class='itemThumbnail' src='https://skydipper.com/images/logo.png'>"
    if is_layer:
        kind_of_item = 'Layer'
        url_link = f'{item.server}/v1/layer/{item.id}?includes=metadata'
    elif is_dataset:
        kind_of_item = 'Dataset'
        url_link = f'{item.server}/v1/dataset/{item.id}?includes=metadata,layer'
    elif is_image:
        if item.type in ['Classified Image', 'Composite Image']:
            instrument = item.type
        else:
            instrument = item.instrument
        html_string = ("<div class='item_container' style='height: auto; overflow: hidden; border: 1px solid #2BA4A0;"
                    "border-radius: 5px; background: #2BA4A0; line-height: 1.21429em; padding: 10px;''>"
                    "<div class='item_left' style='width: 100px; height: 100px; float: left;''>"
                    f"<a href='{item.thumb_url}' target='_blank'>"
                    f"<img class='itemThumbnail' src='{item.thumb_url}'>"
                    "</a></div><div class='item_right' style='float: none; width: auto; hidden;padding-left: 10px; overflow: hidden;''>"
                    f"<b>Image Source</b>: {instrument} </br>"
                    f"<b>Datetime</b>: {item.date_time} </br>"
                    f"<b>Cloud score </b>: {item.cloud_score} </br>"
                    " </div> </div>")
        return html_string
    elif is_geometry:
        kind_of_item = 'Geometry'
        url_link = f'{item.server}/v1/geostore/{item.id}'
        html_string = ("<div class='item_container' style='height: auto; overflow: hidden; border: 1px solid #2bA4A0;"
            "border-radius: 5px; background: #2bA4A0; line-height: 1.21429em; padding: 10px;''>"
            "<div class='item_left' style='width: 210px; float: left;''>"
            f"{site_link}"
            f"{site_logo}"
            "</a></div><div class='item_right' style='float: none; width: auto; hidden;padding-left: 10px; overflow: hidden;''>"
            f"<b>Geometry id</b>: <a href={url_link} target='_blank'>{item.id}</a></br>")
        for k,v in item.attributes.get('info').items():
            if v and k != 'simplifyThresh':
                html_string += f"<br><i>{k}: {v}</i>"
        html_string += (""
            " </div> </div>")
        return html_string
    else:
        kind_of_item = 'Unknown'
        url_link = None
    table_statement = f"Data source {item.attributes.get('provider')}"
    if item.attributes.get('connectorUrl') and item.attributes.get('provider') == "cartodb":
        table_statement = (f"Carto table: <a href={item.attributes.get('connectorUrl')}"
                           " target='_blank'>"
                           f"{item.attributes.get('tableName')}"
                           "</a>"
                          )
    if item.attributes.get('provider') == 'gee':
        table_statement = (f"GEE asset: <a href='https://code.earthengine.google.com/asset='"
                           f"{item.attributes.get('tableName')} target='_blank'>"
                           f"{item.attributes.get('tableName')}"
                           "</a>"
                          )
    html = ("<div class='item_container' style='height: auto; overflow: hidden; border: 1px solid #2BA4A0;"
            "border-radius: 2px; background: #2BA4A0; line-height: 1.21429em; padding: 10px;''>"
            "<div class='item_left' style='width: 210px; float: left;''>"
            f"{site_link}"
            f"{site_logo}"
            "</a></div><div class='item_right' style='float: none; width: auto; hidden;padding-left: 10px; overflow: hidden;''>"
            f"<a href={url_link} target='_blank'>"
            f"<b>{item.attributes.get('name')}</b>"
            "</a>"
            f"<br> {table_statement} | {kind_of_item} in {', '.join(item.attributes.get('application')).upper()}."
            f"<br>Last Modified: {item.attributes.get('updatedAt')}"
            f"<br><a href='{item.server}/v1/fields/{item.id}' target='_blank'>Fields</a>"
            f" Connector: {item.attributes.get('provider')}"
            f" | Published: {item.attributes.get('published')}"
            " </div> </div>")
    return html

def show_image_collection(item, i):
    html_string = ("<div class='item_container' style='height: auto; overflow: hidden; border: 1px solid #2BA4A0;"
                "border-radius: 2px; background: #2BA4A0; line-height: 1.21429em; padding: 10px;''>"
                "<div class='item_left' style='width: 100px; height: 100px; hidden;padding-left: 10px; float: left''>"
                f"<a href='{item.get('thumb_url')}' target='_blank'>"
                f"<img class='itemThumbnail' src='{item.get('thumb_url')}'>"
                "</a></div><div class='item_right' style='float: none; hidden;padding-left: 10px; width: auto; overflow: hidden;''>"
                f"<b>Image Source</b>: {item.get('instrument')} </br>"
                f"<b>Datetime</b>: {item.get('date_time')} </br>"
                f"<b>Cloud score </b>: {item.get('cloud_score')} </br>"
                " </div> </div>")
    return html_string

def show(item, i):
    """Returns an HTML block with template strings filled-in based on item attributes."""
    is_layer = item.get('type') == 'Layer'
    is_dataset = item.get('type') == 'Dataset'
    server = item.get('server', "https://api.skydipper.com")
    item_id = item.get('id', None)
    attributes = item.get('attributes', None)
    if is_layer:
        kind_of_item = 'Layer'
        url_link = f'{server}/v1/layer/{item_id}?includes=metadata'
    elif is_dataset:
        kind_of_item = 'Dataset'
        url_link = f'{server}/v1/dataset/{item_id}?includes=metadata,layer'
    else:
        kind_of_item = 'Unknown'
        url_link = None
    table_statement = f"Data source {attributes.get('provider')}"
    if attributes.get('connectorUrl') and attributes.get('provider') == "cartodb":
        table_statement = (f"Carto table: <a href={attributes.get('connectorUrl')}"
                           " target='_blank'>"
                           f"{attributes.get('tableName')}"
                           "</a>"
                          )
    if attributes.get('connectorUrl') and attributes.get('provider') == "csv":
        table_statement = (f"CSV Table: <a href={attributes.get('connectorUrl')}"
                           " target='_blank'>"
                           f"{attributes.get('tableName')}"
                           "</a>"
                          )
    if attributes.get('provider') == 'gee':
        table_statement = (f"GEE asset: <a href='https://code.earthengine.google.com/asset='"
                           f"{attributes.get('tableName')} target='_blank'>"
                           f"{attributes.get('tableName')}"
                           "</a>"
                          )
    site_link = "<a href='https://skydipper.com/' target='_blank'>"
    site_logo = "<img class='itemThumbnail' src='https://skydipper.com/images/logo.png'>"
    html = ("<div class='item_container' style='height: auto; overflow: hidden; border: 1px solid #2BA4A0;"
            "border-radius: 2px; background: #2BA4A0; line-height: 1.21429em; padding: 10px;''>"
            "<div class='item_left' style='width: 210px;  float: left;''>"
            f"{site_link}"
            f"{site_logo}"
            "</a></div><div class='item_right' style='float: none; width: auto; hidden;padding-left: 10px; overflow: hidden;''>"
            f"<b>{i}. </b>"
            f"<a href={url_link} target='_blank'>"
            f"<b>{attributes.get('name')}</b>"
            "</a>"
            f"<br> {table_statement} | {kind_of_item} in {', '.join(attributes.get('application')).upper()}."
            f"<br>Last Modified: {attributes.get('updatedAt')}"
            f"<br><a href='{server}/v1/fields/{item_id}' target='_blank'>Fields</a>"
            f" | Connector: {attributes.get('provider')}"
            f" | Published: {attributes.get('published')}"
            " </div> </div>")
    return html

def create_class(item):
    from .dataset import Dataset
    from .layer import Layer
    from .Skydipper import Widget
    from .image import Image
    if item['type'] == 'metadata':
        return Dataset(id_hash=item.get('attributes').get('dataset'), server = item.get('server'))
    if item['type'] == 'Dataset' :
        return Dataset(id_hash = item.get('id'), server = item.get('server'))
    elif item['type'] == 'Layer':
        return Layer(id_hash = item.get('id'), server = item.get('server'))
    elif item['type'] == 'Widget':
        return Widget(id_hash = item.get('id'), attributes=item.get('attributes'), server = item.get('server'))
    elif item['type'] == 'Image':
        return Image(**item)

def flatten_list(nested_list):
    if len(nested_list) > 0:
        return [item for sublist in nested_list for item in sublist]
    else:
        return []

def get_geojson_string(geom):
    coords = geom.get('coordinates', None)
    if coords and not any(isinstance(i, list) for i in coords[0]):
        geom['coordinates'] = [coords]
    feat_col = {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {}, "geometry": geom}]}
    return json.dumps(feat_col)

def parse_filters(filter_objects):
    filter_whitelist = ['connectorType', 'provider', 'status', 'published', 'protected', 'geoInfo']
    return_string = ''
    error_string = ''
    if filter_objects:
        for k, v in filter_objects.items():
            if k in filter_whitelist:
                return_string += f'{k}={v}&'
            else:
                error_string += f' {k},'
        if error_string:
            print(f'Unable to filter by{error_string[:-1]}.')
        return return_string
    return ''

def sldDump(sldObj):
    """
    Creates valid SldStyle string from an object.
    """
    sld_type = sldObj.get('type', None)
    extended = str(sldObj.get('extended', 'false')).lower()
    items = sldObj.get('items', None)
    sld_attr = {'color': None, 'label': None, 'quantity': None, 'opacity': None}

    if sld_type not in ['linear', 'ramp', 'gradient', 'intervals', 'values']:
        print('Unable to create SldStyle. Type must be in "linear", "ramp", "gradient", "intervals", "values".')
        return None
    if items:
        sld_str = f'<RasterSymbolizer> <ColorMap type="{sld_type}" extended="{extended}"> '
        for item in items:
            sld_str += f'<ColorMapEntry '
            for k in sld_attr.keys():
                if item.get(k, None): sld_str += f'{k}="{item[k]}" '
            sld_str += '/> + '
    return sld_str + "</ColorMap> </RasterSymbolizer>"

def sldParse(sld_str):
    """
    Builds a dictionary from an SldStyle string.
    """
    sld_str = sld_str.replace("'", '"').replace('\"', '"')
    keys = ['color', 'label', 'quantity', 'opacity']
    items = [el.strip() for el in sld_str.split('ColorMapEntry') if '<RasterSymbolizer>' not in el]
    sld_items = []
    for i in items:
        tmp = {}
        for k in keys:
            v = find_between(i, f'{k}="', '"')
            if v: tmp[k] = v
        sld_items.append(tmp)
    return {
        'type': find_between(sld_str, 'type="', '"'),
        'extended': find_between(sld_str, 'extended="', '"'),
        'items': sld_items
    }

def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""

def nested_set(dic, keys, value):
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = value

def server_uses_widgets(server):
    """
    Does the server currently set use Widget objects? Response gives True if it does, false if not.
    """
    uses_widgets = ['https://api.resourcewatch.org','https://staging-api.globalforestwatch.org']
    if any(server in s for s in uses_widgets):
        return True
    else:
        return False

def tile_url(image, viz_params=None):
    """Create a target url for tiles from an EE image asset.
    e.g.
    im = ee.Image("LE7_TOA_1YEAR/" + year).select("B3","B2","B1")
    viz = {'opacity': 1, 'gain':3.5, 'bias':4, 'gamma':1.5}
    url = tile_url(image=im),viz_params=viz)
    """
    if viz_params:
        d = image.getMapId(viz_params)
    else:
        d = image.getMapId()
    base_url = 'https://earthengine.googleapis.com'
    url = (f"https://earthengine.googleapis.com/v1alpha/{d['mapid']}/tiles/{{z}}/{{x}}/{{y}}")
    return url


class EE_TILE_CALCS(object):
    """
    Copyright (c) 2018 Gennadii Donchyts. All rights reserved.
    This work is licensed under the terms of the MIT license.
    For a copy, see <https://opensource.org/licenses/MIT>.
    Refactored to Python, Vizzuality, 2020.
    This code will help you calculate tile bounds, intersected with
    a given geom, at a specified z-level.
    """
    def __init__(self, tileSize=256):
        ee.Initialize()
        self.tileSize = tileSize
        self.equatorial_circumference = 40075016.686
        self.origin = 2 * math.pi * 6378137 / 2.0

    def zoomToScale(self, zoom):
        tileWidth = self.equatorial_circumference / math.pow(2, zoom)
        pixelWidth = tileWidth / self.tileSize
        return pixelWidth

    def scaleToZoom(self, scale):
        tileWidth = scale * self.tileSize
        zoom = math.log(self.equatorial_circumference / tileWidth) / math.log(2)
        return math.ceil(zoom)

    def pixelsToMeters(self, px, py, zoom):
        resolution = self.zoomToScale(zoom)
        x = px * resolution - self.origin
        y = py * resolution - self.origin
        return [x, y]

    def metersToPixels(self, x, y, zoom):
        resolution = zoomToScale(zoom)
        px = (x + self.origin) / resolution
        py = (y + self.origin) / resolution
        return px, py

    def degreesToTiles(self, lon, lat, zoom):
        tx = math.floor((lon + 180) / 360 * math.pow(2, zoom))
        ty = math.floor((1 - math.log(math.tan(self.toRadians(lat)) + 1 / math.cos(self.toRadians(lat))) / math.pi) / 2 * math.pow(2, zoom))
        return [tx, ty]

    @staticmethod
    def tilesToDegrees(tx, ty, zoom):
        lon = tx / math.pow(2, zoom) * 360 - 180
        n = math.pi - 2 * math.pi * ty / math.pow(2, zoom)
        lat = toDegrees(math.atan(0.5 * (math.exp(n) - math.exp(-n))))
        return [lon, lat]

    def getTilesForGeometry(self, geometry, zoom):
        bounds = ee.List(geometry.bounds().coordinates().get(0))
        ll = bounds.get(0).getInfo() # <-- Look at making this happen server-side
        ur = bounds.get(2).getInfo() # <-- Look at making this happen server-side
        tmin = self.degreesToTiles(ll[0], ll[1], zoom)
        tmax = self.degreesToTiles(ur[0], ur[1], zoom)
        tiles = []
        for tx in range(tmin[0], tmax[0] + 1):
            for ty in range(tmax[1], tmin[1] + 1):
                bounds = self.getTileBounds(tx, ty, zoom)
                rect = ee.Geometry.Rectangle(bounds, 'EPSG:3857', False)
                tiles.append(ee.Feature(rect).set({'tx': tx, 'ty': ty, 'zoom': zoom }))
        return ee.FeatureCollection(tiles).filterBounds(geometry)

    def getTilesList(self, geometry, zoom):
        """Returns a list of individual features, where each feature element is a tile footprint."""
        bounds = ee.List(geometry.bounds().coordinates().get(0))
        ll = bounds.get(0).getInfo() # <-- Look at making this happen server-side
        ur = bounds.get(2).getInfo() # <-- Look at making this happen server-side
        tmin = self.degreesToTiles(ll[0], ll[1], zoom)
        tmax = self.degreesToTiles(ur[0], ur[1], zoom)
        tiles = []
        for tx in range(tmin[0], tmax[0] + 1):
            for ty in range(tmax[1], tmin[1] + 1):
                bounds = self.getTileBounds(tx, ty, zoom)
                rect = ee.Geometry.Rectangle(bounds, 'EPSG:3857', False)
                tiles.append(ee.Feature(rect).set({'tx': tx, 'ty': ty, 'zoom': zoom }))
        return tiles

    def getTileBounds(self, tx, ty, zoom, tileSize=256):
        """Returns a FeatureCollection object, where each feature is a tile footprint"""
        ty = math.pow(2, zoom) - ty - 1 # TMS -> XYZ, flip y index
        tmp_min = self.pixelsToMeters(tx * tileSize, ty * tileSize, zoom)
        tmp_max = self.pixelsToMeters((tx + 1) * tileSize, (ty + 1) * tileSize, zoom)
        return [tmp_min, tmp_max]

    @staticmethod
    def toRadians(degrees):
        return degrees * math.pi / 180

    @staticmethod
    def toDegrees(radians):
        return radians * 180 / math.pi


class MovieMaker(object):
    """
    Create movie tiles for a list of bounds, to go into a GCS bucket

    Parameters
    ----------
    area: ee.Geometry.Polygon()
        A polygon that covers the area which you want to generate tiles within.

    zlist: list
        A list of integer values of z-levels to process, e.g. z=[3] or z=[3,4,5]

    privatekey_path: string
        A string specifying the direction of a json keyfile on your local filesystem
        e.g. "/Users/me/.privateKeys/key_with_bucket_permissions.json"

    bucket_name: string
        A string specifying a GCS bucket (to which your private key should have access)
        e.g. 'skydipper_materials'

    folder_path: string
        A string specifying a folder name to create within the target bucket.
        e.g. 'movie-tiles/DTEST'

    report_status: bool
        Set to true if you want the program to report on the files it is generating.
        Beware it can get long for high z-levels.
    """
    def __init__(self, privatekey_path, bucket_name, folder_path,
                    area=None, zlist=None, ic=None, report_status=False):
        self.storage_client = storage.Client.from_service_account_json(privatekey_path)
        self.privatekey_path = privatekey_path
        self.bucket = self.storage_client.get_bucket(bucket_name)
        self.bucket_name = bucket_name
        self.folder_path = folder_path
        self.tiler = EE_TILE_CALCS()
        self.area = area
        self.zlist = zlist
        self.ic = ic
        self.report_status = report_status
        ee.Initialize()

    def run(self):
        """Main worker method"""
        assert type(self.zlist) == list, "the zlist must be a list to run, e.g. zlist=[2]"
        assert type(self.area) == ee.geometry.Geometry, "An area of type ee.geometry.Geometry must be provided to run"
        for zlevel in self.zlist:
            print(f"🧨 Calculating Z-level {zlevel}")
            tileset = self.tiler.getTilesList(self.area, zlevel)
            d = self.initial_dic_creation(tileset=tileset) # Starting dic of whatever has been burned to the bucket
            to_do = self.get_items_by_state(d, 'WAITING')
            for unprocessed in to_do:
                z=unprocessed[0].split('/')[-3]
                x=unprocessed[0].split('/')[-2]
                y=unprocessed[0].split('/')[-1].split('.mp4')[0]
                if self.report_status: print(f'{z}/{x}/{y}')
                try:
                    self.movie_maker(tile=unprocessed[1].get('tile'), z=z, x=x, y=y)
                except (ee.EEException) as err:
                    sleep(60 * 5)  # Simple - Wait 5 mins and try assigning tasks again (this assumes the only issue )
                    self.movie_maker(tile=unprocessed[1].get('tile'), z=z, x=x, y=y)
        print("Program ended normally. Note that after the files have been generated you should run MovieMaker().reNamer()")
        self.reNamer()
        return

    def movie_maker(self, tile, z, x, y):
        """Generates a single movie tile"""
        g = tile.geometry()
        filtered = self.ic.filterBounds(g)
        #print(f"🗺 Exporting movie-tile to {self.bucket_name}/{self.folder_path}/{z}/{x}/{y}.mp4")
        exp_task = ee.batch.Export.video.toCloudStorage(
                        collection = filtered,
                        description = f'{z}_{x}_{y}',
                        bucket= self.bucket_name,
                        fileNamePrefix = f"{self.folder_path}/{z}/{x}/{y}",
                        dimensions = [256,256],
                        framesPerSecond = 2,
                        region = g)
        exp_task.start()

    def reNamer(self):
        """Renames source files to a clean target that removes jank added by EE."""
        blob_gen = self.bucket.list_blobs(prefix=self.folder_path)
        blobs = [blob for blob in blob_gen]
        print(f'Scanning target {self.bucket_name}/{self.folder_path} for files that require renaming...')
        for blob in blobs:
            tmp_name = blob.name
            if tmp_name[-4:] == '.mp4' and ("ee-export-video" in tmp_name):
                target_name = f"{tmp_name.split('ee-export-video')[0]}.mp4"
                if self.report_status: print(f'renaming:{tmp_name}-->{target_name}')
                _ = self.bucket.rename_blob(blob, target_name)

    def getDoneFileList(self):
        """Returns list of file names in a bucket/path that have already been created"""
        blob_gen = self.bucket.list_blobs(prefix=self.folder_path)
        blobs = [blob for blob in blob_gen]
        completed_files = []
        for blob in blobs:
            completed_files.append(blob.name)
        return completed_files

    def getFullTargetList(self, z):
        """
            Return a list of all files we intend to create for a specified z (int) target to cover a given ee.Geometry input
            area, with a folder path (string) direction appended.
        """
        target_list = []
        tmp_fc = self.tiler.getTilesForGeometry(self.area, z)
        tmp_info = tmp_fc.getInfo()   # <---this is the point where I have the properties, I should make sure to propagate them rather then call getinfo again
        target_list = [f"{self.folder_path}/{item.get('properties').get('zoom')}/{item.get('properties').get('tx')}/{item.get('properties').get('ty')}.mp4"
                       for item in tmp_info.get('features')]
        return sorted(target_list)

    def get_current_status(self):
        """Consult the current EE Task list to see what's what"""
        batch_jobs = ee.batch.Task.list()
        processing_list = []
        processing_status = []
        badness_list = []
        for job in batch_jobs:
            state = job.state
            try:
                tmp = job.config['description'].split("_")
                tmp_fname = f"{self.folder_path}/{tmp[0]}/{tmp[1]}/{tmp[2]}.mp4"
                processing_list.append(tmp_fname)
                processing_status.append(state)
            except:
                badness_list.append(job)
        return {'processing':processing_list,
                'status': processing_status,
                'badness': badness_list}

    def get_objective_list(self, tileset):
        """Returns a list of target files 1:1 for the target tiles"""
        tmp_list = []
        for tile in tileset:
            tmp_str = tile.__str__()
            zoom = json.loads(tmp_str[11:-1]).get('arguments').get('value')
            ty = json.loads(tmp_str[11:-1]).get('arguments').get('object').get('arguments').get('value')
            tx = json.loads(tmp_str[11:-1]).get('arguments').get('object').get('arguments').get('object').get('arguments').get('value')
            tmp_list.append(f"{self.folder_path}/{zoom}/{tx}/{ty}.mp4")
        return tmp_list

    @staticmethod
    def generate_master_dic(objectives, tileset):
        d = {}
        for obj, tile in zip(objectives, tileset):
            d[obj] = {'tile': tile, 'status': "WAITING"}
        return d

    @staticmethod
    def get_items_by_state(d, state="WAITING"):
        result = []
        for i in d.items():
            if (i[1].get('status') == state):
                result.append(i)
        return result


    def initial_dic_creation(self, tileset):
        objectives = self.get_objective_list(tileset) # <--- calculate target files to keep track
        d = self.generate_master_dic(objectives=objectives, tileset=tileset)
        self.reNamer()
        done = self.getDoneFileList() # Consult the bucket and see what files have been completed
        for item in done:
            if d.get(item, None):
                d[item]['status']='COMPLETED'
        return d