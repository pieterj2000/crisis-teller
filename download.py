#import requests
from requests_ratelimiter import LimiterSession
from bs4 import BeautifulSoup
from os import listdir
from itertools import chain
import re
from pathlib import Path
import gzip
import time


requests = LimiterSession(per_second=0.5)
requests.proxies.update({
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050",
})


rauwfolder = Path("./data/rauw/")
rauwfolder.mkdir(parents=True, exist_ok=True)
analysefolder = Path("./data/types/")
analysefolder.mkdir(parents=True, exist_ok=True)

def getlaatste() -> int:

    laatstepagina = requests.get("https://nos.nl/nieuws/laatste")
    soep = BeautifulSoup(laatstepagina.text, "html.parser")

    r = soep.select("main div section ul li a")[0]
    r = r["href"]

    r = re.search(r'\d+', r).group()
    return int(r)


def getdownloaded() -> set[int]:
    try:
        files = listdir(rauwfolder)
        if not files:
            return set()

        filenummers = { int(f.removesuffix(".html.gzip")) for f in files }
        return filenummers

    except Exception as e:
        print(e)
        print("returning set()")
        return set()

def geterrors() -> set[int]:
    try:
        error_set = set()
        p = analysefolder / "errorpaginas"
        if p.exists():
            with open(p, "rt", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        error_set.add(int(line.strip()))
        return error_set
    except Exception as e:
        print(e)
        print("returning set()")
        return set()

def getopenliveblogs() -> list[int]:
    try:
        with open(analysefolder / "liveblog_open", "rt", encoding="utf-8") as f:
            getallen = [ int(line.strip()) for line in f if line.strip() ]
        return getallen
    except Exception as e:
        print(e)
        print("returning []")
        return []


def opdrachtgen():
    laatste = getlaatste()
    downloaded = getdownloaded()
    errors = geterrors()
    eerste = 0

    openliveblogs = getopenliveblogs()

    excluded = downloaded | errors

    todo = [x for x in range(eerste, laatste + 1) if x not in excluded]

    return chain(openliveblogs, todo)


def download(num, tryagain = 3):
    num = str(num)

    r = None
    for i in range(10):
        try:
            r = requests.get("https://nos.nl/artikel/" + num)
            break
        except Exception as e:
            print(e)
            print(f"poging {i} gefaalt, opnieuw in 2 minuten")
            time.sleep(60*2)
        if i == 9:
            print("10 keer gefaalt, we kappen er mee :)")
            exit()
            

    if r.status_code == 200:
        print(num, 200, "opslaan")
        if (r.text == ""):
            print("response leeg")
            print("opnieuw proberen in 1 minuut")
            time.sleep(60)
            download(num)

        with gzip.open(rauwfolder / (num + ".html.gzip"), "wt", encoding="utf-8") as f:
            f.write(r.text)
    elif r.status_code == 404:
        print(num, 404, "overslaan")
        with open(analysefolder / "errorpaginas", "at", encoding="utf-8") as f:
            f.write(str(num) + "\n")
    elif r.status_code == 410:
        print(num, 410, "niet langer beschikbaar")
        with open(analysefolder / "errorpaginas", "at", encoding="utf-8") as f:
            f.write(str(num) + "\n")
    elif r.status_code == 502:
        print(num, 502, "bad gateway")
        print("opnieuw proberen in 1 minuut")
        time.sleep(60)
        download(num)
    elif r.status_code == 500:
        print(num, 500, "Deze pagina werkt helaas niet")
        if tryagain > 0:
            print("opnieuw proberen in 1 minuut")
            time.sleep(60)
            download(num, tryagain - 1)
        else:
            print("ik geef het op")
    else:
        print(num, r.status_code, "niet bekende statuscode")
        exit()


#with gzip.open(rauwfolder / ("2605906" + ".html.gzip"), "rt", encoding="utf-8") as f:
#    print(f.read())


todownload = opdrachtgen()
for n in todownload:
    download(n)
