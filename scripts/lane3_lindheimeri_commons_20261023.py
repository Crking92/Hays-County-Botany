#!/usr/bin/env python3
"""Lane 3: archive only exact taxon Commons photograph with creator/license verified."""
import json,io,pathlib,urllib.request,urllib.parse,hashlib
from PIL import Image,ImageOps
root=pathlib.Path("content/taxa/Poaceae/Muhlenbergia/muhlenbergia-lindheimeri")
card=root/"species.json";d=json.loads(card.read_text());assert d["id"]=="muhlenbergia-lindheimeri"
out={"added":[],"holds":[],"source":"https://commons.wikimedia.org/wiki/File:Muhlenbergia_lindheimeri.jpg"}
def get(url):
 req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyVisualLearner/1.0 (GitHub Crking92/Hays-County-Botany educational attribution)"})
 with urllib.request.urlopen(req,timeout=40) as response:return response.read(16000001)
try:
 api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata","titles":"File:Muhlenbergia lindheimeri.jpg"})
 page=next(iter(json.loads(get(api))["query"]["pages"].values()))
 info=page["imageinfo"][0];md=info["extmetadata"]
 lic=md.get("LicenseShortName",{}).get("value","")
 artist=md.get("Artist",{}).get("value","")
 if "CC BY 4.0" not in lic:raise ValueError("license not CC BY 4.0: "+lic)
 if "Cody Stricker" not in artist:raise ValueError("Cody Stricker attribution not confirmed: "+artist[:180])
 raw=get(info["url"])
 with Image.open(io.BytesIO(raw)) as im:im.verify()
 with Image.open(io.BytesIO(raw)) as im:
  im=ImageOps.exif_transpose(im).convert("RGB")
  if min(im.size)<450:raise ValueError("undersized source JPEG")
  im.thumbnail((2000,2000));buf=io.BytesIO();im.save(buf,"JPEG",quality=88,optimize=True);blob=buf.getvalue()
 rel="images/lindheimeri-cody-stricker-ccby4.jpg"
 if (root/rel).exists():raise ValueError("local image already exists; preserve")
 (root/rel).write_bytes(blob)
 for row in d["images"]:
  if row.get("inaturalist_photo_id")==85414368:
   row["file"]=rel;row["source_image_original"]=info["url"];row["sha256"]=hashlib.sha256(blob).hexdigest()
   row["photo_status"]="PHYSICALLY_ARCHIVED_OPEN_CC_BY_4; ANATOMY_MACRO_NOT_VERIFIED"
 d["visual_comparison"]["items"].append({"label":"Lindheimer's muhly — Cody Stricker Texas plant","scientific_name":"Muhlenbergia lindheimeri","image_url":str(root/rel),"image_fit":"contain","image_role":"Source-identified living-plant view; no microscopic collar or spikelet measurements","caption":"Source-labelled Muhlenbergia lindheimeri, Cody Stricker, CC BY 4.0. Use for plant-scale recognition; separately verify true collar/ligule and mature spikelet.","creator":"Cody Stricker","license":"CC BY 4.0","source_page":out["source"],"markers":[]})
 d["curation_status"]["photo_files_present"]=sum(z.get("file","").startswith("images/") for z in d["images"])
 d["curation_status"]["photo_metadata_count"]=len(d["images"])
 d["learner_visual_status"]["image_count"]=len(d["images"])
 d["learner_visual_status"]["status"]="FIELD_READY_PHOTO_GAPS"
 d["learner_visual_status"]["note"]="Now three locally archived grass photos, plus external Honey Creek grassland context image. True ligule and mature spikelet macro still missing."
 card.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
 out["added"].append({"file":str(root/rel),"sha256":hashlib.sha256(blob).hexdigest(),"license":lic})
except Exception as e:out["holds"].append(str(e)[:300])
pathlib.Path("reports/lane3-lindheimeri-commons-20261023.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out))
