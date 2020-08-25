import json

def parse_item(items, index:int):
    """
    {Command Description Here}

    Parameters
    ------------
    items: dict
        {Parameter Description Here}
    index: int
        {Parameter Description Here}
    """
    content_json = json.loads(items.content)
    try:
        item_name = content_json["Items"][index]["Item"]['itemName']
    except IndexError:
        return {"item_name": ""}
    try:
        price = content_json["Items"][index]["Item"]['itemPrice']
    except IndexError:
        price = ""
    try:
        shop_name = content_json["Items"][index]["Item"]['shopName']
    except IndexError:
        shop_name = ""
    try:
        item_url = content_json["Items"][index]["Item"]['itemUrl']
    except IndexError:
        item_url = ""
    ret = {"item_name": item_name,
           "price": price,
           "shop_name": shop_name,
           "item_url": item_url,
           "item_json": content_json["Items"][index]}
    return ret