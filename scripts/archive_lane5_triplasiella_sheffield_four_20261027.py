#!/usr/bin/env python3
"""Lane 5 Triplasiella SECOND archival pass:
- two individual CC0 Sheffield source images: in-soil basal tuft, a close
  unassigned green floral bract, fresh spikelets on flowering branch
- one individual Eric Knight CC BY real true culm node + exterior sheath.
Do not call tissue a proven inner 1–3mm ligule; don't claim scale/3 veins.
"""
import csv,hashlib,io,json,pathlib,re,time,urllib.request,urllib.error
from PIL import Image,ImageOps
BASE=pathlib.Path("content/taxa/Poaceae/Triplasiella/triplasiella-eragrostoides")
CARD=BASE/"species.json";LEDGER=BASE/"image-sources.csv"
REPORT=pathlib.Path("reports/lane5-triplasiella-sheffield-fine-anatomy-four-20261027.json")
NAME="Triplasiella eragrostoides"
TARGETS=[
 {"obs":321843312,"id":582111406,"license":"cc0",
  "role":"Live slender target shoot with basal leafy cluster emerging in dry Sheffield Texas mixed grass soil; visible lower stems and surrounding debris, roots concealed.",
  "label":"TEXAS BASAL HABIT — living skinny shoots among dry grasses (roots hidden)",
  "caption":"From a real species-determined Sheffield, Texas specimen, slender upright flowering shoots emerge through dry grassy vegetation. Observe the approximate lower shoot/bunch context; other grasses are intermixed and the underground rootstock is NOT extracted, so rhizome presence, crown anatomy or perenniality cannot be certified.",
  "why":"Makes basal habit visible in a dry-season Texas setting, without presenting adjacent weeds or hidden roots as anatomical proof.",
  "tiles":[4,0]},
 {"obs":322073807,"id":582570787,"license":"cc0",
  "role":"Very close image of pale green narrow flowering bract held against a finger; faint linear tissue, but cannot determine whether glume or lemma, identify three dorsal veins, or infer tip mucro.",
  "label":"SINGLE GREEN FLORAL BRACT — close specimen, identity and nerves unresolved",
  "caption":"A tiny pale-green flowering bract from a source-verified plant is held against a finger. This is genuine macro photographic evidence of one grass flower scale, NOT enough to say it is the lemma rather than a glume or palea. Fingerprints give approximate context only: three lemma veins, free tip, central mucro and 2–3 mm measurement are still awaiting calibrated dissection.",
  "why":"Shows one real small floral scale for microscopic teaching, unlike earlier distant seedheads, while keeping organ identity explicitly provisional.",
  "tiles":[2,5]},
 {"obs":322073807,"id":582570805,"license":"cc0",
  "role":"Fresh close-up of short densely clustered pale-green spikelets attached on a small portion of exact target panicle; paired glume/individual fertile lemmas not separated.",
  "label":"PALE GREEN ATTACHED SPIKELETS — fresh source-confirmed flower unit details",
  "caption":"Several fresh pale green compressed target spikelets remain attached along a thin flowering branch, photographed beside fingers in Sheffield. A spikelet is a whole unit of small florets—not a single lemma or glume. Their green edges and overlap are visible, but precise 2–3 mm mature lemma length, three-vein count and central mucro require another close dissection.",
  "why":"Shows developmental contrast with the prior burgundy mature seedhead; individual spikelet outlines are easier to follow.",
  "tiles":[0,2,5]},
 {"obs":325327423,"id":589004519,"license":"cc-by",
  "role":"Real visible grass culm node and leaf blade from a connected source-identified stem, with green outer sheath and junction; inner free membranous 1–3mm ligule not displayed face-on.",
  "label":"TRUE CULM JOINT + LEAF SHEATH — different from inside ligule",
  "caption":"Eric Knight's Texas Triplasiella image shows a green blade just below a pale culm node and the adjoining exterior wrapping sheath. The little stem node band is NOT the true inner ligule; this photo still does not expose or measure the free 1–3 mm membranous margin, and no auricle/rhizome is demonstrated.",
  "why":"A clearer same-taxon demonstration of node versus external leaf sheath prepares crew members to find, rather than invent, the inner ligule.",
  "tiles":[3,4]}
]
rep={"taxon":NAME,"date":"2026-10-27","added":[],"holds":[],"new_arrows":0,
 "photo_boundary":"Floral bract visible but organ identity, vein count, 2–3mm lemma and midnerve mucro not independently certified",
 "remaining":["Extracted connected perennial roots/rootstock","Opened face-on true 1–3mm inner free ligule with physical ruler","Isolated mature 3-veined lemma and a single short central mucro at 1mm scale"]}
def get(url):
 for a in range(4):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotanyVerifiedCC0TrueMorphology/1.0 (educational plant guide)"})
   with urllib.request.urlopen(req,timeout=48) as f:b=f.read(16000000)
   if len(b)>15700000:raise ValueError("Over image size cap")
   return b
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or a==3:raise
   time.sleep(2*(a+1))
d=json.loads(CARD.read_text());assert d["id"]=="triplasiella-eragrostoides"
obs={};new=[]
for spec in TARGETS:
 oid=spec["obs"];pid=spec["id"];record={"observation":oid,"photo":pid}
 try:
  if oid not in obs:
   response=json.loads(get(f"https://api.inaturalist.org/v1/observations/{oid}"))
   obs[oid]=next(iter(response.get("results",[])),None)
  ob=obs[oid]
  if not ob or (ob.get("taxon") or {}).get("name")!=NAME or ob.get("quality_grade")!="research":
   raise ValueError("Target species/research-grade not confirmed on current observation")
  region=ob.get("place_guess") or ""
  if not re.search(r"(Sheffield|Texas|TX\b)",region,re.I):raise ValueError("Not confirmed Texas provenance")
  p=next((p for p in ob.get("photos",[]) if p.get("id")==pid),None)
  if not p or (p.get("license_code") or "").lower().replace("_","-")!=spec["license"]:
   raise ValueError("No exact photo or individual image license mismatch")
  creator=p.get("attribution") or ""
  if spec["license"]=="cc-by" and "Eric Knight" not in creator:
   raise ValueError("Expected named author missing")
  if spec["license"]=="cc0" and "rights reserved" in creator.lower() and not creator.lower().startswith("no rights reserved"):
   raise ValueError("CC0 photographer line contradictory")
  original_url=re.sub(r"/(?:square|small|medium|thumb|large)\.(jpe?g|png)",r"/original.\1",p.get("url") or "")
  if "/original." not in original_url or not original_url.startswith("https://"):raise ValueError("Unexpected image CDN URL")
  source=f"https://www.inaturalist.org/photos/{pid}"
  rel=f"images/tx-triplasiella-detail-{pid}.jpg"
  if any(i.get("file")==rel or i.get("source_page")==source for i in d["images"]):
   raise ValueError("Previously archived")
  raw=get(original_url)
  with Image.open(io.BytesIO(raw)) as im:im.verify()
  with Image.open(io.BytesIO(raw)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   if min(im.size)<650:raise ValueError("Source too low resolution")
   im.thumbnail((2000,2000));dim=list(im.size)
   buff=io.BytesIO();im.save(buff,"JPEG",quality=91,optimize=True);bytes_=buff.getvalue()
  dest=BASE/rel;dest.parent.mkdir(exist_ok=True);dest.write_bytes(bytes_)
  with Image.open(dest) as im:im.verify()
  sha=hashlib.sha256(bytes_).hexdigest()
  licence="CC0 1.0" if spec["license"]=="cc0" else "CC BY 4.0"
  licence_url="https://creativecommons.org/publicdomain/zero/1.0/" if spec["license"]=="cc0" else "https://creativecommons.org/licenses/by/4.0/"
  credit=creator if spec["license"]=="cc-by" else "iNaturalist CC0 individual image (creator not independently identified)"
  d["images"].append({"file":rel,"role":spec["role"],"creator":credit,"license":licence,
      "license_code_exact":spec["license"],"license_url":licence_url,
      "source_page":source,"observation_url":f"https://www.inaturalist.org/observations/{oid}",
      "observation_id":str(oid),"photo_id":str(pid),"source_region":region,
      "source_taxon":NAME,"source_quality_grade":"research as source checked",
      "modifications":"RGB JPEG re-encoded, metadata/EXIF/GPS stripped, zero arrows",
      "sha256":sha,"pixels":dim,"public_reuse":"Individual CC0 or CC BY open license and exact species source checked",
      "photo_status":"Actual source pixels verified at preview and JPEG decode. Macro fine organ identification not independently measured."})
  idx=len(d["visual_comparison"]["items"])
  d["visual_comparison"]["items"].append({"label":spec["label"],"scientific_name":NAME,
     "image_url":str(dest),"image_fit":"contain","image_role":spec["role"],
     "caption":spec["caption"],"why_it_matters":spec["why"],
     "creator":credit,"license":licence,"license_url":licence_url,
     "source_page":source,"markers":[],"photo_status":"Exact species, original pixels and individual reuse rights checked. No free ligule or glume/lemma vein count certified."})
  for ti in spec["tiles"]:
   if idx not in d["field_id_short_tiles"][ti]["photo_panel_indices"]:
    d["field_id_short_tiles"][ti]["photo_panel_indices"].append(idx)
  record.update({"status":"archived","file":str(dest),"sha256":sha,"image_dimensions":dim,"gallery_index":idx,"license":licence})
  new.append((dest.name,spec["role"],credit,licence,licence_url,source,original_url,str(oid),str(pid)))
 except Exception as e:record.update({"status":"HELD","reason":str(e)})
 rep["added" if record["status"]=="archived" else "holds"].append(record)
if rep["added"]:
 d["curation_status"]["photo_metadata_count"]=len(d["images"])
 d["curation_status"]["photo_files_present"]=len(d["images"])
 d["curation_status"]["visual_finish"]="FIELD_READY_PHOTO_GAPS — 10 real species photos incl. central TX green/dark heads, outer leaf junction, true stem node, CC0 field base/individual floral bract/fresh spikelet. Real roots, 1–3mm calibrated inner ligule and dissected 3-veined central-mucronate lemma still missing."
 d["learner_visual_status"]["image_count"]=len(d["images"])
 d["lane5_triplasiella_cc0_details_20261027"]={"photos":rep["added"],"status":"FIELD_READY_PHOTO_GAPS",
    "unproven":["Rooted perennial crown","Actual measured true inner ligule","Anatomically identified glume vs lemma, 3 veins + mucro"],"arrows_added":0}
 CARD.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
 if LEDGER.exists():
  with LEDGER.open(newline="") as f:reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
  existing={r["file_name"] for r in rows}
  for filename,role,creator,lic,licurl,source,orig,oid,pid in new:
   if filename in existing:continue
   row=dict.fromkeys(fields,"")
   for k,v in {"file_name":filename,"role":role,"creator":creator,"license":lic,
     "license_url":licurl,"source_page":source,"direct_url":orig,"observation_id":oid,
     "photo_id":pid,"study_use":"educational diagnostic botanical guide with source attribution",
     "public_reuse":"yes, source verified CC0/CC BY license",
     "modifications":"Original JPEG re-encoded RGB, EXIF/GPS removed, no arrows"}.items():
    if k in row:row[k]=v
   rows.append(row)
  with LEDGER.open("w",newline="") as f:wr=csv.DictWriter(f,fieldnames=fields);wr.writeheader();wr.writerows(rows)
REPORT.parent.mkdir(exist_ok=True);REPORT.write_text(json.dumps(rep,indent=2)+"\n")
print(json.dumps(rep))
