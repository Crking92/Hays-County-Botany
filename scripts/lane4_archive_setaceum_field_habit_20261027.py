#!/usr/bin/env python3
"""Archive one independently verified CC BY 4.0 Paspalum setaceum field-growing photograph.

Not a Hays native-range determination, not ligule, not exposed root. No false arrows.
"""
import urllib.parse,urllib.request,urllib.error,json,pathlib,re,io,hashlib,time
from PIL import Image,ImageOps
BASE=pathlib.Path("content/taxa/Poaceae/Paspalum/paspalum-setaceum")
CARD=BASE/"species.json"
PAGE="https://commons.wikimedia.org/wiki/File:Paspalum_setaceum_49099738.jpg"
SOURCE="https://www.inaturalist.org/photos/49099738"
TARGET="images/alex-abair-49099738-field-habit.jpg"
TITLE="File:Paspalum setaceum 49099738.jpg"
def load(url,size=13000000):
 err=None
 for attempt in range(4):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany-Lane4/1.0 (educational source image CC attribution audit)"})
   with urllib.request.urlopen(req,timeout=60) as r: data=r.read(size+1)
   if len(data)>size:raise ValueError("download oversized")
   return data
  except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as e:
   err=e
   if isinstance(e,urllib.error.HTTPError) and e.code not in (429,500,502,503,504):raise
   time.sleep(3*(attempt+1))
 raise RuntimeError(repr(err))
def main():
 q=urllib.parse.urlencode({"action":"query","titles":TITLE,"prop":"imageinfo","iiprop":"url|extmetadata|size|sha1","iiurlwidth":1400,"format":"json"})
 result=json.loads(load("https://commons.wikimedia.org/w/api.php?"+q,2000000))
 page=next(iter(result["query"]["pages"].values()));assert page.get("title","").casefold()==TITLE.casefold()
 info=page["imageinfo"][0];meta=info.get("extmetadata",{})
 license=re.sub("[^a-z0-9.]","",meta.get("LicenseShortName",{}).get("value","").lower())
 artist=meta.get("Artist",{}).get("value","").lower()
 assert license=="ccby4.0",(license,"wrong photo rights")
 assert "alex abair" in artist,(artist[:120],"wrong author")
 assert info.get("width",0)>=1400 and info.get("height",0)>=1800
 url=info.get("thumburl") or info.get("url");assert "wikimedia.org" in url
 raw=load(url);assert raw[:2]==b"\xff\xd8"
 pic=Image.open(io.BytesIO(raw));pic.verify()
 pic=ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
 assert pic.width>=900 and pic.height>=1000
 dest=BASE/TARGET;dest.parent.mkdir(parents=True,exist_ok=True)
 pic.save(dest,"JPEG",quality=91,optimize=True)
 saved=dest.read_bytes();test=Image.open(io.BytesIO(saved))
 assert test.size==pic.size and not test.getexif() and "exif" not in test.info
 d=json.loads(CARD.read_text())
 assert d["id"]=="paspalum-setaceum" and len(d["images"])>=3
 if not any(x.get("source_page")==PAGE for x in d["images"]):
  d["images"].append({
    "file":TARGET,"role":"Original field-growing live plant and leafy aboveground habit; one actual flowering culm near tuft but connected roots and free ligule NOT visible",
    "creator":"Alex Abair","license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/",
    "source_page":PAGE,"source_photo_page":SOURCE,"source_observation":"https://www.inaturalist.org/observations/31376126",
    "public_reuse":"Individual Commons file CC BY4 with author/source/license/derivative change notice.",
    "photo_status":"Species photographed in Florida by Alex Abair; genuine field upright culm and leafy base. Soil hides roots, no inner free ligule/microspikelet from this distant photograph.",
    "modifications":"Downloaded proportionally resized un-cropped JPEG, re-encoded RGB to strip GPS/EXIF; no painted changes.",
    "archive_sha256":hashlib.sha256(saved).hexdigest(),"image_dimensions":list(pic.size)
  })
 if not any(x.get("source_page")==PAGE for x in d["visual_comparison"]["items"]):
  d["visual_comparison"]["items"].append({
    "label":"LIVE FIELD HABIT — thin paspalum flowering shoot with green basal leaves (exact species source)",
    "scientific_name":"Paspalum setaceum",
    "image_url":(BASE/TARGET).as_posix(),"image_fit":"contain",
    "image_role":"Real Alex Abair field-growing Paspalum setaceum from Florida, with slim flowering axis and green sheathing leaves amid other vegetation. Individual inner ligule/root attachment not visible.",
    "caption":"CC BY 4.0 exact plant source photograph by Alex Abair taken in the field. The growing leafy culms and spikelet stalks can be compared with close reproductive photos already in this card; multiple surrounding plants prevent tracing a single rooted crown to every head. Do not infer Texas locality, or a measured true ligule.",
    "why_it_matters":"Actual growing form rather than only detached flowering branch; valuable for crew's field visual recognition even where diagnostic ligule remains absent.",
    "creator":"Alex Abair","license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/",
    "source_page":PAGE,"markers":[],
    "modifications":"Uncropped resized RGB JPEG, GPS/EXIF stripped; no annotations",
    "photo_status":"Exact source and CC license verified and local photo byte archived. Original field plant photo pixels preview checked 2026-10-27; full local pixel QA to follow."
  })
 d["curation_status"]["photo_metadata_count"]=len(d["images"])
 d["curation_status"]["photo_files_present"]=sum(x.get("file","").startswith("images/") for x in d["images"])
 d["learner_visual_status"]["image_count"]=len(d["images"])
 d["field_id_finish_pass"]["lane4_setaceum_field_photo_20261027"]={"new_original_file":TARGET,"source":PAGE,"image_sha256":hashlib.sha256(saved).hexdigest(),
    "rights":"Alex Abair one individual CC BY 4.0 Commons-reviewed original, license and attribution preserved",
    "photo_evidence":"actual field growing plant showing grass's whole leafy habit; no inner ligule or roots, no microscopic anatomy",
    "new_arrows":0,"new_species_photo_files":1,"publication":"NOT VERIFIED"}
 CARD.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
 print("INSTALLED "+str(dest)+" "+str(pic.size)+" "+hashlib.sha256(saved).hexdigest(),flush=True)
if __name__=="__main__":main()
