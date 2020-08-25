import os
import requests

def get(search: str, page="1"):
    """
    Function that returns a request obtained from the Rakuten API

    Parameters
    ------------
    search: str
        Query
    page: str
        (OPTIONAL) Page number, will default to 1 if not given

    Return
    ------------
    req: list
    """
    #print(page)
    req = requests.get("https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706?format=json&"
                        "keyword=" + search + "&"
                        "page=" + str(page) + "&"
                        "genreId=" + os.getenv("GENRE_ID") + "&"
                        "hits=" + os.getenv("HITS") + "&"
                        "sort=-updateTimestamp&applicationId=" + os.getenv("RAK_APP_ID"))
    #print(req)
    return req