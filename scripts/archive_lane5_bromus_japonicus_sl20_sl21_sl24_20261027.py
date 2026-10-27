#!/usr/bin/env python3
"""Archive three exact-source CC BY-SA 4.0 Japanese brome anatomical photographs.
Replace existing TWO externally hotlinked teaching images in situ (indices
8,9), append a true glumes-at-spikelet-base photo. Do not claim microscopic
vein count or free ligule unless certified in actual source pixels.
Canonical originals and other species photos untouched.
"""
from pathlib import Path
import csv,hashlib,html,io,json,re,time,urllib.parse,urllib.request,urllib.error
from PIL import Image,ImageOps
ROOT=Path("content/taxa/Poaceae/Bromus/bromus-japonicus")
CARD=ROOT/"species.json";LEDGER=ROOT/"image-sources.csv"
OUT=Path("reports/lane5-bromus-japonicus-three-scaled-anatomy-20261027.json")
SPECS=[
  {"name":"Bromus japonicus sl20.jpg","panel":8,
   "dest":"stefan-lefnaer-bromus-japonicus-true-hairy-stem-nodes-sl20.jpg",
   "role":"Actual FOUR true culm nodes and softly hairy grass sheaths on same photographed Japanese brome stem, source has 5-mm printed scale; 1–2 mm inner free ligule and fibrous roots NOT visible.",
   "label":"REAL CULM NODES — reddish joints and hairy external sheaths with source scale",
   "caption":"Stefan.lefnaer's four source-identified Japanese brome stem views show dark/purple true culm nodes, adjacent green internodes and many long fine external sheath hairs. The photographer's 5-mm bar offers a genuine reference; do not confuse a culm NODE with the INTERNAL free ligule at a blade–sheath seam. This original Austrian stem is not a Texas voucher, and roots are out of frame.",
   "tiles":[1,5]},
  {"name":"Bromus japonicus sl21.jpg","panel":9,
   "dest":"stefan-lefnaer-bromus-japonicus-true-hairy-leaf-sheath-sl21.jpg",
   "role":"Three same-taxon original photographic views of real blade/sheath overlap with fine soft sheath hairs and true external collar search location; opened inner 1–2 mm membranous ligule free margin not confirmed.",
   "label":"TRUE HAIRY LEAF SHEATH — actual blade–sheath overlap (inner ligule hidden)",
   "caption":"Real Japanese brome vegetative anatomy from the Austrian source-labelled specimen: green leaf blade and hairy external sheath are photographed with a printed 5-mm scale. The inner free membrane itself has not been pulled open face-on; the long outer hairs should NOT be labeled as a diagnostic ligule. Distinguish a leaf-sheath junction from a true culm node.",
   "tiles":[1,5]},
  {"name":"Bromus japonicus sl24.jpg","panel":None,
   "dest":"stefan-lefnaer-bromus-japonicus-real-glumes-at-spikelet-base-sl24.jpg",
   "role":"Actual detached/isolated Japanese brome spikelet bases with both outer glumes visible in multiple source-panel views; 1-mm anatomical vein counting and lower-vs-upper glume designation are not yet independently certified.",
   "label":"ACTUAL SPIKELET BASE + PAIR OF GLUMES — true reproductive macro",
   "caption":"Stefan.lefnaer photographed actual Japanese brome spikelet bases and their outer glumes from a source-identified Austrian plant. The thin outer bracts are GLUMES, not the overlapping many-floret lemmas. This closes the previous 'no glume image' gap, but counting the (3)5 versus 7 dorsal glume veins from these combined original views still requires pixel/microscope verification and should not be illustrated by invented vein arrows.",
   "tiles":[2,4,5]}
]
R={"date":"2026-10-27","species":"Bromus japonicus","archived":[],"held":[],"anatomy_arrows_added":0,
   "scientific_holds":["TRUE free 1–2 mm membranous ligule opened beside real 1mm ruler","Exposed connected annual fibrous roots and same-plant panicle","Count lower versus upper glume nerves confidently under backlight and 1mm reference","Matched Texas brome dissection for 1/3-veined glumes"],
   "no_individual_glume_vein_arrows":True}
def get(url):
 for i in range(4):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotanyVerifiedSourceJapaneseBromePhotos/1.0 (educational CC BY-SA reuse)","Accept":"image/jpeg,application/json,*/*"})
   with urllib.request.urlopen(req,timeout=50) as f:b=f.read(16500000)
   if len(b)>16000000:raise ValueError("Source >16MB")
   return b
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or i==3:raise
   time.sleep(2*(i+1))
def validate_commons(name):
 param={"action":"query","format":"json","prop":"imageinfo|categories","iiprop":"url|extmetadata","cllimit":"max","iiurlwidth":"3600","titles":"File:"+name}
 page=next(iter(json.loads(get("https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(param)))["query"]["pages"].values()))
 info=page["imageinfo"][0];md=info["extmetadata"]
 lic=re.sub("[^A-Z0-9]","",md.get("LicenseShortName",{}).get("value","").upper())
 author=html.unescape(re.sub("<[^>]+>"," ",md.get("Artist",{}).get("value",""))).strip()
 cats={c["title"] for c in page.get("categories",[])}
 if lic!="CCBYSA40" or "Stefan.lefnaer" not in author or "Category:Bromus japonicus" not in cats:
  raise ValueError("Commons exact photo taxon, author, CC BY-SA 4.0 gate failed: "+str((lic,author,sorted(cats)[:5])))
 return info
d=json.loads(CARD.read_text())
if d.get("id")!="bromus-japonicus":raise SystemExit("Unexpected species; stopped")
for p in SPECS:
 row={"source":p["name"],"panel_expected":p["panel"]}
 try:
  info=validate_commons(p["name"])
  src="https://commons.wikimedia.org/wiki/File:"+p["name"].replace(" ","_")
  rel="images/"+p["dest"];path=ROOT/rel
  if any(x.get("file")==rel or urllib.parse.unquote(x.get("source_page",""))==src for x in d["images"]):
   raise ValueError("Already installed, refuse duplicates")
  blob=get(info.get("thumburl") or info["url"])
  with Image.open(io.BytesIO(blob)) as im:im.verify()
  with Image.open(io.BytesIO(blob)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   if min(im.size)<900:raise ValueError("Anatomical rendition too small")
   size=list(im.size);buffer=io.BytesIO();im.save(buffer,"JPEG",quality=89,optimize=True,progressive=True,subsampling=0);clean=buffer.getvalue()
  path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(clean)
  with Image.open(path) as im: im.verify()
  sha=hashlib.sha256(clean).hexdigest()
  d["images"].append({"file":rel,"role":p["role"],"creator":"Stefan.lefnaer",
   "license":"CC BY-SA 4.0","license_url":"https://creativecommons.org/licenses/by-sa/4.0/",
   "source_page":src,"source_original_url":info["url"],"source_taxon":"Bromus japonicus, author's 2018 Rosenberg Grafensulz Austrian specimen",
   "source_region":"Lower Austria, photographed 2018-06-08; NOT Hays County",
   "modifications":"Wikimedia 3600px JPEG imageinfo source converted to metadata-free RGB JPEG; no new arrows burned in or added",
   "image_dimensions":size,"sha256":sha,"public_reuse":"Individually Commons-verified CC BY-SA 4.0, creator and source; adaptation/reencoding declared",
   "photo_status":"Actual source-labelled photographic anatomy, separate published technical dimensions NOT falsely arrowed"})
  if p["panel"] is not None:
   n=p["panel"]
   panel=d["visual_comparison"]["items"][n]
   if panel.get("scientific_name")!="Bromus japonicus" or not urllib.parse.unquote(panel.get("source_page","")).endswith(p["name"].replace(" ","_")):
    raise ValueError("Existing panel identity shifted; source check failed")
   panel["image_url"]=str(path)
   panel["label"]=p["label"];panel["image_role"]=p["role"];panel["caption"]=p["caption"]
   panel["photo_status"]="REAL LOCAL IMAGE, SOURCE CC BY-SA 4.0, bytes/pixels and original taxon checked 2026-10-27. Existing panel index retained; no fine-anatomy arrows."
   panel["modifications"]="Metadata-free RGB JPEG rendition; source photographer Stefan.lefnaer, CC BY-SA 4.0 retained, original reencoded"
  else:
   n=len(d["visual_comparison"]["items"])
   d["visual_comparison"]["items"].append({"label":p["label"],"scientific_name":"Bromus japonicus",
    "image_url":str(path),"image_fit":"contain","image_role":p["role"],
    "caption":p["caption"],
    "why_it_matters":"First physically archived exact-species photo of the two actual glumes at a Japanese brome spikelet base; avoids using separate lemma photo as glume proof.",
    "creator":"Stefan.lefnaer","license":"CC BY-SA 4.0",
    "license_url":"https://creativecommons.org/licenses/by-sa/4.0/","source_page":src,
    "markers":[],"photo_status":"Source-identification and image rights verified; individual nervation not asserted; no arrows until pixel-level count."})
  for tileid in p["tiles"]:
   inds=d["field_id_short_tiles"][tileid]["photo_panel_indices"]
   if n not in inds:inds.append(n)
  row.update({"status":"archived","file":str(path),"pixels":size,"bytes":len(clean),"sha256":sha,"panel":n,
              "copyright":"CC BY-SA 4.0","original_file_page":src})
 except Exception as e:row.update({"status":"HELD","reason":str(e)})
 R["archived" if row["status"]=="archived" else "held"].append(row)
if R["archived"]:
 d["curation_status"]["photo_metadata_count"]=len(d["images"])
 d["curation_status"]["photo_files_present"]=len(d["images"])
 d["curation_status"]["visual_finish"]="FIELD_READY_PHOTO_GAPS — 3 genuine previously archived same-species reproductive photos plus new two local real 5-mm-scaled hairy sheath/node anatomy photos and first actual glumes-at-spikelet-base picture. Rooted crown, opened measured ligule and individually counted glume veins still missing."
 d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
 d["learner_visual_status"]["note"]="Local licensed actual Japanese brome vegetative/stem nodes and actual glume base now stored (Stefan.lefnaer CC BY-SA 4.0). One old CC BY-NC iNat image remains in archive but not teaching gallery; count does not mean publicly illustrated. 5 actual local own-species photo panels plus external lookalikes; true open free ligule, extracted crown, independently backlit glume nerve count and local Texas same-voucher photos still missing."
 d["lane5_bromus_japonicus_scalebar_20261027"]={"added":R["archived"],"stage":"FIELD_READY_PHOTO_GAPS",
   "roles_added":"Actual hairy leaf sheath and dark node macro at 5mm scale and unmeasured real paired glume base",
   "still_missing":R["scientific_holds"],"new_unverified_arrows":0}
 CARD.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
 with LEDGER.open(newline="") as f:reader=csv.DictReader(f);cols=reader.fieldnames;rows=list(reader)
 existing={r["file_name"] for r in rows}
 # Refresh ALL image credits in incomplete ledger, not only new images.
 for p in d["images"]:
  name=Path(p["file"]).name
  if name in existing:continue
  row=dict.fromkeys(cols,"")
  fields={"file_name":name,"role":p.get("role") or "",
   "creator":p.get("creator") or "UNKNOWN","license":p.get("license") or "UNKNOWN — DO NOT PUBLISH",
   "source_page":p.get("source_page") or "","direct_url":p.get("source_original_url") or "",
   "study_use":p.get("study_use") or "properly credited botanical educational learner",
   "public_reuse":p.get("public_reuse") or "check file-level reuse license",
   "observation_id":p.get("observation_id") or "","photo_id":p.get("photo_id") or ""}
  for k,v in fields.items():
   if k in row:row[k]=v
  rows.append(row);existing.add(name)
 with LEDGER.open("w",newline="") as f:wr=csv.DictWriter(f,fieldnames=cols);wr.writeheader();wr.writerows(rows)
 R["ledger_count"]=len(rows)
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(R,indent=2)+"\n")
print(json.dumps(R))
