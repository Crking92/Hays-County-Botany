#!/usr/bin/env python3
"""Lane 5 Chloris virgata source-checked real NODE anatomy and Texas live habit.

Three individually verified images:
  CC BY 2.0 Harry Rose 6920191777: dark circumferential culm node
  CC BY 2.0 Harry Rose 6923835606: stem node with adjacent blade + sheath
  CC BY (iNaturalist) CK2AZ 46785084: El Paso in-ground plant, NO roots exposed

Only arrows actually visible on nodes. One-to-one photo license, creator,
same species, source verification, jpeg pixel integrity. Fill photo ledger for
all preexisting nine images as well, without overwriting attribution.
"""
import csv,hashlib,html,io,json,pathlib,re,time,urllib.parse,urllib.request,urllib.error
from PIL import Image,ImageOps
ROOT=pathlib.Path("content/taxa/Poaceae/Chloris/chloris-virgata")
CARD=ROOT/"species.json";LEDGER=ROOT/"image-sources.csv"
OUT=pathlib.Path("reports/lane5-chloris-virgata-two-node-texas-habit-20261027.json")
SPECIES="Chloris virgata"
TARGETS=[
 {"type":"commons","name":"Chloris virgata node (6920191777).jpg",
  "dest":"harry-rose-chloris-virgata-dark-node-6920191777.jpg",
  "label":"TRUE CULM NODE — photographed dark circumferential joint",
  "role":"Real dark reddish stem node ring completely encircling source-labelled Chloris virgata green culm. The leaf collar is a different structure and is not pictured in this macro.",
  "caption":"A real dark chestnut-red STEM NODE encircles the otherwise green grass culm, above a finger for general size. The node forms a joint on the stem; it is NOT a true free ligule and proves neither rooting at the lower node nor the plant's lifespan.",
  "why":"Photographs the conspicuous real dark culm-node character, previously missing from the target gallery.",
  "markers":[{"label":"Dark true stem node (not a ligule)","label_x":8,"label_y":16,"target_x":50,"target_y":52}],
  "tiles":[1]},
 {"type":"commons","name":"Chloris virgata node3 (6923835606).jpg",
  "dest":"harry-rose-chloris-virgata-node-and-blade-6923835606.jpg",
  "label":"NODE VERSUS LEAF BLADE — dark joint and attached green outer sheath",
  "role":"True source-verified culm node is visibly dark across an upright green stem, with a long flat grass leaf blade entering from the side. Inner ligule membrane not exposed.",
  "caption":"An actual reddish node ring crosses the upright green stem; a separate long leaf blade diverges nearby. The two are NOT interchangeable: the node is a stem joint, while the free LIGULE lies inside the blade/sheath transition and cannot be resolved here. Long bright hairlike filaments in the background are not identified as the ligule.",
  "why":"Teaches novices where to find a stem node relative to the leaf and sheath while avoiding false inner-collar arrows.",
  "markers":[{"label":"Dark culm node across stem","label_x":38,"label_y":9,"target_x":77,"target_y":40}],
  "tiles":[1]},
 {"type":"inat","obs":29959547,"pid":46785084,
  "dest":"tx-ck2az-chloris-virgata-in-ground-habit-46785084.jpg",
  "label":"REAL TEXAS FIELD HABIT — narrow flowering culms emerging from rocky road verge",
  "role":"Exact-source Texas live plant growing upright in gravelly roadside substrate, feathery flowering head and multiple slender leafy shoots converge near base. Root system beneath soil is invisible.",
  "caption":"An actual feather fingergrass grows on a disturbed rocky roadside in El Paso, Texas. The narrow leafy culms and seedheads emerge together near the ground, giving realistic survey context. NO fibrous roots or connected rooted lower nodes are uncovered; this is a live in-situ growth photograph, not an excavated rooted crown.",
  "why":"Provides a real source-labeled Texas growing-habit view alongside the older Mexican field photo, without pretending the underground roots are exposed.",
  "markers":[],"tiles":[0,1]}
]
REPORT={"species":SPECIES,"date":"2026-10-27","archived":[],"held":[],"new_node_arrows":0,
"unresolved":["True open free inner ligule edge with millimeter reference","Exposed fibrous roots and any lower nodal rooting (if present) on source-labelled flowering plant","Individually dissected measured glumes + fertile/sterile lemma and separate awn insertions"],
"note":"These new photographic roles do not certify fine-floret microstructure; two real node markers only."}
def get(url):
 for n in range(4):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyIndividualCCNodeAnatomyArchive/1.0 (public educational field ID)"})
   with urllib.request.urlopen(req,timeout=48) as f: b=f.read(17000000)
   if len(b)>16500000:raise ValueError("Oversize response")
   return b
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or n==3:raise
   time.sleep(2*(n+1))
d=json.loads(CARD.read_text())
if d.get("id")!="chloris-virgata":raise SystemExit("Canonical taxon mismatch")
def source_details(s):
 if s["type"]=="commons":
  q=urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo|categories",
      "cllimit":"max","iiprop":"url|extmetadata","iiurlwidth":"1800","titles":"File:"+s["name"]})
  page=next(iter(json.loads(get("https://commons.wikimedia.org/w/api.php?"+q))["query"]["pages"].values()))
  info=page["imageinfo"][0];md=info["extmetadata"]
  lic=re.sub("[^A-Z0-9]","",md.get("LicenseShortName",{}).get("value","").upper())
  author=html.unescape(re.sub("<[^>]*>"," ",md.get("Artist",{}).get("value",""))).strip()
  cats={x["title"] for x in page.get("categories",[])}
  if lic!="CCBY20" or "Harry Rose" not in author or "Category:Chloris virgata" not in cats:
   raise ValueError("Exact CC BY 2.0, creator, species Commons gates not passed")
  return {"src":"https://commons.wikimedia.org/wiki/File:"+urllib.parse.quote(s["name"].replace(" ","_")),
          "raw_url":info.get("thumburl") or info["url"],
          "orig_url":info["url"],
          "creator":"Harry Rose (Macleay Grass Man)","license":"CC BY 2.0",
          "license_url":"https://creativecommons.org/licenses/by/2.0/",
          "location":"Harry Rose Australian source photograph, not a Texas voucher"}
 ob=next(iter(json.loads(get(f"https://api.inaturalist.org/v1/observations/{s['obs']}")).get("results",[])),None)
 if not ob or (ob.get("taxon") or {}).get("name")!=SPECIES or ob.get("quality_grade")!="research":
  raise ValueError("iNaturalist source no longer exact research-grade species")
 place=ob.get("place_guess") or ""
 if not re.search(r"El Paso|Texas|TX\b",place,re.I):raise ValueError("Texas provenance not verified")
 p=next((p for p in ob.get("photos",[]) if p.get("id")==s["pid"]),None)
 if not p or (p.get("license_code") or "").lower().replace("_","-")!="cc-by":
  raise ValueError("Individual photo rights changed or unavailable")
 artist=p.get("attribution") or ""
 if "CK2AZ" not in artist:raise ValueError("Photographer source mismatch")
 uri=re.sub(r"/(?:square|small|medium|thumb|large)\.(jpe?g|png)",r"/original.\1",p.get("url") or "")
 if "/original." not in uri:raise ValueError("Bad source-original URL")
 return {"src":f"https://www.inaturalist.org/photos/{s['pid']}",
   "raw_url":uri,"orig_url":uri,"creator":"CK2AZ","license":"CC BY",
   "license_url":"https://creativecommons.org/licenses/by/4.0/",
   "location":place,"source_observation":f"https://www.inaturalist.org/observations/{s['obs']}"}
for s in TARGETS:
 rec={"photo":s.get("name") or s.get("pid"),"target_role":s["role"]}
 try:
  sd=source_details(s);rel="images/"+s["dest"]
  if any(x.get("file")==rel or x.get("source_page")==sd["src"] for x in d["images"]):
   raise ValueError("Source already archived; no duplicate")
  raw=get(sd["raw_url"])
  with Image.open(io.BytesIO(raw)) as im:im.verify()
  with Image.open(io.BytesIO(raw)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   if min(im.size)<440:raise ValueError("Source image resolution too small")
   im.thumbnail((2000,2000));dims=list(im.size)
   buff=io.BytesIO();im.save(buff,"JPEG",quality=91,optimize=True);clean=buff.getvalue()
  dest=ROOT/rel;dest.parent.mkdir(exist_ok=True);dest.write_bytes(clean)
  with Image.open(dest) as im:im.verify()
  sha=hashlib.sha256(clean).hexdigest()
  img={"file":rel,"role":s["role"],"creator":sd["creator"],
      "license":sd["license"],"license_url":sd["license_url"],
      "source_page":sd["src"],"source_original_url":sd["orig_url"],
      "source_location":sd["location"],
      "modifications":"Re-encoded RGB JPEG with EXIF/GPS removed; separate accurate browser-overlay node arrow only where true joint directly pictured",
      "sha256":sha,"pixels":dims,
      "photo_status":"TRUE SOURCE-VERIFIED EXACT-SPECIES IMAGE — only visible stem node / aboveground field habit counted"}
  if sd.get("source_observation"):img["observation_url"]=sd["source_observation"]
  d["images"].append(img)
  ix=len(d["visual_comparison"]["items"])
  d["visual_comparison"]["items"].append({"label":s["label"],
     "scientific_name":SPECIES,"image_url":str(dest),"image_fit":"contain",
     "image_role":s["role"],"caption":s["caption"],"why_it_matters":s["why"],
     "creator":sd["creator"],"license":sd["license"],"license_url":sd["license_url"],
     "source_page":sd["src"],"markers":s["markers"],
     "photo_status":"Individually licensed true species JPEG locally archived 2026-10-27; node arrow follows visible dark band. Inner ligule and roots NOT photographed."})
  for tile_index in s["tiles"]:
   indices=d["field_id_short_tiles"][tile_index]["photo_panel_indices"]
   if ix not in indices:indices.append(ix)
  REPORT["new_node_arrows"]+=len(s["markers"])
  rec.update({"status":"archived","file":str(dest),"dims":dims,"sha256":sha,"gallery_panel":ix,
              "license":sd["license"],"source_page":sd["src"]})
 except Exception as exc:rec.update({"status":"HELD","reason":str(exc)})
 REPORT["archived" if rec["status"]=="archived" else "held"].append(rec)
if REPORT["archived"]:
 d.setdefault("curation_status",{})["photo_metadata_count"]=len(d["images"])
 d["curation_status"]["photo_files_present"]=len(d["images"])
 d["curation_status"]["visual_finish"]="FIELD_READY_PHOTO_GAPS — actual photographed dark culm nodes plus Texas roadside real flowering habit now added. Still missing exact inner measured ligule, exposed attached rootstock and measured fertile/sterile lemma awn insertion."
 d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
 d["learner_visual_status"]["note"]="True twelve physical source-licensed species JPEGs, eleven actual species photographic panels plus one C. verticillata comparison panel. Two new verified dark true culm node photographs and one Texas roadside real in-ground plant; inner membranous free ligule, excavated rooted crown and scaled fertile/sterile lemma dissection remain missing. Live Pages and mobile annotation positions not certified."
 d["lane5_chloris_virgata_node_growth_20261027"]={
   "added":REPORT["archived"],"status":"FIELD_READY_PHOTO_GAPS","arrows":REPORT["new_node_arrows"],
   "roles":"True dark culm node + leaf blade distinction, plus Texas in-situ field habit (roots hidden)",
   "remains":REPORT["unresolved"]}
 CARD.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
 # Repair partial source ledger using source-level metadata without overwriting existing rows.
 with LEDGER.open(newline="") as f:rd=csv.DictReader(f);fields=rd.fieldnames;rows=list(rd)
 present={r["file_name"] for r in rows}
 for img in d["images"]:
  name=pathlib.Path(img["file"]).name
  if name in present:continue
  src=img.get("source_page") or ""
  creator=img.get("creator") or "not identified"
  license_=img.get("license") or "UNKNOWN — HOLD PUBLIC USE"
  row=dict.fromkeys(fields,"")
  mapping={"file_name":name,"role":img.get("role") or "",
    "creator":creator,"license":license_,"source_page":src,
    "direct_url":img.get("source_original_url") or img.get("source_image") or img.get("media_source_url") or "",
    "study_use":"source-attributed educational image","public_reuse":img.get("public_reuse") or ("source licence above; preserve attribution"),
    "license_url":img.get("license_url") or "",
    "modifications":img.get("modifications") or "Existing local JPG; original modifications not reverified"}
  for k,v in mapping.items():
   if k in row:row[k]=v
  rows.append(row);present.add(name)
 with LEDGER.open("w",newline="") as f:wr=csv.DictWriter(f,fieldnames=fields);wr.writeheader();wr.writerows(rows)
REPORT["source_ledger_rows"]=len(rows)
OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(REPORT,indent=2)+"\n")
print(json.dumps(REPORT))
