#!/usr/bin/env python3
"""Locate reusable Lindheimer panicgrass real herbarium specimen imagery.
No download to a canonical species folder unless photo-level public rights,
source taxonomic variety, individual media and actual anatomy are confirmed.
"""
import html,json,re,pathlib,urllib.request,urllib.error,time
from html.parser import HTMLParser
from urllib.parse import urljoin,urlparse
URIS=[
 "https://www.si.edu/object/dichanthelium-acuminatum-var-lindheimeri-nash-gould-ca-clark%3Anmnhbotany_16018883",
 "https://collections.si.edu/search/detail/edanmdm:nmnhbotany_16018883",
 "https://www.si.edu/object/nmnhbotany_16018883",
 "https://www.si.edu/es/object/dichanthelium-acuminatum-var-lindheimeri-nash-gould-ca-clark%3Anmnhbotany_16018883"
]
REFERENCE="https://www.si.edu/object/dichanthelium-acuminatum-var-lindheimeri-nash-gould-ca-clark%3Anmnhbotany_16018883"
class SnippetLinks(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  if tag not in ("a","img","source","meta","link","script"):return
  for k,v in attrs:
   if k in ("href","src","content","srcset") and v and ("si.edu" in v or "iiif" in v or "manifest" in v or "ids." in v):
    self.links.append(v[:1000])
def read(url):
 error=None
 for i in range(3):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 Hays-Botany-Field-Identification (photo-license scout; github.com/Crking92/Hays-County-Botany)","Accept":"text/html,application/json;q=0.9,*/*;q=0.5"})
   with urllib.request.urlopen(req,timeout=35) as r:
    data=r.read(5500000)
    return r.geturl(),r.status,r.headers.get("Content-Type",""),data.decode("utf-8","replace")
  except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as e:
   error=e
   if isinstance(e,urllib.error.HTTPError) and e.code not in (429,500,502,503,504): break
   time.sleep(i+1)
 raise RuntimeError(str(error))
results=[]
for url in URIS:
 try:
  redirected,status,typ,payload=read(url)
  links=SnippetLinks();links.feed(payload)
  matches=re.findall(r"(?:https?:)?//(?:ids|collections|iiif|api)\.si\.edu[^<>\"'\s\\]{6,450}",payload)
  key_patterns=["public domain","cc0","free of copyright","high-resolution jpeg","Dichanthelium acuminatum var. lindheimeri","Mary","Agnes","Chase"]
  evidence={x:(x.casefold() in payload.casefold()) for x in key_patterns}
  entries=[urljoin(redirected,html.unescape(z).replace("\\u0026","&")) for z in links.links if "ids.si.edu" in z or "manifest" in z or "iiif" in z]
  candidates=list(dict.fromkeys(entries+matches))
  results.append({"url":url,"redirect":redirected,"status":status,"content_type":typ,
                  "evidence":evidence,"potential_image_or_manifest_urls":candidates[:45],
                  "raw_media_fragments":[payload[max(0,m.start()-180):m.end()+120].replace("\n"," ")[:450] for m in list(re.finditer("ids.si.edu|\\.jp[eg]|manifest",payload,re.I))[:22]],
                  "body_chars":len(payload)})
 except Exception as e:
  results.append({"url":url,"error":str(e)[:250]})
folder=pathlib.Path("reports");folder.mkdir(exist_ok=True)
target=folder/"lane4-lindheimeri-smithsonian-cc0-source-scout-20261027.json"
report={"exact_taxon_candidate":"Dichanthelium acuminatum var. lindheimeri; canonical may recognize as Dichanthelium lindheimeri; subspecies/county status still held.",
 "source_specimen_id":"nmnhbotany_16018883","credit":"Smithsonian NMNH, Mary Agnes Chase (collector), 1906, North Carolina",
 "photo_rights_claim":"SMITHSONIAN ITEM PAGE explicitly public domain/CC0; individual delivered image rights and media id not independently matched yet.",
 "goal":"Direct physical byte source for exact-vouchered photo of genuine specimen with attached flowering and potentially roots; no microscopic ligule or dissection inference.",
 "no_public_media_archived":True,"entries":results}
target.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps({"results":results},indent=2,ensure_ascii=False),flush=True)
