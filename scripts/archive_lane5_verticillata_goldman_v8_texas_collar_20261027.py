#!/usr/bin/env python3
"""Lane 5: archive two distinct, genuine Chloris verticillata photos after real
contact-sheet pixel review. Source-specific public licensing only. NO new
ligule/lemma/glume or rooted-node claims unless explicitly visible.
"""
import csv,hashlib,html,io,json,pathlib,re,time,urllib.parse,urllib.request,urllib.error
from PIL import Image,ImageOps
BASE=pathlib.Path("content/taxa/Poaceae/Chloris/chloris-verticillata")
CARD=BASE/"species.json";LEDGER=BASE/"image-sources.csv"
REPORT=pathlib.Path("reports/lane5-chloris-verticillata-two-real-20261027.json")
SPECIES="Chloris verticillata"
SELECTION=[
 {"source":"Commons","name":"ChlorisV8.jpg",
  "file":"douglas-goldman-verticillata-mature-attached-spikelet-detail-v8.jpg",
  "label":"REAL ONE-SIDED SPIKELET ROW — attached bracts and awns on raceme",
  "role":"Source-identified exact species close photographic view of one slender Chloris verticillata raceme with a regular alternating one-sided row of awned units; individual glumes, fertile lemma, upper sterile lemma and separate awn insertions NOT independently resolved.",
  "caption":"Douglas Goldman's unarchived photograph shows a close, continuous portion of the actual slender spikelet-bearing raceme against a dark background. Notice the overlapping pale narrow units and their distribution along the same rachis. No 1-mm reference or separately isolated upper sterile lemma or basal glume pair is in this view, so do not mark microscopic vein counts or assign an individual awn to either floret.",
  "why":"A different true same-taxon close-up places repeated overlapping floral units on ONE intact slender branch. It complements the detached awn and tiered-whorl photographs, without pretending to be a measured floret dissection.",
  "tiles":[2,3,4]},
 {"source":"iNaturalist","observation":330926974,"pid":600205067,
  "file":"texas-idclaire-verticillata-outer-leaf-blade-sheath-junction-600205067.jpg",
  "label":"ACTUAL TEXAS BLADE–SHEATH TRANSITION — green leaf insertion, inner ligule not resolved",
  "role":"Source-labelled San Antonio Texas live Chloris verticillata narrow leaf blade, green surrounding sheath and pale external blade-sheath transition on a held flowering shoot; true INSIDE 0.7–1.3mm ciliate membranous ligule free edge not isolated.",
  "caption":"A real source-identified San Antonio tumble windmillgrass leafy shoot is held apart to show a flat narrow blade and overlapping green sheath near their actual junction. The pale seam provides a location where the INSIDE ciliate ligule should be searched for, but the photograph does not show its complete free edge with a true ruler. Do not treat the sheath rim, external hairs or nearby stem joint as a proven ligule. Roots are also not exposed.",
  "why":"Adds a real regional live vegetative example in contrast to the earlier Massachusetts/Montana sheath close-ups, while leaving the true short ciliate membrane as an explicit unresolved anatomy target.",
  "tiles":[1]}
]
R={"species":SPECIES,"date":"2026-10-27","added":[],"holds":[],"new_arrows":0,
   "not_certified":["The face-on 0.7–1.3mm ciliate inner free ligule and true scale","Separately identified lower fertile and upper sterile lemmas and BOTH actual awn insertions at 0.5–1mm","Isolated paired glumes/vein count against a real ruler","Any extra roots arising at a connected decumbent STEM NODE"]}
def get(url):
 for i in range(4):
  try:
   q=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotanyLicensedTrueWindmillgrassPhotoArchive/1.0 (educational)"})
   with urllib.request.urlopen(q,timeout=48) as f:b=f.read(13000000)
   if len(b)>12700000:raise ValueError("Media response too large")
   return b
  except urllib.error.HTTPError as exc:
   if exc.code not in (429,500,502,503,504) or i==3:raise
   time.sleep(2*(i+1))
def get_meta(p):
 if p["source"]=="Commons":
  params={"action":"query","format":"json","prop":"imageinfo|categories","cllimit":"max","iiprop":"url|extmetadata","iiurlwidth":"2000","titles":"File:"+p["name"]}
  page=next(iter(json.loads(get("https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(params)))["query"]["pages"].values()))
  info=page["imageinfo"][0];md=info["extmetadata"]
  lic=re.sub("[^A-Z0-9]","",md.get("LicenseShortName",{}).get("value","").upper())
  artist=html.unescape(re.sub("<[^>]*>"," ",md.get("Artist",{}).get("value",""))).strip()
  cats={c["title"] for c in page.get("categories",[])}
  if lic!="CCBYSA40" or "Douglas Goldman" not in artist or "Category:Chloris verticillata" not in cats:raise ValueError("Wikimedia photo author, exact species category or CC BY-SA 4.0 failed")
  return {"url":info.get("thumburl") or info["url"],"creator":"Douglas Goldman",
   "license":"CC BY-SA 4.0","license_url":"https://creativecommons.org/licenses/by-sa/4.0/",
   "source_page":"https://commons.wikimedia.org/wiki/File:ChlorisV8.jpg",
   "source_orig":info["url"],"region":"Wikimedia original source, not geographically claimed as Texas"}
 obs=next(iter(json.loads(get(f"https://api.inaturalist.org/v1/observations/{p['observation']}")).get("results",[])),None)
 if not obs or (obs.get("taxon") or {}).get("name")!=SPECIES or obs.get("quality_grade")!="research":raise ValueError("Source original observation not research-grade exact taxon")
 place=obs.get("place_guess") or ""
 if not re.search(r"Texas|TX\b|San Antonio|Bexar",place,re.I):raise ValueError("Texas provenance missing")
 photo=next((p0 for p0 in obs.get("photos",[]) if p0.get("id")==p["pid"]),None)
 if not photo or (photo.get("license_code") or "").lower().replace("_","-")!="cc-by":raise ValueError("Individual photo source license no longer CC BY")
 if "IDClaire" not in (photo.get("attribution") or ""):raise ValueError("Individual photographer source mismatch")
 uri=re.sub(r"/(?:square|small|medium|thumb|large)\.(jpe?g|png)",r"/original.\1",photo.get("url") or "")
 if not uri.startswith("https://") or "/original." not in uri:raise ValueError("Source original photo URL malformed")
 return {"url":uri,"creator":"IDClaire","license":"CC BY 4.0",
  "license_url":"https://creativecommons.org/licenses/by/4.0/",
  "source_page":f"https://www.inaturalist.org/photos/{p['pid']}",
  "source_orig":uri,"region":place,"observation_url":f"https://www.inaturalist.org/observations/{p['observation']}",
  "photo_id":str(p["pid"]),"observation_id":str(p["observation"])}
d=json.loads(CARD.read_text());assert d["id"]=="chloris-verticillata"
new=[]
for p in SELECTION:
 record={"source":p.get("name") or p.get("pid")}
 try:
  meta=get_meta(p)
  rel="images/"+p["file"]
  if any(im.get("file")==rel or im.get("source_page")==meta["source_page"] for im in d["images"]):raise ValueError("Photo duplicate")
  raw=get(meta["url"])
  with Image.open(io.BytesIO(raw)) as im:im.verify()
  with Image.open(io.BytesIO(raw)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   if min(im.size)<550:raise ValueError("Pixel resolution inadequate")
   im.thumbnail((2000,2000));pixels=list(im.size);buf=io.BytesIO();im.save(buf,"JPEG",quality=90,optimize=True);clean=buf.getvalue()
  dst=BASE/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(clean)
  with Image.open(dst) as im:im.verify()
  sha=hashlib.sha256(clean).hexdigest()
  d["images"].append({"file":rel,"role":p["role"],"creator":meta["creator"],"license":meta["license"],
   "license_url":meta["license_url"],"source_page":meta["source_page"],"source_original_url":meta["source_orig"],
   "source_location":meta["region"],"observation_id":meta.get("observation_id"),"photo_id":meta.get("photo_id"),
   "source_taxon":SPECIES,"source_evidence":"Exact source taxon and individual photo license checked 2026-10-27",
   "modifications":"Source photograph re-encoded JPEG and EXIF/GPS removed; no new arrows",
   "sha256":sha,"pixels":pixels,
   "public_reuse":"Photo-specific open CC BY/CC BY-SA rights verified; credit and adaptations noted",
   "photo_status":"Real source-labelled exact species anatomical field photo; no submillimeter structures certified"})
  idx=len(d["visual_comparison"]["items"])
  d["visual_comparison"]["items"].append({"label":p["label"],"scientific_name":SPECIES,"image_url":str(dst),
   "image_fit":"contain","image_role":p["role"],"caption":p["caption"],"why_it_matters":p["why"],
   "creator":meta["creator"],"license":meta["license"],"license_url":meta["license_url"],
   "source_page":meta["source_page"],"markers":[],
   "photo_status":"Exact source/right/pixels verified; two new photo roles limited to visible attached spikelet arrangement or Texas outer collar, not the true ligule or lemma glumes."})
  for ti in p["tiles"]:
   a=d["field_id_short_tiles"][ti]["photo_panel_indices"]
   if idx not in a:a.append(idx)
  record.update({"status":"archived","file":str(dst),"gallery_index":idx,"sha256":sha,"pixels":pixels})
  new.append((p["file"],p["role"],meta))
 except Exception as e:record.update({"status":"HELD","reason":str(e)})
 R["added" if record["status"]=="archived" else "holds"].append(record)
if R["added"]:
 d["curation_status"]["photo_metadata_count"]=len(d["images"])
 d["curation_status"]["photo_files_present"]=len(d["images"])
 d["curation_status"]["visual_finish"]="FIELD_READY_PHOTO_GAPS — real rooted fibrous crown, two collar views, node, tiered heads, awned spikelets, plus extra true raceme micro-detail and Texas external collar. Unresolved true inner short ligule and dissected two-floret awns/glumes."
 d["learner_visual_status"]["image_count"]=len(d["images"])
 d["lane5_verticillata_two_images_20261027"]={"new":R["added"],"stage":"FIELD_READY_PHOTO_GAPS",
    "missing":R["not_certified"],"new_arrows":0}
 CARD.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
 with LEDGER.open(newline="") as f:rd=csv.DictReader(f);fields=rd.fieldnames;rows=list(rd)
 existing={x["file_name"] for x in rows}
 for name,role,meta in new:
  if name in existing:continue
  row=dict.fromkeys(fields,"")
  vals={"file_name":name,"role":role,"creator":meta["creator"],"license":meta["license"],
    "source_page":meta["source_page"],"direct_url":meta["source_orig"],
    "study_use":"educational botanical learner with attributed source image",
    "public_reuse":"Image-specific license verified; CC BY-SA retained where applicable",
    "license_url":meta["license_url"],"observation_id":meta.get("observation_id") or "",
    "photo_id":meta.get("photo_id") or "","review":"Photo exact taxon, pixels and open reuse rights confirmed; true inner ligule and dissected lemmas unverified",
    "modifications":"Original re-encoded RGB JPEG, EXIF/GPS removed, zero new markers"}
  for k,v in vals.items():
   if k in row:row[k]=v
  rows.append(row);existing.add(name)
 with LEDGER.open("w",newline="") as f:wr=csv.DictWriter(f,fieldnames=fields);wr.writeheader();wr.writerows(rows)
 R["photo_ledger_rows"]=len(rows)
REPORT.parent.mkdir(exist_ok=True);REPORT.write_text(json.dumps(R,indent=2)+"\n")
print(json.dumps(R))
