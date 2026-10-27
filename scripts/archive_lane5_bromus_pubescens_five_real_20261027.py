#!/usr/bin/env python3
"""Lane 5 real woodland brome licensed photos. Individual observation taxon,
research grade, source photo cc-by and author required. No microscopic
hair/glume/ligule claims. New panels appended so old indices stay stable.
"""
import csv,hashlib,io,json,pathlib,re,time,urllib.request,urllib.error
from PIL import Image,ImageOps
ROOT=pathlib.Path("content/taxa/Poaceae/Bromus/bromus-pubescens")
CARD=ROOT/"species.json";LEDGER=ROOT/"image-sources.csv"
REPORT=pathlib.Path("reports/lane5-bromus-pubescens-five-diagnostic-20261027.json")
CANDIDATES=[
{"oid":75093729,"pid":122809054,"name":"Sophia K",
 "title":"REAL UPPER LEAF SHEATH — green blade, sheath wrap, actual culm",
 "role":"Close-up real source-identified Bromus pubescens exterior green leaf blade and overlapping enclosing sheath along flowering shoot; inner 0.5–2 mm ligule not pulled open",
 "caption":"A photographed upper blade branches from its tight green enclosing leaf sheath along the culm. Look for the actual blade–sheath opening, but DO NOT label the outside green sheath lip as the tiny INNER membranous ligule. Exact ligule free margin and sheath hairs remain unmeasured.",
 "why":"A real vegetative structure in an exact-species source photo, not another-only seedhead.","tiles":[1]},
{"oid":75093729,"pid":122809074,"name":"Sophia K",
 "title":"REAL WOODLAND HABIT — living green leaves in shallow soil",
 "role":"Source-labelled native woodland brome live plant growing amid vegetation along Austin woodland margin; leafy lower shoots and soil in frame, roots not exposed",
 "caption":"This exact-source woodland brome grows among other green vegetation at the edge of a wooded Austin site. A loose bunch of broad green blades is visible at ground level. Nearby vegetation may be other plants; NO extracted fibrous roots, single connected crown-to-head voucher, or perennial age are proven by this shot.",
 "why":"Gives crew the growing environment and rough low bunch context, distinct from cropped flowering heads.","tiles":[0,1]},
{"oid":75169322,"pid":122941694,"name":"Michelle W",
 "title":"TRUE CULM NODE — leaf insertion and stem joint (NOT ligule)",
 "role":"Real green brome stem with external leaf blade attaching above sheath and small pale stem node scar at culm joint; precise inner ligule and hair origins not proved",
 "caption":"This photograph captures a living true grass culm joint and the neighboring leaf-sheath region. Find the V of leaf and culm, then distinguish the pale STEM NODE scar from the unseen INNER membranous ligule. No separated 0.5–2-mm membrane or calibrated short hairs are shown.",
 "why":"Teaches beginners exactly where the stem node is, without confusing it with the collar membrane.","tiles":[1]},
{"oid":76282607,"pid":124787218,"name":"Sam Kieschnick",
 "title":"FRESH MULTIFLORED SPIKELETS — source-identified woodland brome",
 "role":"Fresh green narrow awned multi-flowered woodland brome spikelets held alongside broad leaf in a Texas forested park; no calibrated separate glume/lemma",
 "caption":"A Fort Worth woodland-brome flowering branch photographed against fingers shows living narrow green spikelets with pointed bracts and awns. Each SPIKELET contains several florets. This is not a dissection: the usual 1/3-veined glume pair, lemma hairs and awn insertion cannot be safely marked.",
 "why":"Adds living reproductive shape to the existing very small flowering photo and botanical-garden leafy-habit view.","tiles":[2,3]},
{"oid":84333645,"pid":138597227,"name":"Sam Kieschnick",
 "title":"MATURE DRY SPIKELETS — overlapping bracts and projecting awns",
 "role":"Mature dry source-identified woodland-brome spikelets photographed close in the field in East Texas, overlapping elongated pale florets and thin awns; no glume count/scale",
 "caption":"The photographed mature dry woodland-brome spikelets show many overlapping narrow brown bracts and long slender awns. The source plant is from near Hawkins, Texas. The picture does not separate lower from upper glume or show backlit 1/3 veins, detached hairy lemma surface, palea keels or measured awn insertion.",
 "why":"A high-value dry-season actual species reproductive reference instead of another distant panicle.","tiles":[2,3,4]}
]
report={"species":"Bromus pubescens","date":"2026-10-27","photos":[],"holds":[],"new_arrows":0,
        "gaps":["Visible extracted perennial fibrous roots of same flowering plant","Actual true inner 0.5–2mm free membranous ligule with mm scale","Measured backlit lower 1-veined and upper 3-veined glumes","Detached mature dorsal-hairy lemma plus palea and attached awn insertion"]}
def get(url):
 for n in range(4):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyIndividuallyOpenLicensedWoodlandGrass/1.0 (educational)"})
   with urllib.request.urlopen(req,timeout=50) as f:b=f.read(17500000)
   if len(b)>=17500000:raise ValueError("Oversize source response")
   return b
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or n==3:raise
   time.sleep((n+1)*2)
o=json.loads(CARD.read_text());assert o["id"]=="bromus-pubescens"
obs={};added=[]
for c in CANDIDATES:
 oid=c["oid"];pid=c["pid"];rec={"photo_id":pid,"observation_id":oid}
 try:
  if oid not in obs:
   data=json.loads(get("https://api.inaturalist.org/v1/observations/"+str(oid)))
   obs[oid]=next(iter(data.get("results",[])),None)
  ob=obs[oid]
  if not ob or (ob.get("taxon") or {}).get("name")!="Bromus pubescens" or ob.get("quality_grade")!="research":
   raise ValueError("Current exact species or research grade not verified")
  place=ob.get("place_guess") or ""
  if not re.search(r"Texas|TX\b|Austin|Fort Worth|Hawkins",place,re.I):raise ValueError("Place no longer identified as Texas")
  p=next((p for p in ob.get("photos",[]) if p.get("id")==pid),None)
  if not p:raise ValueError("Source observation lost photo")
  lic=(p.get("license_code") or "").lower().replace("_","-")
  if lic!="cc-by":raise ValueError("Individual source image not CC BY: "+repr(lic))
  creator=p.get("attribution") or ""
  if c["name"].lower() not in creator.lower():raise ValueError("Author mismatch")
  source=f"https://www.inaturalist.org/photos/{pid}"
  rel=f"images/tx-woodland-brome-{pid}.jpg"
  if any(x.get("file")==rel or x.get("source_page")==source for x in o["images"]):
   raise ValueError("Image already archived; no duplicate")
  uri=re.sub(r"/(?:square|small|medium|thumb|large)\.(jpe?g|png)",r"/original.\1",p.get("url") or "")
  if not uri.startswith("https://") or "/original." not in uri:raise ValueError("Source URL malformed")
  original=get(uri)
  with Image.open(io.BytesIO(original)) as im:im.verify()
  with Image.open(io.BytesIO(original)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   if min(im.size)<650:raise ValueError("Image insufficient for gross feature")
   im.thumbnail((2000,2000));pixels=list(im.size)
   out=io.BytesIO();im.save(out,"JPEG",quality=90,optimize=True);clean=out.getvalue()
  dst=ROOT/rel;dst.parent.mkdir(exist_ok=True);dst.write_bytes(clean)
  with Image.open(dst) as im:im.verify()
  sha=hashlib.sha256(clean).hexdigest()
  o["images"].append({"file":rel,"role":c["role"],"creator":c["name"],"license":"CC BY",
    "license_code_exact":"cc-by","source_page":source,
    "source_observation":f"https://www.inaturalist.org/observations/{oid}",
    "photo_id":pid,"source_region":place,"source_taxon":"Bromus pubescens, source observation research-grade",
    "modifications":"RGB JPEG re-encoded, EXIF/GPS stripped. Browser arrows 0.",
    "sha256":sha,"pixels":pixels,"public_reuse":"Individual CC BY license and creator verified live from photo metadata",
    "photo_status":"Authentic source-labelled regional photo, role restricted to visible coarse structures"})
  idx=len(o["visual_comparison"]["items"])
  o["visual_comparison"]["items"].append({"label":c["title"],"scientific_name":"Bromus pubescens",
    "image_url":str(dst),"image_fit":"contain","image_role":c["role"],
    "caption":c["caption"],"why_it_matters":c["why"],"creator":c["name"],"license":"CC BY",
    "source_page":source,"markers":[],
    "photo_status":"Pixel-reviewed specimen-specific gross photo, individual image license and source validated, no fine structure arrows"})
  for i in c["tiles"]:
   if idx not in o["field_id_short_tiles"][i]["photo_panel_indices"]:
    o["field_id_short_tiles"][i]["photo_panel_indices"].append(idx)
  rec.update({"status":"archived","pixels":pixels,"file":str(dst),"gallery_index":idx,"sha256":sha,"license":"cc-by"})
  added.append((pathlib.Path(rel).name,c["role"],c["name"],source,oid,pid,uri))
 except Exception as e:rec.update({"status":"HELD","reason":str(e)})
 report["photos" if rec["status"]=="archived" else "holds"].append(rec)
if report["photos"]:
 o["curation_status"]["photo_metadata_count"]=len(o["images"])
 o["curation_status"]["photo_files_present"]=len(o["images"])
 o["curation_status"]["visual_finish"]="FIELD_READY_PHOTO_GAPS — open-licensed Texas whole woodland habit, live true exterior sheath/node and fresh/dry multi-flowered spikelets archived; actual inner ligule and connected rooted perennial crown and mature 1mm dissection missing."
 o.setdefault("learner_visual_status",{})["image_count"]=len(o["images"])
 o.setdefault("lane5_woodland_brome_five_real_photos_20261027",{}).update({
   "added":report["photos"],"status":"FIELD_READY_PHOTO_GAPS","unresolved":report["gaps"],"new_arrows":0})
 CARD.write_text(json.dumps(o,indent=2,ensure_ascii=False)+"\n")
 if LEDGER.exists():
  with LEDGER.open(newline="") as f:rd=csv.DictReader(f);fields=rd.fieldnames;rows=list(rd)
  for filename,role,creator,source,oid,pid,url in added:
   if any(x.get("file_name")==filename for x in rows):continue
   row=dict.fromkeys(fields,"")
   for k,v in {"file_name":filename,"role":role,"creator":creator,"license":"CC BY",
    "source_page":source,"direct_url":url,"study_use":"source-checked educational real grass anatomy",
    "public_reuse":"Individual image-level CC BY confirmed","observation_id":str(oid),"photo_id":str(pid)}.items():
    if k in row:row[k]=v
   rows.append(row)
  with LEDGER.open("w",newline="") as f:wr=csv.DictWriter(f,fieldnames=fields);wr.writeheader();wr.writerows(rows)
REPORT.parent.mkdir(exist_ok=True);REPORT.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
