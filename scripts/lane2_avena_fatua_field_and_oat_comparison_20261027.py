#!/usr/bin/env python3
"""Lane 2 Avena fatua: two ORIGINAL Texas species photos + exact Commons
Avena barbata and A. sativa comparisons. Verified individual media license,
archive bytes no EXIF, annotate gross visible organs only.
"""
import json,io,hashlib,html
from urllib.request import Request,urlopen
from urllib.parse import urlencode
from pathlib import Path
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"content/taxa/Poaceae/Avena/avena-fatua"
CARD=BASE/"species.json"
REPORT=ROOT/"reports/lane2-avena-fatua-field-and-oat-lookalikes-20261027.json"
UA={"User-Agent":"HaysBotanyVisualLearner/1.0 (educational exact-license source verification, admin contact GitHub Crking92)"}
SRC=[
 {"taxon":"Avena fatua","obs":369569943,"photo":675080156,"license":"cc-by-nc","author":"Shaun Michael",
  "name":"shaun-michael-lee-county-green-flowering-wild-oat-675080156.jpg",
  "label":"TEXAS · live green wild oat flowering plants among grassland growth",
  "role":"Green in-situ meadow whole culms, nodding wild-oat open panicles and living blades, in mixed-grass setting; roots NOT exposed",
  "caption":"Shaun Michael's Research Grade Lee County wild-oat photo shows mature pale nodding oat spikelets on spreading branches supported by living, slender green flowering shoots. The scene includes other grasses—follow the visible attached oats and DO NOT claim every blade in this view belongs to this individual. No roots or opened true ligule are exposed.",
  "why":"Real Central Texas growing habit in a green spring field, paired with diagnostic close-ups elsewhere in this card.",
  "markers":[{"label":"Drooping wild-oat spikelets","label_x":64,"label_y":13,"target_x":53,"target_y":41}]},
 {"taxon":"Avena fatua","obs":367069469,"photo":670312346,"license":"cc-by-nc","author":"Lynn Djahangiri",
  "name":"lynn-djahangiri-rowlett-mature-standing-wild-oat-670312346.jpg",
  "label":"TEXAS · full mature seed-bearing wild-oat plants in place",
  "role":"In-situ mature annual oat colony next to fence, visible pendent spikelets and erect upper culms; rooting mechanism obscured",
  "caption":"Lynn Djahangiri photographed wild-oat plants by a Rowlett fence. The elevated, open, gently drooping panicles bear large narrow pale hanging spikelets. These are attached flowering shoots, not disconnected grains; stalk base and root system remain hidden in dry litter.",
  "why":"An additional clearly different growth stage, showing dry seed-bearing oat panicles recognizable from a distance in landscapes.",
  "markers":[{"label":"Open drooping oat panicle","label_x":6,"label_y":21,"target_x":61,"target_y":32}]}
]
COMMONS=[
 {"taxon":"Avena barbata","filename":"Avena barbata spikelet1 (6804423998) (2).jpg","name":"harry-rose-barbata-compared-spikelet-6804423998.jpg","creator":"Harry Rose",
 "expect_license":"CC BY 2.0", "license":"CC BY 2.0","license_url":"https://creativecommons.org/licenses/by/2.0/",
 "label":"LOOK-ALIKE · slender oat (*Avena barbata*), photographed spikelet and glumes",
 "role":"Genuine introduced Avena barbata spikelet photo, larger botanical structure, species-specified Commons file by Harry Rose; not A. fatua",
 "caption":"SLENDER / BEARDED OAT (Avena barbata), photographed by Harry Rose. Its spikelets carry long glumes and awned florets, broadly resembling wild oat. Compare opened mature florets and especially lemma-tip teeth under a millimeter ruler: A. barbata generally has longer bifid lemma teeth than A. fatua. No identification by simply counting the two long glumes.",
 "why":"Real same-genus look-alike at the matching spikelet scale, to prevent treating all awned Avena florets as wild oat."},
 {"taxon":"Avena sativa","filename":"Avena sativa - Oslo botanical garden - IMG 8898.jpg","name":"daderot-sativa-oat-flowering-original-8898.jpg","creator":"Daderot",
 "expect_license":"Public domain", "license":"Public domain — author Daderot released work", "license_url":"https://creativecommons.org/publicdomain/mark/1.0/",
 "label":"LOOK-ALIKE · cultivated oat (*Avena sativa*), original photographed plant",
 "role":"Real introduced cultivated oat Avena sativa, distinct other species, botanical garden original photograph",
 "caption":"CULTIVATED OAT (Avena sativa), source-labelled from Oslo Botanical Garden by Daderot. Cultivated oats often have more compact heads and reduced, straighter or absent awns on mature florets, whereas wild oat commonly shows strongly bent/twisted awns and a readily shattering floret base. The present overview must not be used to certify single floret hair or shattering scar, which require macro views.",
 "why":"Introduced cultivated species can be confused with wild oat in parks or restoration seed mixes. Their ligules are similar; inspect mature disarticulation and awns."}
]
def read(url,limit=10_000_000):
 with urlopen(Request(url,headers=UA),timeout=60) as h:b=h.read(limit+1)
 if len(b)>limit:raise RuntimeError("Downloaded media exceeds 10MB cap")
 return b
def getjson(url):return json.loads(read(url,9_000_000))
def store(jpeg,name):
 dest=BASE/"images"/name
 if dest.exists():raise RuntimeError("Already present unexpected: "+str(dest))
 with Image.open(io.BytesIO(jpeg)) as im:
  if im.format not in {"JPEG","PNG"}:raise RuntimeError("No valid raster")
  im=ImageOps.exif_transpose(im).convert("RGB")
  if min(im.size)<450:raise RuntimeError("Resolution too low")
  orig_size=list(im.size)
  im.thumbnail((2600,2600))
  buff=io.BytesIO();im.save(buff,"JPEG",quality=89,optimize=True)
 b=buff.getvalue()
 if not b.startswith(b"\xff\xd8") or not b.endswith(b"\xff\xd9"):raise RuntimeError("Corrupt re-encoded JPEG")
 dest.write_bytes(b)
 return {"relative":"content/taxa/Poaceae/Avena/avena-fatua/images/"+name,
    "size_bytes":len(b),"sha256":hashlib.sha256(b).hexdigest(),"original_dimensions":orig_size}
def commonspage(name):
 info=getjson("https://commons.wikimedia.org/w/api.php?"+urlencode(
  {"action":"query","format":"json","prop":"imageinfo","titles":"File:"+name,"iiprop":"url|extmetadata"}))
 page=next(iter(info["query"]["pages"].values()))
 if page.get("missing") is not None:raise RuntimeError("Commons file missing: "+name)
 return page["imageinfo"][0]
def main():
 j=json.loads(CARD.read_text())
 if j["scientific_name"]!="Avena fatua":raise RuntimeError("Wrong species card")
 existing={p["image_url"] for p in j["visual_comparison"]["items"]}
 if any("lynn-djahangiri-rowlett" in x for x in existing):print("ALREADY_INSTALLED");return
 panels=[];metadata=[];report=[]
 for p in SRC:
  data=getjson(f'https://api.inaturalist.org/v1/observations/{p["obs"]}')["results"][0]
  if data["taxon"]["name"]!=p["taxon"] or data.get("quality_grade")!="research":raise RuntimeError("Research-grade taxon changed")
  photo=next((x for x in data["photos"] if x["id"]==p["photo"]),None)
  if not photo or photo.get("license_code")!=p["license"] or p["author"].lower() not in photo.get("attribution","").lower():
   raise RuntimeError(f"License/creator mismatch: {p['photo']}")
  url=photo["url"].replace("/square.","/original.").replace("/medium.","/original.").replace("/large.","/original.")
  b=store(read(url),p["name"])
  source=f'https://www.inaturalist.org/photos/{p["photo"]}'
  props={"creator":p["author"],"license":"CC BY-NC 4.0","license_url":"https://creativecommons.org/licenses/by-nc/4.0/",
   "source_page":source,"public_reuse":"only on verified noncommercial educational site with credit",
   "modifications":"EXIF/GPS removed via clean RGB JPEG conversion; separate browser arrows",
   "source_observation_id":p["obs"],"photo_original_dimensions_px":b["original_dimensions"],"photo_sha256":b["sha256"]}
  metadata.append({"file":"images/"+p["name"],"role":p["role"],**props})
  panels.append({"label":p["label"],"scientific_name":p["taxon"],"image_url":b["relative"],"image_fit":"contain",
   "image_role":p["role"],"caption":p["caption"],"why_it_matters":p["why"],"markers":p["markers"],
   "photo_status":"2026-10-27 original pixels individually source-verified; only real gross seedhead arrows. Root and inner ligule not shown.",**props})
  report.append({"photo_id":p["photo"],"species":p["taxon"],"original_source":source,"license":p["license"],"creator":p["author"],"arrows":len(p["markers"]),**b})
 for p in COMMONS:
  info=commonspage(p["filename"])
  em=info.get("extmetadata",{})
  license_short=html.unescape(em.get("LicenseShortName",{}).get("value",""))
  artist=html.unescape(em.get("Artist",{}).get("value",""))
  if p["expect_license"].lower() not in license_short.lower():raise RuntimeError(f"Commons photo license unexpected {p['filename']}: {license_short}")
  if p["creator"].lower() not in artist.lower():raise RuntimeError(f"Commons photographer unexpected {p['filename']}: {artist[:300]}")
  original_url=info["url"]
  b=store(read(original_url),p["name"])
  source="https://commons.wikimedia.org/wiki/File:"+p["filename"].replace(" ","_")
  props={"creator":p["creator"],"license":p["license"],"license_url":p["license_url"],
    "source_page":source,"source_media_url":original_url,"public_reuse":"yes under exact Commons individual media rights",
    "modifications":"EXIF/GPS stripped, resized within 2600px, visually equivalent photo, no in-photo arrows",
    "photo_original_dimensions_px":b["original_dimensions"],"photo_sha256":b["sha256"]}
  metadata.append({"file":"images/"+p["name"],"role":p["role"],**props})
  panels.append({"label":p["label"],"scientific_name":p["taxon"],"image_url":b["relative"],"image_fit":"contain",
    "image_role":p["role"],"caption":p["caption"],"why_it_matters":p["why"],
    "markers":[],"photo_status":"Original separate-species Commons image; individual media license and photo author verified; source identification only, not voucher.",**props})
  report.append({"species":p["taxon"],"original_source":source,"license":license_short,"creator":p["creator"],"arrows":0,**b})
 arr=j["visual_comparison"]["items"]
 index=next((i for i,a in enumerate(arr) if a.get("scientific_name")!="Avena fatua"),len(arr))
 arr[index:index]=panels
 j["images"]+=metadata
 j["visual_comparison"]["subtitle"]="Six physically stored photographed wild oat views (including two source-verified Texas green and dry growing stands, actual membrane ligule, opened spikelet, twisted awn and callus hair), plus two clearly OTHER-species spikelet/habit comparators: slender oat and cultivated oat. No truly washed intact rooted annual whole plant."
 j["curation_status"]["lane2_avena_field_and_comp_20261027"]={
   "stage":"FIELD_READY_PHOTO_GAPS","added_physical_jpegs":len(report),
   "added_exact_species_jpegs":2,"added_other_species_reference_jpegs":2,
   "new_gross_arrows":2,"gross_live_plant_habit":"photographed",
   "full_attached_flowering_head":"photographed","reproductive_closeups":"existing precise original photos",
   "true_ligule":"existing actual Matt Lavin photographed membrane, no mm scale",
   "rooted_base":"NOT PHOTOGRAPHED","public_pages":"unverified until successful build"
 }
 j["photo_note"]+="\n2026-10-27 Lane 2 archived TWO separately licensed real Texas wild-oat growing-plant photos (Shaun Michael and Lynn Djahangiri, CC BY-NC) and TWO separately source/media-licensed photo comparisons of A. barbata (Harry Rose CC BY) and A. sativa (Daderot Public Domain). Gross arrows only on oat heads. Do not confuse foreign look-alike panels with wild-oat anatomy, or claim roots illustrated."
 REPORT.write_text(json.dumps({"stage":"FIELD_READY_PHOTO_GAPS","date":"2026-10-27",
   "photos":report,"new_local_jpegs":len(report),"new_exact_species_photo_count":2,"new_other_species_photo_count":2,"new_arrows":2,
   "new_photo_roles":["whole field growing habit","complete attached flowering panicles","look-alike compared oat floral shapes"],
   "still_missing":["washed intact rooted annual wild-oat crown and tiller mechanism"],"public_pages_status":"not verified"},indent=2)+"\n")
 CARD.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n")
 print("ARCHIVED",json.dumps(report))
if __name__=="__main__":main()
