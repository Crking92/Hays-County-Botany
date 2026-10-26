#!/usr/bin/env python3
"""Lane 2 archive a Research Grade CC BY sand lovegrass blade–sheath photograph from Blanco County.
Strictly OUTSIDE sheath geometry: no unphotographed ligule or collar hair labels.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageOps
from hashlib import sha256
import io,json
ROOT=Path("content/taxa/Poaceae/Eragrostis/eragrostis-trichodes")
CARD=ROOT/"species.json"
OUT=ROOT/"images"/"cody-stricker-blanco-blade-sheath-480904239.jpg"
REPORT=Path("reports/lane2-trichodes-blanco-sheath-photo-20261026.json")
PID=480904239
OID=267593301
UA={"User-Agent":"HaysCountyBotanyLearner/1.0 (photo-level CC BY verification and noncommercial education)"}
SRC=f"https://www.inaturalist.org/photos/{PID}"
def main():
 with urlopen(Request(f"https://api.inaturalist.org/v1/observations/{OID}",headers=UA),timeout=38) as h:d=json.load(h)
 assert len(d.get("results",[]))==1
 o=d["results"][0]
 assert o["id"]==OID and o["quality_grade"]=="research" and o["taxon"]["name"]=="Eragrostis trichodes"
 assert "Blanco County" in o.get("place_guess",""),"Source locality unexpectedly changed"
 photo=next(p for p in o["photos"] if p["id"]==PID)
 assert photo.get("license_code")=="cc-by",photo.get("license_code")
 assert "Cody Stricker" in photo.get("attribution",""),photo.get("attribution")
 u=f"https://inaturalist-open-data.s3.amazonaws.com/photos/{PID}/original.jpg"
 with urlopen(Request(u,headers=UA),timeout=45) as h:
  assert h.url.startswith("https://inaturalist-open-data.s3.amazonaws.com/")
  data=h.read(10_000_001)
 assert 100_000<len(data)<10_000_001
 with Image.open(io.BytesIO(data)) as src:
  assert src.format=="JPEG" and src.size==(1536,2048),src.size
  image=ImageOps.exif_transpose(src).convert("RGB")
 b=io.BytesIO();image.save(b,format="JPEG",quality=89,optimize=True)
 payload=b.getvalue()
 with Image.open(io.BytesIO(payload)) as check:
  assert check.format=="JPEG" and not check.getexif()
 OUT.parent.mkdir(parents=True,exist_ok=True)
 if OUT.exists():
  assert OUT.read_bytes()==payload,"Different existing file; hold"
 else:OUT.write_bytes(payload)
 j=json.loads(CARD.read_text(encoding="utf-8"))
 assert j["id"]=="eragrostis-trichodes"
 assert not any(x.get("source_page")==SRC for x in j["images"]),"Another worker installed same photo"
 rel="images/"+OUT.name
 j["images"].append({
   "file":rel,"role":"SOURCE VERIFIED LIVE BLANCO COUNTY exterior blade–sheath V where long narrow blade emerges from enclosing basal sheath. No opened inner ligule or 0.4-mm cilia demonstrated.",
   "creator":"Cody Stricker",
   "license":"CC BY (iNaturalist original photo-level code cc-by)",
   "license_url":"https://creativecommons.org/licenses/by/4.0/",
   "source_page":SRC,"source_observation_page":f"https://www.inaturalist.org/observations/{OID}",
   "source_locality":"Blanco County, TX (regional, NOT Hays County voucher)",
   "photo_status":"2026-10-26 original 1536×2048 Research Grade Eragrostis trichodes pixels actually inspected and photo-level license verified. Outer blade–sheath geometry yes; true inner ligule NO.",
   "modifications":"Original RGB JPEG re-encoded to remove EXIF and GPS; no crop; browser arrow separate",
   "public_reuse":"Yes CC BY with source and creator credit, adaptation notice."
 })
 url="content/taxa/Poaceae/Eragrostis/eragrostis-trichodes/"+rel
 panels=j["visual_comparison"]["items"]
 idx=next((i for i,x in enumerate(panels) if x.get("scientific_name")!="Eragrostis trichodes"),len(panels))
 panels.insert(idx,{
   "label":"BLANCO COUNTY · actual external leaf blade / sheath V-junction",
   "scientific_name":"Eragrostis trichodes","image_url":url,"image_fit":"contain",
   "image_role":"Live local-region native sand lovegrass blade, green enclosing sheath and obvious external V attachment; true ligule remains hidden",
   "caption":"Cody Stricker's March 2025 Blanco County Research Grade E. trichodes photograph shows a narrow green leaf blade diverging from a sheathing section around the stem. One arrow marks the visible exterior junction ONLY; the very short inner densely ciliate ligule (~0.4 mm) and longer oral hairs have not been opened or scaled. This is useful local-region field reference, but not a specimen from Hays County.",
   "why_it_matters":"Adds a nearby Edwards Plateau source and an unobstructed blade/sheath junction to pair with the existing broad clump and spikelet lessons; trains crew exactly where to peel the blade back for a ligule photo.",
   "creator":"Cody Stricker","license":"CC BY (iNaturalist photo-level code cc-by)",
   "license_url":"https://creativecommons.org/licenses/by/4.0/","source_page":SRC,
   "modifications":"Image EXIF/GPS stripped, no crop; annotation SVG over unmarked JPEG",
   "photo_status":"Original source pixels inspected 2026-10-26, Research Grade source photo, one precisely delimited junction arrow; 0.4-mm true ligule NOT resolved.",
   "markers":[{"label":"Blade–sheath V (true ligule hidden inside)","label_x":4,"label_y":46,"target_x":54,"target_y":51}]
 })
 j["field_photo_quickcheck"]["featured_photo_indices"]=list(range(idx+1))
 j["field_photo_quickcheck"]["steps"].insert(1,"BLANCO COUNTY FIELD MACRO: open the credited Cody Stricker original blade–sheath V photo. This shows the OUTSIDE junction and exactly which blade to pull away. It still cannot show the tiny white ~0.4-mm inner ligule or separately measured 4–5-mm sheath-throat hairs.")
 j["field_photo_quickcheck"]["warning"]+=" Lane 2 2026-10-26: new regional Research Grade Cody Stricker CC BY close photograph of external blade–sheath V archived; one junction arrow added; no calibrated true ligule or whole-root connection. Do not call strict completion."
 j["curation_status"]["photo_metadata_count"]=len(j["images"])
 j["curation_status"]["photo_files_present"]=sum(str(x.get("file","")).startswith("images/") for x in j["images"])
 j["curation_status"]["lane2_blanco_junction_20261026"]="REAL NEARBY FIELD GROWTH AND EXTERIOR BLADE SHEATH MACRO ONLY, NOT TRUE LIGULE"
 j["photo_note"]=j.get("photo_note","")+"\n2026-10-26 source/photo CC BY confirmed true E. trichodes Research Grade Blanco County exterior blade–sheath photo locally archived. 1 anatomy-limited arrow; inner true ligule with scale still absent."
 if isinstance(j.get("learner_visual_status"),dict):j["learner_visual_status"]["image_count"]=len(j["images"])
 CARD.write_text(json.dumps(j,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 REPORT.parent.mkdir(parents=True,exist_ok=True)
 REPORT.write_text(json.dumps({"species":"Eragrostis trichodes","original_photo_id":PID,"source_observation_id":OID,"creator":"Cody Stricker","license":"CC BY original photo-level verified","photo_url":SRC,"source_region":"Blanco County TX","photo_path":str(OUT),"sha256":sha256(payload).hexdigest(),"bytes":len(payload),"archived_dimensions":[1536,2048],"new_JPEGs":1,"current_local_JPEGs":j["curation_status"]["photo_files_present"],"new_arrows":1,"conclusion":"External blade-sheath junction visible, true internal 0.4-mm ligule still missing", "stage":"FIELD_READY_PHOTO_GAPS","public_website_live_not_confirmed":True},indent=2)+"\n",encoding="utf-8")
 print("ARCHIVED_BLANC0_SAND_LOVEGRASS",str(OUT),len(payload))
if __name__=="__main__":main()
