#!/usr/bin/env python3
"""Archive verified Commons grass images into canonical folders in small capped batches.
Retains originals/metadata; swaps direct gallery and comparison-panel external refs
only after actual JPEG write; rejects changed/ambiguous licenses.
"""
from __future__ import annotations
import argparse,collections,hashlib,html,io,json,pathlib,re,time,urllib.parse,urllib.request,urllib.error
from PIL import Image
ROOT=pathlib.Path(".")
VALID={"CC0","PUBLICDOMAIN","PDM","NORESTRICTIONS","CCBY2.0","CCBY3.0","CCBY3.0US","CCBY4.0","CCBYSA2.0","CCBYSA3.0","CCBYSA4.0","CCBYNC2.0","CCBYNC3.0","CCBYNC4.0","CCBYNCSA2.0","CCBYNCSA3.0","CCBYNCSA4.0"}
def normalize(s):return re.sub(r"[^A-Z0-9]","",str(s).upper())
def fetch(url):
 for retry in range(4):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 (botanical educational photo archive; contact via GitHub repository)"}),timeout=65) as res:return res.read()
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or retry==3:raise
   time.sleep(20*(retry+1))
def info_for(url):
 parts=urllib.parse.urlparse(url)
 if parts.netloc=="commons.wikimedia.org" and "/Special:Redirect/file/" in parts.path:
  name=urllib.parse.unquote(parts.path.split("/Special:Redirect/file/")[-1])
 elif parts.netloc=="upload.wikimedia.org":
  name=urllib.parse.unquote(parts.path.split("/")[-1])
 else:raise ValueError("Not a Wikimedia source URL")
 api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","prop":"imageinfo","iiprop":"url|extmetadata","titles":"File:"+name,"format":"json"})
 pages=json.loads(fetch(api))["query"]["pages"]
 page=next(iter(pages.values()))
 if "imageinfo" not in page:raise ValueError("Commons file not found: "+name)
 return name,page["imageinfo"][0]
def replace_urls(value,mapping):
 if isinstance(value,dict):
  return {k:replace_urls(v,mapping) for k,v in value.items()}
 if isinstance(value,list):return [replace_urls(v,mapping) for v in value]
 if isinstance(value,str):return mapping.get(value,value)
 return value
def main():
 parser=argparse.ArgumentParser();parser.add_argument("--start",type=int,default=0);parser.add_argument("--limit",type=int,default=10)
 opts=parser.parse_args()
 assert 0<=opts.start<=101 and 0<opts.limit<=12
 manifest=json.loads((ROOT/"data/manifest.json").read_text())["species"]
 work=[];host_counts=collections.Counter()
 for entry in manifest:
  if "/Poaceae/" not in entry["path"]:continue
  p=ROOT/entry["path"];card=json.loads(p.read_text())
  for ix,photo in enumerate(card.get("images",[])):
   url=photo.get("file","")
   if not url.startswith(("https://","http://")):continue
   host=urllib.parse.urlparse(url).netloc;host_counts[host]+=1
   work.append((entry["id"],str(p),ix,url))
 work.sort(key=lambda z:(z[0],z[2]))
 eligible=[x for x in work if urllib.parse.urlparse(x[3]).netloc in ("commons.wikimedia.org","upload.wikimedia.org")]
 selected=eligible[opts.start:opts.start+opts.limit]
 report={"scope":"Wikimedia-hosted external image references in all 112 grass cards","total_external":len(work),"by_host":dict(host_counts),"wikimedia_candidates":len(eligible),"batch_start":opts.start,"batch_limit":opts.limit,"selected":len(selected),"archived":[],"held":[]}
 for taxon,path,ix,url in selected:
  try:
   p=pathlib.Path(path);card=json.loads(p.read_text())
   source=card["images"][ix]
   if source.get("file")!=url:raise ValueError("Image ordering changed while processing")
   name,info=info_for(url)
   metadata=info.get("extmetadata",{})
   license=metadata.get("LicenseShortName",{}).get("value","")
   norm=normalize(license)
   if norm not in {normalize(v) for v in VALID}:raise ValueError("Unapproved license: "+license)
   declared=normalize(source.get("license",""))
   # An original license mismatch requires manual review; Commons can have more than one alias.
   if declared and declared not in norm and norm not in declared:
    if not (declared in ("PUBLICDOMAIN","CC0") and norm in ("PUBLICDOMAIN","PDM","CC0","NORESTRICTIONS")):
     raise ValueError("Source vs Commons license differs: "+source.get("license","")+" / "+license)
   creator=html.unescape(re.sub(r"<[^>]*>","",metadata.get("Artist",{}).get("value",""))).strip()
   if not creator and norm not in ("PUBLICDOMAIN","CC0","PDM","NORESTRICTIONS"):raise ValueError("Missing image-level creator credit")
   payload=fetch(info["url"])
   if not 10000<len(payload)<25000000:raise ValueError("Unexpected image byte length")
   image=Image.open(io.BytesIO(payload));image.verify()
   image=Image.open(io.BytesIO(payload)).convert("RGB")
   if min(image.size)<250:raise ValueError("Source resolution too small")
   dest_name="commons-archive-"+hashlib.sha256(url.encode()).hexdigest()[:16]+".jpg"
   dest=p.parent/"images"/dest_name
   dest.parent.mkdir(parents=True,exist_ok=True)
   image.save(dest,"JPEG",quality=90,optimize=True)
   new_file="images/"+dest_name
   previous=url
   source["file"]=new_file
   source["archived_original_url"]=previous
   source["archived_original_commons_filename"]=name
   source["archive_license_verified"]=license
   source["archive_creator_metadata"]=creator
   source["archive_status"]="LOCALLY_STORED; original source attribution and anatomy notes preserved"
   reference=p.parent/new_file
   mapping={previous:str(reference).replace("\\","/")}
   card=replace_urls(card,mapping)
   card["images"][ix]["file"]=new_file
   card["images"][ix]["archived_original_url"]=previous
   card.setdefault("learner_visual_status",{})["image_count"]=len(card["images"])
   p.write_text(json.dumps(card,indent=2,ensure_ascii=False)+"\n")
   report["archived"].append({"species":taxon,"source":previous,"dest":str(reference),"license":license})
   print("ARCHIVED",taxon,name,flush=True)
  except Exception as ex:
   report["held"].append({"species":taxon,"url":url,"reason":str(ex)})
   print("HELD",taxon,str(ex),flush=True)
 out=ROOT/"reports"/("grass-external-wikimedia-batch-%03d.json"%opts.start)
 out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps({"archived":len(report["archived"]),"held":len(report["held"]),"total_external":report["total_external"],"hosts":report["by_host"]}))
if __name__=="__main__":main()
