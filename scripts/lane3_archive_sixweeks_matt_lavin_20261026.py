#!/usr/bin/env python3
"""Physically archive the already-public-gallery Matt Lavin CC BY-SA 2.0 Zion living habit image.
Exact Commons source file and Flickr original photo ID checked against canonical gallery.
Archive resized with metadata/GPS removed and retain ShareAlike 2.0 and attribution.
Do not duplicate or replace copyrighted Bob Harms external images.
"""
import io,json,pathlib,urllib.request,hashlib
from PIL import Image,ImageOps
BASE=pathlib.Path("content/taxa/Poaceae/Festuca/festuca-octoflora")
CARD=BASE/"species.json"
REPORT=pathlib.Path("reports/lane3-sixweeks-matt-lavin-archive-20261026.json")
NAME="images/sixweeks-matt-lavin-zion-6243564299-ccby-sa2.jpg"
LOCAL=BASE/NAME
URLS=[
 "https://upload.wikimedia.org/wikipedia/commons/0/03/Vulpia_octoflora_%286243564299%29.jpg",
 "https://live.staticflickr.com/6098/6243564299_e27cf97a4b_o.jpg",
]
SOURCE="https://commons.wikimedia.org/wiki/File:Vulpia_octoflora_(6243564299).jpg"
def download(url):
 request=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 (public CC BY-SA educational image archiver; github.com/Crking92/Hays-County-Botany)","Accept":"image/jpeg,image/*"})
 with urllib.request.urlopen(request,timeout=50) as response:
  if "image" not in response.headers.get("content-type","").lower():
   raise ValueError("Not image media")
  data=response.read(11_000_001)
 if not 250000<len(data)<11_000_001:raise ValueError("Invalid expected original length")
 return data
d=json.loads(CARD.read_text())
assert d["id"]=="festuca-octoflora" and len(d["images"])==7
ps=d["visual_comparison"]["items"]
panels=[x for x in ps if x.get("source_page")==SOURCE]
assert len(panels)==1,"Previous specific Commons source panel must be unique"
panel=panels[0]
assert panel["creator"]=="Matt Lavin" and panel["license"]=="CC BY-SA 2.0"
assert "6243564299" in panel["image_url"] or panel["image_url"]==str(LOCAL)
assert not LOCAL.exists(),"Existing installed image—no overwriting without review"
errors=[];raw=None;origin=None
for url in URLS:
 try:
  payload=download(url)
  with Image.open(io.BytesIO(payload)) as im:
   assert im.format=="JPEG"
   assert im.size==(4320,3240), f"Unexpected dimensions {im.size}"
   im.verify()
  raw=payload;origin=url;break
 except Exception as e:
  errors.append({"url":url,"reason":str(e)[:220]})
if raw is None:
 REPORT.write_text(json.dumps({"status":"HOLD_NO_VERIFIED_ORIGINAL","rights":"Original CC BY-SA 2.0 retained as external unchanged source","attempts":errors},indent=2)+"\n")
 raise SystemExit("No successfully retrieved full original JPEG")
with Image.open(io.BytesIO(raw)) as im:
 im=ImageOps.exif_transpose(im).convert("RGB")
 im.thumbnail((2200,2200),Image.Resampling.LANCZOS)
 b=io.BytesIO();im.save(b,"JPEG",quality=90,optimize=True);processed=b.getvalue()
with Image.open(io.BytesIO(processed)) as im:
 assert not im.getexif().get(34853)
 im.verify()
LOCAL.parent.mkdir(parents=True,exist_ok=True)
LOCAL.write_bytes(processed)
saved_hash=hashlib.sha256(processed).hexdigest()
newrow={
"file":NAME,"role":"Living in-situ whole annual grass in Utah rocky ledge with narrow attached flowering panicles; roots remain hidden",
"creator":"Matt Lavin","license":"CC BY-SA 2.0",
"license_url":"https://creativecommons.org/licenses/by-sa/2.0/",
"source_page":SOURCE,"original_source_page":"https://www.flickr.com/photos/plant_diversity/6243564299/",
"source_image_original":origin,"flickr_photo_id":"6243564299",
"raw_source_sha256":hashlib.sha256(raw).hexdigest(),
"physical_archive_sha256":saved_hash,
"source_original_dimensions":[4320,3240],
"modifications":"Resized to fit within 2200 px and resaved as JPEG with EXIF/GPS removed; no crop or baked-in arrows. This reproduction and its photographic adaptations remain governed by CC BY-SA 2.0, with Matt Lavin attribution.",
"photo_status":"EXACT COMMONS ORIGINAL SOURCE RIGHTS CC BY-SA 2.0 VERIFIED, LOCALLY ARCHIVED; published source adult habit, roots unseen"
}
d["images"].append(newrow)
panel["image_url"]=str(LOCAL)
panel["source_image"]=origin
panel["modification_note"]=newrow["modifications"]
panel["photo_status"]="LOCALLY_ARCHIVED_FULL_COMMONS_SOURCE_CC_BY_SA_2.0; original habits/flowering arrow overlays from prior lesson retained; microscopic ligule/roots not photographed"
d["curation_status"]["photo_metadata_count"]=len(d["images"])
d["curation_status"]["photo_files_present"]=len(d["images"])
d["curation_status"]["lane3_matt_lavin_zion_archive_20261026"]="Previously external Matt Lavin Zion whole-plant/attached flowering panicles physically archived, source page CC BY-SA 2.0/creator preserved and resized with EXIF/GPS stripped. Root crown still underground.";
if isinstance(d.get("learner_visual_status"),dict):
 d["learner_visual_status"]["image_count"]=len(d["images"])
d["field_id_finish_pass"]["lane3_matt_lavin_zion_archive_20261026"]={
"new_local_real_photo":1,"total_local_image_files":len(d["images"]),
"source":"Wikimedia Commons exact file 6243564299 originally from Matt Lavin Flickr",
"rights":"CC BY-SA 2.0, author credit, original page, license and modification note stored",
"roles":"Living wild annual grass HABIT + attached narrow flowering heads; not exposed underground roots or inner collar/ligule",
"scientific_holds_preserved":True}
CARD.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
REPORT.write_text(json.dumps({"status":"LOCALLY_ARCHIVED_MATT_LAVIN_CC_BY_SA_2","new_image_file":str(LOCAL),
"original_source":origin,"source_page":SOURCE,"creator":"Matt Lavin","license":"CC BY-SA 2.0",
"original_sha256":hashlib.sha256(raw).hexdigest(),"archived_sha256":saved_hash,
"new_files":1,"total_species_local_files":len(d["images"]),"gallery_panels":len(ps),"attempts":errors},indent=2)+"\n")
print(json.dumps({"result":"LOCALLY_ARCHIVED_MATT_LAVIN_CC_BY_SA_2","photo_files":len(d["images"]),"file":str(LOCAL)}))
