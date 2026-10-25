#!/usr/bin/env python3
"""Inspect exact-species vouchered CC0 Smithsonian GBIF records and Pine muhly Commons photo.
NO unknown-rights files are imported here.
"""
import json,pathlib,urllib.parse,urllib.request,re,html
report={"taxon":"Muhlenbergia dubia","smithsonian":[],"commons":[],"holds":[]}
def fetch(url):
 req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyVisualLearner/1.0 (photo source-rights educational audit; github.com/Crking92/Hays-County-Botany)"})
 with urllib.request.urlopen(req,timeout=40) as f:return json.loads(f.read(4000000))
try:
 params=urllib.parse.urlencode({"scientificName":"Muhlenbergia dubia","institutionCode":"US","limit":80,"mediaType":"StillImage"})
 d=fetch("https://api.gbif.org/v1/occurrence/search?"+params)
 report["smithsonian_found"]=d.get("count",0)
 for x in d.get("results",[]):
  if x.get("scientificName","").split(" E.")[0].strip()!="Muhlenbergia dubia":continue
  if "smithsonian" not in str(x.get("datasetName","")).lower() and x.get("institutionCode")!="US":continue
  photos=[{"type":m.get("type"),"identifier":m.get("identifier"),"rights":m.get("rightsHolder"),"license":m.get("license"),"creator":m.get("creator"),"format":m.get("format")} for m in x.get("media",[]) if m.get("identifier")]
  if photos:
   report["smithsonian"].append({"key":x.get("key"),"institution":x.get("institutionCode"),"catalog":x.get("catalogNumber"),"basis":x.get("basisOfRecord"),"license":x.get("license"),"scientific":x.get("scientificName"),"determinedBy":x.get("identifiedBy"),"collectionCode":x.get("collectionCode"),"source":x.get("references"),"dataset":x.get("datasetName"),"media":photos[:4]})
except Exception as e:report["holds"].append("GBIF Smithsonian "+str(e)[:350])
try:
 name="Pine muhly (34180781821).jpg"
 params=urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo","iiprop":"url|size|extmetadata","titles":"File:"+name})
 d=fetch("https://commons.wikimedia.org/w/api.php?"+params)
 for entry in d.get("query",{}).get("pages",{}).values():
  if not entry.get("imageinfo"):report["holds"].append("Commons media missing");continue
  info=entry["imageinfo"][0];m=info.get("extmetadata",{})
  def val(k):return html.unescape(re.sub("<[^>]*>"," ",m.get(k,{}).get("value",""))).strip()
  report["commons"].append({"name":name,"license":val("LicenseShortName"),"credit":val("Artist"),"description":val("ImageDescription")[:700],"image_url":info.get("url"),"height":info.get("height"),"width":info.get("width"),"page":"https://commons.wikimedia.org/wiki/File:Pine_muhly_(34180781821).jpg"})
except Exception as e:report["holds"].append("Commons "+str(e)[:350])
out=pathlib.Path("reports/lane3-pine-muhly-voucher-rights-20261025.json")
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"found":report.get("smithsonian_found",0),"smithsonian_with_images":len(report["smithsonian"]),"smithsonian_sample":report["smithsonian"][:2],"commons":report["commons"],"holds":report["holds"]},ensure_ascii=False))
