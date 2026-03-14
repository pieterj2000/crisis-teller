#import requests
from requests_ratelimiter import LimiterSession
from bs4 import BeautifulSoup
from os import listdir
from itertools import chain
import re
from pathlib import Path


requests = LimiterSession(per_second=1)


def getlaatste() -> int:

    laatstepagina = requests.get("https://nos.nl/nieuws/laatste")
    soep = BeautifulSoup(laatstepagina.text, "html.parser")

    r = soep.select("main div section ul li a")[0]
    r = r["href"]

    r = re.search(r'\d+', r).group()
    return int(r)


rauwfolder = Path("./data/rauw/")
rauwfolder.mkdir(parents=True, exist_ok=True)

def getstate() -> tuple[int, int] | None:
    try:
        files = listdir(rauwfolder)
        if not files:
            return None

        filenummers = [ int(f.removesuffix(".html")) for f in files ]
        mx = max(filenummers)
        mn = min(filenummers)

        return (mn, mx)

    except:
        return None


def opdrachtgen():
    s = getstate()
    laatste = getlaatste()
    eerste = 0
    if s is None:
        return reversed(range(eerste, laatste+1))
    else:
        (mn, mx) = s
        nieuwe = range(mx+1, laatste+1)
        oude = reversed(range(eerste, mn))
        return chain(nieuwe, oude)




def download(num):
    num = str(num)
    r = requests.get("https://nos.nl/artikel/" + num)

    if r.status_code == 200:
        print(num, 200, "opslaan")
        with open(rauwfolder / (num + ".html"), "w") as f:
            f.write(r.text)
    elif r.status_code == 404:
        print(num, 404, "overslaan")
    else:
        print(num, r.status_code, "niet bekende statuscode")
        exit()



todownload = opdrachtgen()
for n in todownload:
    download(n)
