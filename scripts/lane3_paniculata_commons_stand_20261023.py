#!/usr/bin/env python3
"""Archive authenticated tumblegrass stand by Matt Lavin, rights-checked from Commons."""
import json,pathlib,urllib.parse,urllib.request,io,hashlib
from PIL import Image,ImageOps
root=pathlib.Path("content/taxa/Poaceae/Muhlenbergia/muhlenbergia-paniculata");card=root/"species.json"
d=json.loads(card.read_text());assert d["id"]=="muhlenbergia-paniculata"
filename="Schedonnardus paniculatus (3883870771).jpg"
source="https://commons.wikimedia.org/wiki/File:Schedonnardus_paniculatus_(3883870771).jpg"
report={"source":source,"added":[],"holds":[]}
def fetch(url):
 req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyVisualLearner/1.0 (credited botany educational reuse; github.com/Crking92/Hays-County-Botany)"})
 with urllib.request.urlopen(req,timeout=45) as res:return res.read(18000001)
try:
 url="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata","titles":"File:"+filename})
 info=next(iter(json.loads(fetch(url))["query"]["pages"].values()))["imageinfo"][0]
 lic=info["extmetadata"]["LicenseShortName"]["value"];artist=info["extmetadata"]["Artist"]["value"]
 assert "CC BY-SA 2.0" in lic, lic
 assert "Matt Lavin" in artist, "artist attribution not confirmed"
 raw=fetch(info["url"])
 with Image.open(io.BytesIO(raw)) as im:im.verify()
 with Image.open(io.BytesIO(raw)) as im:
  im=ImageOps.exif_transpose(im).convert("RGB")
  assert min(im.size)>=450
  im.thumbnail((2000,2000));buf=io.BytesIO();im.save(buf,"JPEG",quality=87,optimize=True);blob=buf.getvalue()
 rel="images/matt-lavin-schedonnardus-stand-3883870771-cc-by-sa2.jpg";dest=root/rel
 assert not dest.exists(), "already archived"
 dest.write_bytes(blob)
 credit={"file":rel,"role":"Source-labelled tumblegrass field stand, branching seed heads and habitat; botanical microanatomy unverified","creator":"Matt Lavin","license":"CC BY-SA 2.0","source_page":source,"source_taxon_name":"Schedonnardus paniculatus","taxonomic_basis":"Synonym of Muhlenbergia paniculata per existing canonical card","sha256":hashlib.sha256(blob).hexdigest(),"photo_status":"LOCAL_EXACT_HISTORIC_SYNONYM_OPEN_LICENSE_ANATOMY_HOLD","modifications":"Resized; EXIF stripped"}
 d["images"].append(credit)
 d["visual_comparison"]["items"].append({"label":"Tumblegrass — mature spreading stand and dispersal heads","scientific_name":"Muhlenbergia paniculata (syn. Schedonnardus paniculatus)","image_url":str(root/rel),"image_fit":"contain","image_role":"Source-labelled field stand and characteristic flowering habit","caption":"Matt Lavin photographed a stand with conspicuous mature dispersal heads. Whole-plant growth form; not a scale-verified ligule, glume or single spikelet macro.","creator":"Matt Lavin","license":"CC BY-SA 2.0","source_page":source,"markers":[]})
 d["learner_visual_status"]["status"]="FIELD_READY_PHOTO_GAPS";d["learner_visual_status"]["image_count"]=len(d["images"])
 d["learner_visual_status"]["note"]="Three archived images, including two CC BY-SA Matt Lavin sources. Stand and inflorescence supported; true ligule, detached mature spikelet and glume/lemma scale macro still missing."
 d["curation_status"]["photo_files_present"]=len(d["images"]);d["curation_status"]["photo_metadata_count"]=len(d["images"])
 card.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
 report["added"].append({"file":str(dest),"sha256":hashlib.sha256(blob).hexdigest(),"license":lic})
except Exception as exc:report["holds"].append(str(exc)[:300])
pathlib.Path("reports/lane3-paniculata-commons-stand-20261023.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
