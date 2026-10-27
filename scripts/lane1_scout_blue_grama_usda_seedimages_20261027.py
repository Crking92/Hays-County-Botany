#!/usr/bin/env python3
"""Investigate actual original-size USDA/CSU SeedImages blue grama florets.

No publication if original image cannot be linked to B. gracilis source or if
original pixels are not sufficient. Output source filenames, rights, sizes.
"""
import io, urllib.request, urllib.parse, time, re, json
from bs4 import BeautifulSoup
from PIL import Image
BASE="https://idtools.org/tools/2134/"
PAGE=BASE+"index.cfm?entityID=62219&packageID=2289"
RIGHTS="https://idtools.org/seedimages/index.cfm?pageID=3760"
def load(url):
    for n in range(3):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 HaysCountyBotanyPhotoRightsAndBotanicalAnatomy/1.0"})
            with urllib.request.urlopen(req,timeout=50) as r:
                b=r.read()
                return b,r.headers.get("content-type","")
        except Exception as e:
            print("SOURCE_GET_RETRY",n,url,str(e)[:300],flush=True)
            time.sleep((n+1)*3)
    raise RuntimeError("Source failed "+url)
rights=BeautifulSoup(load(RIGHTS)[0],"html.parser").get_text(" ",strip=True)
print("RIGHTS_EXCERPT",rights[rights.find("Copyright notice"):rights.find("Copyright notice")+850],flush=True)
assert "public domain except where otherwise indicated" in rights.lower(),"Cannot verify SeedImages photo reuse policy"
page=load(PAGE)[0].decode("utf-8",errors="replace")
soup=BeautifulSoup(page,"html.parser")
print("PAGE_EXCERPT",soup.get_text(" ",strip=True)[-1200:],flush=True)
assert "Bouteloua gracilis" in soup.get_text(" ",strip=True),"Not actual target page"
for num in ("BAT002862_IMG0006.jpg","BAT002862_IMG0007.jpg"):
    print("=== FILE",num,flush=True)
    matches=[]
    for tag in soup.find_all(True):
        t=str(tag)
        if num in t and len(t)<3000:
            matches.append(t)
    print("MATCHES",json.dumps(matches[:10]),flush=True)
    candidates=[]
    for m in re.findall(r'["\\x27]([^"\\x27]*'+re.escape(num)+r'[^"\\x27]*)["\\x27]',page,re.I):
        if not (m.startswith("data:") or m.startswith("#")):
            candidates.append(urllib.parse.urljoin(PAGE,m.split("?")[0]))
    candidates=list(dict.fromkeys(candidates))
    print("DERIVED",json.dumps(candidates),flush=True)
    for u in candidates:
        try:
            raw,ct=load(u)
            try:
                im=Image.open(io.BytesIO(raw));im.load()
                print("PIXELS",json.dumps({"url":u,"size":im.size,"format":im.format,"bytes":len(raw),"content_type":ct}),flush=True)
            except Exception as e:print("NON_IMAGE",u,str(e)[:140],flush=True)
        except Exception as e:print("CANDIDATE_FAILURE",u,str(e)[:200],flush=True)
