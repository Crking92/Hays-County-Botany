#!/usr/bin/env python3
"""Lane 5 hooded windmillgrass: archive THREE genuine Texas source-licensed
field diagnostic photos, no fantasy microscopic ligule/sterile hood arrows.
Original iNaturalist photo-specific CC BY, exact taxon, research grade, geographic
source, creator and JPEG byte checks. Appends panels preserving all old indices.
"""
import csv,hashlib,io,json,pathlib,re,time,urllib.request,urllib.error
from PIL import Image,ImageOps
BASE=pathlib.Path("content/taxa/Poaceae/Chloris/chloris-cucullata")
CARD=BASE/"species.json";LEDGER=BASE/"image-sources.csv"
OUT=pathlib.Path("reports/lane5-chloris-cucullata-texas-three-20261027.json")
SPECIES="Chloris cucullata"
P=[
 {"ob":283863418,"id":510098390,"who":"Tyler Cannon","file":"texas-tyler-cannon-cucullata-raceme-underside-510098390.jpg",
 "role":"Actual Texas source-determined hooded windmillgrass: mature radiating racemes lifted against a finger, clearly showing dense one-sided rows of pale spikelets and several entire short whorl branches. No glume, sterile hood or paired lemma separated.",
 "label":"AUSTIN RACEME UNDERSIDES — dense single-sided spikelet rows in hand",
 "caption":"A living source-determined Austin Chloris cucullata inflorescence viewed against fingers. Each slender raceme has many tiny spikelets lined up along one side, with several short branches spreading from the same hub. The specimen confirms actual whorl architecture in another Texas locality. Neither the individual inflated sterile lemma nor its free hood margin or short awn insertion is dissected; fingers are not a true millimeter scale.",
 "why":"Clear different real Texas photograph teaching one-sided spikelets along multiple short branches, rather than simply repeating the whole bunch photo.",
 "tiles":[0,2,5]},
 {"ob":283690062,"id":509767009,"who":"Cody Stricker","file":"texas-cody-stricker-cucullata-attached-branch-509767009.jpg",
 "role":"Actual Cotulla Texas photographed narrow Chloris cucullata culm rising to a terminal whorl of multiple short straight racemes with visibly crowded green spikelets; lower leaves are adjacent, roots not visible.",
 "label":"COTULLA ATTACHED FLOWERING CULM — terminal whorl and narrow stem",
 "caption":"Cody Stricker photographed an attached hooded-windmillgrass flowering culm against red Texas soil near Cotulla. The green slender stem supports the short, tightly grouped terminal branches, with green spikelets arrayed along them. The stem remains held by the fingers; no entire root crown, measured ligule or individually isolated sterile hood is visible.",
 "why":"Shows the connection between a mature windmill head and a true slender flowering stem, helpful for beginners distinguishing the dense crowded Chloris from unrelated seedheads.",
 "tiles":[0,1]},
 {"ob":301079044,"id":542522932,"who":"Don Bosan-Bruno","file":"texas-don-bosan-bruno-cucullata-ground-basal-leaves-542522932.jpg",
 "role":"Actual Austin source-labelled Chloris cucullata rooted-in-ground growth cluster: dense narrow upright green leaf blades converging into basal leafy tufts among other grasses; soil surface visible, roots obscured.",
 "label":"AUSTIN LIVING BASAL TUFT — real erect green blades at soil surface",
 "caption":"A real Austin source-identified hooded windmillgrass clump shows numerous thin, upright, bluish-green leaves emerging toward the ground. Adjacent unrelated grass shoots may be present in this mixed stand, so do not label them all one plant. NO separated connected underground perennial crown, root system, rhizome, stolon node or measured inner 0.7–1 mm ciliate ligule can be demonstrated from these pixels.",
 "why":"Adds actual Central Texas vegetative growing habit from a second photographer; valuable for beginner field recognition outside full flowering season, without presenting hidden roots as photographed.",
 "tiles":[0,1]}
]
R={"species":SPECIES,"date":"2026-10-27","added":[],"held":[],"new_diagnostic_arrows":0,
"scientific_anatomy_hold":["actual opened inner ciliate membrane free edge at 1 mm physical scale","one photographed pulled-up live flowering plant with connected exposed roots and any actual runner","dissected measured upper sterile hood with same-source outer glumes and fertile lemma/awn origins"],
"rights_rule":"iNaturalist individual photo code cc-by; exact research-grade Chloris cucullata and creator reconfirmed"}
def get(url):
 for n in range(4):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyIndividuallyLicensedRealCucullataPhotoArchive/1.0 (educational)"})
   with urllib.request.urlopen(req,timeout=46) as f:d=f.read(15000000)
   if len(d)>14800000:raise ValueError("Response over 15MB")
   return d
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or n==3:raise
   time.sleep(2*(n+1))
d=json.loads(CARD.read_text());assert d["id"]=="chloris-cucullata"
obs_cache={}
new_rows=[]
for s in P:
 obid,pid=s["ob"],s["id"]
 rec={"source_observation":obid,"photo_id":pid}
 try:
  if obid not in obs_cache:
   obs_cache[obid]=next(iter(json.loads(get(f"https://api.inaturalist.org/v1/observations/{obid}")).get("results",[])),None)
  ob=obs_cache[obid]
  if not ob or (ob.get("taxon") or {}).get("name")!=SPECIES or ob.get("quality_grade")!="research":
   raise ValueError("Exact target species research-grade source absent")
  location=ob.get("place_guess") or ""
  if not re.search("Texas|TX\\b|Austin|Cotulla",location,re.I):raise ValueError("Source no longer confirms Texas locality")
  photo=next((p for p in ob.get("photos",[]) if p.get("id")==pid),None)
  if not photo:raise ValueError("Original photo no longer attached to observation")
  if (photo.get("license_code") or "").lower().replace("_","-")!="cc-by":raise ValueError("Individual source photo not CC BY")
  if s["who"].lower() not in (photo.get("attribution") or "").lower():raise ValueError("Exact source credited creator not verified")
  source=f"https://www.inaturalist.org/photos/{pid}"
  rel="images/"+s["file"]
  if any(x.get("file")==rel or x.get("source_page")==source for x in d["images"]):
   raise ValueError("Duplicate source photo")
  orig=re.sub(r"/(?:square|small|medium|thumb|large)\.(jpe?g|png)",r"/original.\1",photo.get("url") or "")
  if not orig.startswith("https://") or "/original." not in orig:raise ValueError("Original image URL not valid")
  raw=get(orig)
  with Image.open(io.BytesIO(raw)) as im:im.verify()
  with Image.open(io.BytesIO(raw)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   if min(im.size)<700:raise ValueError("Low resolution")
   im.thumbnail((2000,2000));size=list(im.size)
   buff=io.BytesIO();im.save(buff,"JPEG",quality=89,optimize=True);clean=buff.getvalue()
  dst=BASE/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(clean)
  with Image.open(dst) as im:im.verify()
  hash_=hashlib.sha256(clean).hexdigest()
  d["images"].append({"file":rel,"role":s["role"],"creator":s["who"],"license":"CC BY 4.0",
   "license_code_exact":"cc-by","license_url":"https://creativecommons.org/licenses/by/4.0/",
   "source_page":source,"source_observation":f"https://www.inaturalist.org/observations/{obid}",
   "source_original_url":orig,"photo_id":str(pid),"source_taxon":SPECIES,
   "source_region":location,"source_quality_grade":"research when archived",
   "photo_status":"REAL VERIFIED TEXAS EXACT SPECIES FIELD IMAGE; only directly visible external structures described",
   "modifications":"Original converted and metadata stripped as JPEG, no new anatomy arrows",
   "sha256":hash_,"pixels":size,
   "public_reuse":"Individual image-level CC BY checked and source photographer credit retained"})
  i=len(d["visual_comparison"]["items"])
  d["visual_comparison"]["items"].append({"label":s["label"],"scientific_name":SPECIES,
   "image_url":str(dst),"image_fit":"contain","image_role":s["role"],
   "caption":s["caption"],"why_it_matters":s["why"],"creator":s["who"],
   "license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/",
   "source_page":source,"markers":[],
   "photo_status":"Original image independently verified from iNaturalist accepted species, CC BY photographer source and decoded bytes. No false ligule, sterile hood or root anatomy labels."})
  for ti in s["tiles"]:
   tile=d["field_id_short_tiles"][ti]["photo_panel_indices"]
   if i not in tile:tile.append(i)
  new_rows.append((s["file"],s["role"],s["who"],source,orig,obid,pid))
  rec.update({"status":"archived","file":str(dst),"gallery_panel_index":i,"pixels":size,"sha256":hash_})
 except Exception as e:rec.update({"status":"HELD","reason":str(e)})
 R["added" if rec["status"]=="archived" else "held"].append(rec)
if R["added"]:
 d["curation_status"]["photo_metadata_count"]=len(d["images"])
 d["curation_status"]["photo_files_present"]=len(d["images"])
 d["curation_status"]["visual_finish"]="FIELD_READY_PHOTO_GAPS — three actual additional licensed Texas target grass photos show mature underside one-sided spikelet rows, Cotulla attached flowering stem, and Austin lower live leafy tuft. Still missing dissected hood, true ciliate ligule and connected root crown."
 d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
 d["lane5_cucullata_texas_three_20261027"]={"new_sources":R["added"],"stage":"FIELD_READY_PHOTO_GAPS",
    "remaining":R["scientific_anatomy_hold"],"arrows_added":0}
 CARD.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
 with LEDGER.open(newline="") as f:rd=csv.DictReader(f);fields=rd.fieldnames;rows=list(rd)
 existing={x["file_name"] for x in rows}
 for fname,role,author,src,orig,oid,pid in new_rows:
  if fname in existing:continue
  row=dict.fromkeys(fields,"")
  vals={"file_name":fname,"role":role,"creator":author,"license":"CC BY 4.0",
    "source_page":src,"direct_url":orig,"study_use":"source-verified botanical field ID",
    "public_reuse":"YES, image-specific CC BY source license with photographer credit",
    "license_url":"https://creativecommons.org/licenses/by/4.0/",
    "modifications":"RGB JPEG re-encoded and EXIF/GPS removed; no marker overlays"}
  for k,v in vals.items():
   if k in row:row[k]=v
  rows.append(row)
 with LEDGER.open("w",newline="") as f:wr=csv.DictWriter(f,fieldnames=fields);wr.writeheader();wr.writerows(rows)
 R["source_ledger_rows"]=len(rows)
OUT.parent.mkdir(exist_ok=True);OUT.write_text(json.dumps(R,indent=2)+"\n")
print(json.dumps(R))
