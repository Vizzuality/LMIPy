import json

def html_box(item):
    """Returns an HTML block with template strings filled-in based on item attributes."""
    is_layer = str(type(item)) == "<class 'LMIPy.layer.Layer'>"
    is_dataset = str(type(item)) == "<class 'LMIPy.dataset.Dataset'>"
    is_table = str(type(item)) == "<class 'LMIPy.table.Table'>"
    is_widget = str(type(item)) == "<class 'LMIPy.lmipy.Widget'>"
    is_geometry = str(type(item)) == "<class 'LMIPy.geometry.Geometry'>"
    is_image = str(type(item)) == "<class 'LMIPy.image.Image'>"
    if is_layer:
        kind_of_item = 'Layer'
        url_link = f'{item.server}/v1/layer/{item.id}?includes=vocabulary,metadata'
    elif is_dataset:
        kind_of_item = 'Dataset'
        url_link = f'{item.server}/v1/dataset/{item.id}?includes=vocabulary,metadata,layer,widget'
    elif is_table:
        kind_of_item = 'Table'
        url_link = f'{item.server}/v1/dataset/{item.id}?includes=vocabulary,metadata,layer,widget'
    elif is_image:
        if item.type in ['Classified Image', 'Composite Image']:
            instrument = item.type
        else:
            instrument = item.instrument
        html_string = ("<div class='item_container' style='height: auto; overflow: hidden; border: 1px solid #80ceb9;"
                    "border-radius: 2px; background: #f2fffb; line-height: 1.21429em; padding: 10px;''>"
                    "<div class='item_left' style='width: 100px; height: 100px; float: left; padding-right:10px''>"
                    f"<a href='{item.thumb_url}' target='_blank'>"
                    f"<img class='itemThumbnail' src='{item.thumb_url}'>"
                    "</a></div><div class='item_right' style='float: none; width: auto; overflow: hidden;''>"
                    f"<b>Image Source</b>: {instrument} </br>"
                    f"<b>Datetime</b>: {item.date_time} </br>"
                    f"<b>Cloud score </b>: {item.cloud_score} </br>"
                    " </div> </div>")
        return html_string
    elif is_widget:
        kind_of_item = 'Widget'
        url_link = f'{item.server}/v1/widget/{item.id}'
    elif is_geometry:
        kind_of_item = 'Geometry'
        url_link = f'{item.server}/v1/geostore/{item.id}'
        html_string = ("<div class='item_container' style='height: auto; overflow: hidden; border: 1px solid #80ceb9;"
            "border-radius: 2px; background: #f2fffb; line-height: 1.21429em; padding: 10px;''>"
            "<div class='item_left' style='width: 210px; float: left;''>"
            "<a href='https://resourcewatch.org/' target='_blank'>"
            "<img class='itemThumbnail' src='https://resourcewatch.org/static/images/logo-embed.png'>"
            "</a></div><div class='item_right' style='float: none; width: auto; overflow: hidden;''>"
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
    if item.attributes.get('connectorUrl') and item.attributes.get('provider') == "csv":
        table_statement = (f"CSV Table: <a href={item.attributes.get('connectorUrl')}"
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

    html = ("<div class='item_container' style='height: auto; overflow: hidden; border: 1px solid #80ceb9;"
            "border-radius: 2px; background: #f2fffb; line-height: 1.21429em; padding: 10px;''>"
            "<div class='item_left' style='width: 210px; float: left;''>"
            "<a href='https://resourcewatch.org/' target='_blank'>"
            "<img class='itemThumbnail' src='https://resourcewatch.org/static/images/logo-embed.png'>"
            "</a></div><div class='item_right' style='float: none; width: auto; overflow: hidden;''>"
            f"<a href={url_link} target='_blank'>"
            f"<b>{item.attributes.get('name')}</b>"
            "</a>"
            f"<br> {table_statement} 🗺{kind_of_item} in {', '.join(item.attributes.get('application')).upper()}."
            f"<br>Last Modified: {item.attributes.get('updatedAt')}"
            f"<br>Connector: {item.attributes.get('provider')}"
            f" | Published: {item.attributes.get('published')}"
            " </div> </div>")
    return html

def show_image_collection(item, i):
    html_string = ("<div class='item_container' style='height: auto; overflow: hidden; border: 1px solid #80ceb9;"
                "border-radius: 2px; background: #f2fffb; line-height: 1.21429em; padding: 10px;''>"
                "<div class='item_left' style='width: 100px; height: 100px; float: left; padding-right:10px''>"
                f"<a href='{item.get('thumb_url')}' target='_blank'>"
                f"<img class='itemThumbnail' src='{item.get('thumb_url')}'>"
                "</a></div><div class='item_right' style='float: none; width: auto; overflow: hidden;''>"
                f"<b>Image Source</b>: {item.get('instrument')} </br>"
                f"<b>Datetime</b>: {item.get('date_time')} </br>"
                f"<b>Cloud score </b>: {item.get('cloud_score')} </br>"
                " </div> </div>")
    return html_string

def show(item, i):
    """Returns an HTML block with template strings filled-in based on item attributes."""
    is_layer = item['type'] == 'Layer'
    is_dataset = item['type'] == 'Dataset'
    is_table = item['type'] == 'Table'
    is_widget = item['type'] == 'Widget'
    server = item['server']
    item_id = item['id']
    attributes = item['attributes']
    if is_layer:
        kind_of_item = 'Layer'
        url_link = f'{server}/v1/layer/{item_id}?includes=vocabulary,metadata'
    elif is_dataset:
        kind_of_item = 'Dataset'
        url_link = f'{server}/v1/dataset/{item_id}?includes=vocabulary,metadata,layer,widget'
    elif is_table:
        kind_of_item = 'Table'
        url_link = f'{server}/v1/dataset/{item_id}?includes=vocabulary,metadata,layer,widget'
    elif is_widget:
        kind_of_item = 'Table'
        url_link = f'{server}/v1/widget/{item_id}'
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

    html = ("<div class='item_container' style='height: auto; overflow: hidden; border: 1px solid #80ceb9;"
            "border-radius: 2px; background: #f2fffb; line-height: 1.21429em; padding: 10px;''>"
            "<div class='item_left' style='width: 210px; float: left;''>"
            "<a href='https://resourcewatch.org/' target='_blank'>"
            "<img class='itemThumbnail' src='https://resourcewatch.org/static/images/logo-embed.png'>"
            "</a></div><div class='item_right' style='float: none; width: auto; overflow: hidden;''>"
            f"<b>{i}. </b>"
            f"<a href={url_link} target='_blank'>"
            f"<b>{attributes.get('name')}</b>"
            "</a>"
            f"<br> {table_statement} 🗺{kind_of_item} in {', '.join(attributes.get('application')).upper()}."
            f"<br>Last Modified: {attributes.get('updatedAt')}"
            f"<br>Connector: {attributes.get('provider')}"
            f" | Published: {attributes.get('published')}"
            " </div> </div>")
    return html

def create_class(item):
    from .dataset import Dataset
    from .table import Table
    from .layer import Layer
    from .lmipy import Widget
    from .image import Image
    if item['type'] == 'Table':
        return Table(id_hash = item.get('id'), server = item.get('server'))
    elif item['type'] == 'Dataset':
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