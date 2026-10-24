#!/usr/bin/env python3
"""Archive native-lineage comparison image ONLY as reference, never imply Hays genotype."""
import urllib.request,urllib.parse,json,io,pathlib,hashlib
from PIL import Image,ImageOps
root=pathlib.Path("content/taxa/Poaceae/Phragmites/phragmites-australis")
card=root/"species.json";d=json.loads(card.read_text());assert d["id"]=="phragmites-australis"
name="Phragmites americanus iN-24224288.jpg"
out={"source":"https://commons.wikimedia.org/wiki/File:"+name.replace(" ","_"),"added":[],"holds":[]}
def fetch(url):
 req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyVisualLearner/1.0 (credited research image reuse; github.com/Crking92/Hays-County-Botany)"})
 with urllib.request.urlopen(req,timeout=40) as r:return r.read(17000001)
try:
 url="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata","titles":"File:"+name})
 info=next(iter(json.loads(fetch(url))["query"]["pages"].values()))["imageinfo"][0]
 ext=info["extmetadata"];lic=ext.get("LicenseShortName",{}).get("value","")
 if lic not in ("CC BY 4.0","CC BY-SA 4.0","CC0","Public domain"):raise ValueError("license not supported: "+lic)
 credit=ext.get("Artist",{}).get("value","")
 if not credit.strip():raise ValueError("missing author credit")
 b=fetch(info["url"])
 with Image.open(io.BytesIO(b)) as im:im.verify()
 with Image.open(io.BytesIO(b)) as im:
  im=ImageOps.exif_transpose(im).convert("RGB")
  if min(im.size)<450:raise ValueError("source resolution insufficient")
  im.thumbnail((1800,1800));buffer=io.BytesIO();im.save(buffer,"JPEG",quality=88,optimize=True);raw=buffer.getvalue()
 rel="images/native-americanus-reference-24224288.jpg";dest=root/rel
 if dest.exists():raise ValueError("already present; not overwritten")
 dest.write_bytes(raw)
 d["images"].append({"file":rel,"role":"Native American reed COMPARISON only; no local population or genotype conclusion","creator":credit,"license":lic,"source_page":out["source"],"source_taxon_name":"Phragmites americanus","lineage_caution":"Source-labelled native lineage comparison from outside Texas; photograph does not establish identity of Hays County reed","sha256":hashlib.sha256(raw).hexdigest(),"modifications":"Resized and EXIF removed"})
 for panel in d["visual_comparison"]["items"]:
  if "Phragmites_americanus_iN-24224288" in panel.get("image_url",""):
   panel["image_url"]=str(root/rel);panel["license"]=lic;panel["source_page"]=out["source"];panel["photo_status"]="LOCAL_LICENSED_NATIVE_COMPARISON_NOT_TEXAS_LINEAGE_EVIDENCE"
 d["curation_status"]["photo_metadata_count"]=len(d["images"]);d["curation_status"]["photo_files_present"]=len(d["images"])
 d["learner_visual_status"]["image_count"]=len(d["images"])
 card.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
 out["added"].append({"file":str(dest),"license":lic,"sha256":hashlib.sha256(raw).hexdigest()})
except Exception as exc:out["holds"].append(str(exc)[:300])
pathlib.Path("reports/lane3-phragmites-native-reference-20261023.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out))
