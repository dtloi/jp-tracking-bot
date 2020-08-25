#https://item.rakuten.co.jp/loop-online/mc61390/
import json
import os
import rak_parse
import rak_request

def update(query:str, anchor:str, depth:int):
    """
    {Command Description Here}

    Parameters
    ------------
    query: str
        {Parameter Description Here}
    anchor: str
        {Parameter Description Here}
    """
    ret = []
    #hile True:
    for j in range(1,5):

        req = rak_request.get(query, str(j))
        content_json = json.loads(req.content)

        #print(content_json["hits"])
        if content_json["hits"] == "0": #check to see if we are past the final page
            break
        request_size = int(content_json["hits"])
        #print(request_size)
        for i in range(request_size):
            item = rak_parse.parse_item(req, i)
            #print(item)
            if item["item_url"] == anchor:
                return ret
            else:
                ret.append(item)
        #print(ret)
    return ret
