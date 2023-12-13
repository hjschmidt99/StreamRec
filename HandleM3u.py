import sys
import os
import urllib.request
import urllib.parse
import re

# regex to split by comma, but not inside quotes
COMMA_MATCHER = re.compile(r",(?=(?:[^\"']*[\"'][^\"']*[\"'])*[^\"']*$)")

def toDict(s):
    d1 = {}
    l1 = COMMA_MATCHER.split(s)
    for e in l1:
        l2 = e.split("=")
        v = l2[1].strip('"')
        if v.isnumeric():
            v = int(v)
        d1[l2[0]] = v
    return d1

# make string a valid filename
def toFilename(s):
    s = s.replace("\r", "")
    s = s.replace("\n", " - ")
    s = s.replace("\t", " ")
    s = s.replace("?", " ")
    s = s.replace("*", " ")
    s = s.replace(":", "-")
    s = s.replace("\"", "-")
    s = s.replace("/", "-")
    #s = s.replace(".", "-")
    #s = s.replace(",", "-")
    #s = s.replace(";", "-")
    s = s.replace("  ", " ")
    return s.strip()

def download(url):
    with urllib.request.urlopen(url) as response:
        rsp = response.read()
    return rsp.decode("utf-8")

def absurl(url, baseurl):
    # make relative urls absolute
    url1 = url
    if not url1.startswith("http"):
        url1 = baseurl + url1
    return url1
   
def decodeM3u(url, chan = "Channel"):
    p = download(url)
    p1 = p.splitlines()
    baseUrl = url.rsplit("/", 1)[0] + "/"
    tagStram = "#EXT-X-STREAM-INF:"
    tagMedia = "#EXT-X-MEDIA:"
    items = { "CHANNEL": chan, "URL": url }

    for ix1, x1 in enumerate(p1):
        s1 =  {}

        if x1.startswith(tagStram):
            t1 = x1.partition(tagStram)[2]
            s1 = toDict(t1)
            s1["URL"] = absurl(p1[ix1 + 1], baseUrl)
            s1 = { "TYPE": "VIDEO" } | s1

        if x1.startswith(tagMedia):
            t1 = x1.partition(tagMedia)[2]
            s1 = toDict(t1)
            if "URI" in s1:
                s1["URL"] = absurl(s1["URI"], baseUrl)

        if "TYPE" in s1.keys():
            type = s1["TYPE"]
            if not type in items.keys():
                items[type] = []

            s1["INDEX"] = len(items[type])
            items[type].append(s1)

    return items

def processM3u(url, dir, chan = "Channel"):
    p = download(url)
    p1 = p.splitlines()

    savenext1 = False
    savenext2 = False
    for ix1, x1 in enumerate(p1):
        if savenext1 or savenext2:
            url2 = x1
            # make relative urls absolute
            if not url2.startswith("http"):
                url2 = url.rsplit("/", 1)[0] + "/" + url2
                p1[ix1] = url2

            if savenext1:
                processM3u(url2, dir, chan)

        savenext1 = x1.startswith("#EXT-X-STREAM-INF") 
        savenext2 = x1.startswith("#EXTINF")

    fn1 = url.split("?")[0]
    fn1 = toFilename(chan) + "-" + os.path.basename(fn1)
    fn1 = os.path.join(dir, fn1)
    with open(fn1, 'w') as f1:
        f1.write("\n". join(p1))

    return p

