#import requests
from bs4 import BeautifulSoup
from os import listdir
from itertools import chain
import re
from pathlib import Path
import gzip
import json


rauwfolder = Path("./data/rauw/")
analysefolder = Path("./data/types/")
onbekendfolder = Path("./data/types/onbekend/")
onbekendfolder.mkdir(parents=True, exist_ok=True)
for f in onbekendfolder.iterdir():
    f.unlink()



def getrauwpaginas() -> list[int]:
    try:
        files = listdir(rauwfolder)
        if not files:
            return []

        filenummers = [ int(f.removesuffix(".html.gzip")) for f in files ]
        
        return filenummers

    except:
        return []





def getvantype(type: str) -> list[int]:
    try:
        with open(analysefolder / type, "rt", encoding="utf-8") as f:
            getallen = [ int(line.strip()) for line in f if line.strip() ]
        return getallen
    except Exception as e:
        print(e)
        return []
    




alles = getrauwpaginas()

artikels = getvantype("artikels")
videos = getvantype("videos")
livestreams = getvantype("livestreams")
liveblogs = getvantype("liveblogs")
#print(alles)
#print(artikels)
#print(videos)
#print(liveblogs)


artikels_set = set(artikels)
videos_set = set(videos)
livestreams_set = set(livestreams)
liveblog_set = set(liveblogs)
allesets = [artikels_set, videos_set, liveblog_set, livestreams_set]
allestodo = [ x for x in alles if all(x not in s for s in allesets)]

#print(allestodo)


videofile = open(analysefolder / "videos", "at", encoding="utf-8")
livestreams = open(analysefolder / "livestreams", "at", encoding="utf-8")
artikelfile = open(analysefolder / "artikels", "at", encoding="utf-8")
liveblogfile = open(analysefolder / "liveblogs", "at", encoding="utf-8")
liveblogfile_open = open(analysefolder / "liveblog_open", "wt", encoding="utf-8") # NB overwrites bestand

def process(num: int):
    filenaam = str(num) + ".html"
    
    with gzip.open(rauwfolder / (filenaam + ".gzip"), "rt", encoding="utf-8") as f:
        filecontent = f.read()

    soup = BeautifulSoup(filecontent, "html.parser")
    type = soup.find("meta", property="og:type")["content"]
    
    if type == "video":
        print(num, type)
        videofile.write(str(num) + "\n")
    elif type == "livestream":
        print(num, type)
        livestreams.write(str(num) + "\n")
    elif type == "article":
        print(num, type)
        artikelfile.write(str(num) + "\n")
    elif type == "liveblog":
        spul = soup.find("script",id="__NEXT_DATA__")
        spul = json.loads(spul.string)
        status = spul["props"]["pageProps"]["data"]["status"]
        print(num, type, status)
        
        if status == "closed":
            liveblogfile.write(str(num) + "\n")
        elif status == "open":
            liveblogfile_open.write(str(num) + "\n")
        else:
            exit()

        #print(spul)
        #print(json.dumps(spul, indent=4))# sort_keys=True, indent=4))
        #print(json.dumps(status, indent=4))# sort_keys=True, indent=4))
        #artikelfile.write(str(num) + "\n")
    else:
        print(num, type)
        with open(onbekendfolder / filenaam, "wt", encoding="utf-8") as of:
            of.write(filecontent)


i = 0
for artnum in allestodo:
    process(artnum)
    i += 1
    if i > 10:
        exit()






