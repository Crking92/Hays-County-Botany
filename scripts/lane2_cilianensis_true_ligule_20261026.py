#!/usr/bin/env python3
"""Archive source-licensed, species-specific collar and true ligule photographs for Eragrostis cilianensis.
No image from another taxon, no invented micrometer measurements, no changes to old science or rights.
"""
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from PIL import Image,ImageOps
import io,json,re,hashlib,html

BASE=Path("content/taxa/Poaceae/Eragrostis/eragrostis-cilianensis")
CARD=BASE/"species.json"
REPORT=Path("reports/lane2-cilianensis-scaled-ligule-sheath-20261026.json")
UA={"User-Agent":"HaysBotanyLearner/1.0 (source-licensed anatomical photos)"}
LIC="https://creativecommons.org/licenses/by-sa/4.0/"
photos=[
 {
 "name":"Eragrostis cilianensis sl4.jpg","out":"stefan-cilianensis-true-ligule-3mm-sl4.jpg",
 "dims":[2216,2442],"role":"REAL species-labelled TRUE ligule closeup: opened blade/sheath interface showing a short whitish fringe; original 3-mm scale printed on photograph",
 "label":"TRUE LIGULE · real white hair fringe at inner sheath mouth; printed 3-mm scale",
 "caption":"Stefan.lefnaer's exact-species Eragrostis cilianensis macro shows the real whitish SHORT ligule fringe inside the blade–sheath interface, with the photographer's printed 3-mm scale. The arrow marks the visible white fringe, not longer external collar hairs. From Croatia, not Hays County, and no length claimed without image-specific scale calibration.",
 "reason":"Teaches a genuinely photographed inner ligule rather than guessing from exterior hairs at the throat.",
 "markers":[{"label":"True white ligule hair fringe","label_x":75,"label_y":17,"target_x":55,"target_y":31}],
 "visible":"white fringe at internal blade-sheath junction and 3-mm source-printed scale; no gland pits demonstrated"
 },
 {
 "name":"Eragrostis cilianensis sl1.jpg","out":"stefan-cilianensis-blade-sheath-overview-10mm-sl1.jpg",
 "dims":[2816,3744],"role":"REAL multi-view photographer montage: sheath around culm, outer blade base, three blade/sheath junction angles, original printed 10-mm scale",
 "label":"BLADE–SHEATH JUNCTION · four true source views; printed 10-mm scale",
 "caption":"Four original source views of an Eragrostis cilianensis culm and sheath–blade junction. At a glance the leaf blade and the sheathing portion can be tracked separately. This photograph supplies surrounding context for the tiny true ligule shown in the dedicated sl4 macro; no glandular spots or precise ligule height inferred.",
 "reason":"Shows crew where to open the folded sheath to find the tiny ligule on the inside.",
 "markers":[{"label":"Outside blade–sheath junction","label_x":74,"label_y":70,"target_x":59,"target_y":77}],
 "visible":"four photographed blade/sheath overlaps, with original 10-mm reference scale; not a close inner ligule measurement"
 }
]
def get(url,limit=11_000_000):
 with urlopen(Request(url,headers=UA),timeout=45) as response:
  data=response.read(limit+1)
  assert len(data)<=limit
  return response.url,data

def main():
 card=json.loads(CARD.read_text(encoding="utf-8"))
 assert card["id"]=="eragrostis-cilianensis"
 existing={p.get("source_page") for p in card["images"]}
 records=[]
 to_insert=[]
 for p in photos:
  source="https://commons.wikimedia.org/wiki/File:"+p["name"].replace(" ","_")
  assert source not in existing,"Photo already in metadata; audit manually before retry"
  query=urlencode({"action":"query","titles":"File:"+p["name"],"prop":"imageinfo","iiprop":"url|extmetadata|size","format":"json"})
  _,data=get("https://commons.wikimedia.org/w/api.php?"+query,2_000_000)
  page=next(iter(json.loads(data)["query"]["pages"].values()))
  assert page["title"]=="File:"+p["name"]
  info=page["imageinfo"][0]
  assert [info["width"],info["height"]]==p["dims"],"Source dimension changed"
  meta=info["extmetadata"]
  license_short=html.unescape(meta["LicenseShortName"]["value"]).lower()
  creator=html.unescape(meta["Artist"]["value"])
  assert "by-sa 4.0" in license_short and "Stefan.lefnaer" in creator, (license_short,creator[:120])
  remote=info["url"]
  assert remote.startswith("https://upload.wikimedia.org/wikipedia/commons/")
  final,raw=get(remote,11_000_000)
  assert final.startswith("https://upload.wikimedia.org/") and len(raw)>100000
  with Image.open(io.BytesIO(raw)) as im:
   assert im.format=="JPEG" and list(im.size)==p["dims"]
   image=ImageOps.exif_transpose(im).convert("RGB")
  image.thumbnail((2600,2600))
  output=io.BytesIO()
  image.save(output,"JPEG",quality=90,optimize=True)
  clean=output.getvalue()
  with Image.open(io.BytesIO(clean)) as check:
   assert check.format=="JPEG" and not check.getexif()
  path=BASE/"images"/p["out"]
  path.parent.mkdir(parents=True,exist_ok=True)
  if path.exists():
   assert path.read_bytes()==clean,"Existing different binary, refusing overwrite"
  else:path.write_bytes(clean)
  rel="images/"+p["out"]
  card["images"].append({
    "file":rel,"role":p["role"],"creator":"Stefan.lefnaer","license":"CC BY-SA 4.0","license_url":LIC,
    "source_page":source,"source_locality":"Krk, Croatia, photographer-identified E. cilianensis; NOT a Texas voucher",
    "public_reuse":"Yes CC BY-SA 4.0, credit, link and ShareAlike for adaptation",
    "photo_status":"True original species-specific anatomical pixels and image-level license verified, source 2021-10-11, EXIF scrubbed archival JPEG 2026-10-26",
    "modifications":"Re-encoded RGB JPEG, EXIF/GPS removed, downscaled longest side to at most 2600 px, no crop; SVG arrow overlay kept separate"
  })
  u="content/taxa/Poaceae/Eragrostis/eragrostis-cilianensis/"+rel
  to_insert.append({
    "label":p["label"],"scientific_name":"Eragrostis cilianensis","image_url":u,"image_fit":"contain",
    "image_role":p["role"],"caption":p["caption"],"why_it_matters":p["reason"],
    "creator":"Stefan.lefnaer","license":"CC BY-SA 4.0","license_url":LIC,"source_page":source,
    "modifications":"Cleaned EXIF/GPS JPEG with browser-only anatomically grounded arrow overlay",
    "photo_status":"Original pixels visually inspected and actual source measurements not altered. Exact species identification per creator. Source-printed ruler, not a newly inferred scale.",
    "markers":p["markers"]
  })
  records.append({"source":source,"creator":"Stefan.lefnaer","license":"CC BY-SA 4.0","file":str(path),"sha256":hashlib.sha256(clean).hexdigest(),"original_dimensions":p["dims"],"archived_dimensions":list(image.size),"bytes":len(clean),"visible":p["visible"],"arrows":len(p["markers"])})
 gallery=card["visual_comparison"]["items"]
 idx=next((i for i,x in enumerate(gallery) if x.get("scientific_name")!="Eragrostis cilianensis"),len(gallery))
 # Present whole collar/multi-angle before small ligule, but retain original source/photos and comparison lesson.
 gallery[idx:idx]=[to_insert[1],to_insert[0]]
 quick=card["field_photo_quickcheck"]
 quick["steps"]=[
   "START with the source-verified 10-mm montage of actual leaf sheaths and blades: identify the OUTSIDE blade–sheath junction in multiple angles.",
   "OPEN the blade away from its sheathing base: the new source-verified 3-mm macro shows a short whitish fringe of the TRUE LIGULE on its inner side. Do not confuse it with long hairs at the outside sheath mouth or collar.",
   *[s for s in quick.get("steps",[]) if not s.startswith("COLLAR PHOTO:")]
 ]
 quick["warning"]+=" 2026-10-26: two actual Stefan.lefnaer CC BY-SA 4.0 macro photos installed, one showing 10-mm outside sheath montage and one source-printed 3-mm TRUE ligule fringe. Source-labelled Croatian E. cilianensis, not Texas voucher; glandular pits and calibrated length below 1 mm still NOT verified."
 quick["featured_photo_indices"]=list(range(idx+2))
 if isinstance(card.get("field_id_finish_pass"),dict):
  gaps=card["field_id_finish_pass"].get("photo_parts_to_capture",[])
  card["field_id_finish_pass"]["photo_parts_to_capture"]=[g for g in gaps if "Collar/ligule closeup" not in g]
  card["field_id_finish_pass"]["ligule_photo_role_20261026"]="REAL_HAIRY_LIGULE_PIXELS_WITH_PRINTED_3_MM_REFERENCE; TEXAS VOUCHER AND GLANDULAR PIT EVIDENCE STILL REQUIRED"
  card["field_id_finish_pass"]["stage"]="FIELD_READY_PHOTO_GAPS"
 card["curation_status"]["photo_metadata_count"]=len(card["images"])
 card["curation_status"]["photo_files_present"]=sum(str(x.get("file","")).startswith("images/") for x in card["images"])
 card["curation_status"]["lane2_stinkgrass_ligule_20261026"]="TWO ACTUAL MACROS LICENSED AND ARCHIVED; TRUE SOURCE-LABELLED LIGULE REFERENCE PRESENT, GLANDULAR PITS STILL GAP"
 card["photo_note"]=card.get("photo_note","")+"\n2026-10-26 Lane 2: physical CC BY-SA 4.0 local archive for exact E. cilianensis Stefan.lefnaer sl1 stem/sheath 10-mm plate and sl4 real hairy inner ligule 3-mm macro, two anatomically justified arrows; existing canonical media, look-alikes, original NC terms retained."
 if isinstance(card.get("learner_visual_status"),dict):card["learner_visual_status"]["image_count"]=len(card["images"])
 CARD.write_text(json.dumps(card,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 REPORT.parent.mkdir(parents=True,exist_ok=True)
 REPORT.write_text(json.dumps({"species":"Eragrostis cilianensis","date":"2026-10-26","source_licenses_photo_level_verified":True,"anatomy":"measured source-printed macro showing true short inner ligule hair fringe and separate entire outside blade/sheath junction; no glandular pit claims","new_local_JPEGs":len(records),"total_local_JPEGs":card["curation_status"]["photo_files_present"],"new_arrows":sum(x["arrows"] for x in records),"records":records,"status":"FIELD_READY_PHOTO_GAPS","public_site":"not yet verified by live Pages QA"},indent=2)+"\n",encoding="utf-8")
 print("INSTALLED",len(records),"same-species-gallery",idx+2,"local_files",card["curation_status"]["photo_files_present"])
if __name__=="__main__":main()
