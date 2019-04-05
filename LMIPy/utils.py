

def html_box(item):
    """Returns an HTML block with template strings filled-in based on item attributes."""
    is_layer = str(type(item)) == "<class 'LMIPy.layer.Layer'>"
    is_dataset = str(type(item)) == "<class 'LMIPy.dataset.Dataset'>" or str(type(item)) == "<class 'LMIPy.table.Table'>"
    if is_layer:
        kind_of_item = 'Layer'
        url_link = f'{item.server}/v1/layer/{item.id}?includes=vocabulary,metadata'
    elif is_dataset:
        kind_of_item = 'Dataset'
        url_link = f'{item.server}/v1/dataset/{item.id}?includes=vocabulary,metadata,layer'
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

