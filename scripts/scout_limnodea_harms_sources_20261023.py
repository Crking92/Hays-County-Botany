#!/usr/bin/env python3
"""Discover individual source-labelled Limnodea original image codes from
Bob Harms Selected Central Texas Monocots BEFORE any public-use installation.
Writes source research only; never claims photos installed.
"""
import re,json
from urllib.parse import urljoin,urlsplit
from html.parser import HTMLParser
from pathlib import Path
import requests

BASE="https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/"
ENTRY=BASE+"Limnodea-H-frameset.html"
class Links(HTMLParser):
 def __init__(self):super().__init__();self.urls=[];self.title=""
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  for k in ("href","src"):
   if a.get(k):self.urls.append((tag,a[k]))
s=requests.Session();s.headers["User-Agent"]="HaysBotanyCentralTexasPhotoSourceAudit/1.0"
queue=[ENTRY]
seen=set();pages=[];image_refs=[];failed=[]
for _ in range(20):
 if not queue:break
 u=queue.pop(0)
 if u in seen:continue
 seen.add(u)
 try:
  r=s.get(u,timeout=30);r.raise_for_status()
  txt=r.text
  z=Links();z.feed(txt)
  pages.append({"url":u,"length":len(txt),"head":txt[:300].replace("\n"," "),"urls":z.urls[:55]})
  for tag,rel in z.urls:
   target=urljoin(u,rel)
   if "/Monocots/GrassHTML/data/" not in target:continue
   if re.search(r"\.(jpe?g|png)(?:[?#]|$)",target,re.I):
    image_refs.append({"from":u,"file":target})
   elif re.search(r"\.html?(?:[?#]|$)",target,re.I) and (
      ("Limnodea" in target) or ("LIAR" in target.upper()) or
      ("/data/" in target and len(seen)<14)):
    if target not in seen and target not in queue:queue.append(target)
 except Exception as e:failed.append({"url":u,"error":str(e)[:160]})
report={"entry":ENTRY,"pages":pages,"image_refs":image_refs,"failures":failed,
 "source_taxon":"Limnodea arkansana","rights":"copyright Bob Harms; Selected Monocots educational/scientific with individual credit only","archive_installed":False}
p=Path("reports/limnodea-harms-original-source-discovery-20261023.json")
p.parent.mkdir(parents=True,exist_ok=True)
p.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print("Discovered",len(pages),"pages",len(image_refs),"image references")
