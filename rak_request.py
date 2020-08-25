import os
import requests
import datetime
import logging

x = datetime.datetime.now()
filename = "log_"+x.strftime("%b_%d_%y")+".log"
logging.basicConfig(filename=filename, level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logging.getLogger('cassandra').setLevel(logging.ERROR)
logging.getLogger('discord').setLevel(logging.ERROR)
logging = logging.getLogger(__name__)

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
    mens_fashion = 551177
    hats_acc = 110746
    shoes = 409409
    jewel = 407344
    womens_fashion = 303656
    #print(page)
    req = requests.get("https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706?format=json&"
                        "keyword=" + search + "&"
                        "page=" + str(page) + "&"
                        "genreId=" + os.getenv("GENRE_ID") + "&"
                        "hits=" + os.getenv("HITS") + "&"
                        "NGKeyword=ROVNER エレキギター Mozart セルマー HONDA GAME UNDERWEAR SUPREME ROMANCE" +"&"
                        "sort=-updateTimestamp&applicationId=" + os.getenv("RAK_APP_ID"))
    logging.info(req.status_code)
    #print(req)
    return req