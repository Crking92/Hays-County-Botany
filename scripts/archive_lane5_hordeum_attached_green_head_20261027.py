#!/usr/bin/env python3
"""Lane 5 little barley: source-specific attached green spike macro.
CC BY-SA 2.0 Matt Lavin / individual Commons source verified. No false
single-node triad, glume, or ligule assertions. Existing indices unchanged.
"""
import hashlib,html,io,json,pathlib,re,time,urllib.parse,urllib.request,urllib.error,csv
from PIL import Image,ImageOps
ROOT=pathlib.Path("content/taxa/Poaceae/Hordeum/hordeum-pusillum")
CARD=ROOT/"species.json";LEDGER=ROOT/"image-sources.csv"
REPORT=pathlib.Path("reports/lane5-hordeum-pusillum-attached-green-spike-20261027.json")
SOURCE="https://commons.wikimedia.org/wiki/File:Hordeum_pusillum_(7495172732).jpg"
NAME="Hordeum pusillum (7495172732).jpg"
REL="images/matt-lavin-little-barley-attached-rachis-spike-7495172732.jpg"
report={"species":"Hordeum pusillum","source":SOURCE,"added":[],"held":[],"arrows_added":0,"anatomy_boundary":"Photographed intact green head with overlapping spikelet bodies and many awns; individual 3-spikelet node grouping, fertile/sterile glumes and lemma awns not certified."}
def get(url):
 for n in range(4):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyIndividuallyLicensedPhotoArchivist/1.0 (field identification education)"})
   with urllib.request.urlopen(req,timeout=50) as f:raw=f.read(16000000)
   if len(raw)>15500000:raise ValueError("oversize")
   return raw
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or n==3:raise
   time.sleep(3*(n+1))
try:
 query=urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo|categories","cllimit":"max","iiprop":"url|extmetadata","iiurlwidth":"1900","titles":"File:"+NAME})
 page=next(iter(json.loads(get("https://commons.wikimedia.org/w/api.php?"+query))["query"]["pages"].values()))
 info=page["imageinfo"][0];md=info["extmetadata"]
 lic=re.sub("[^A-Z0-9]","",md.get("LicenseShortName",{}).get("value","").upper())
 artist=html.unescape(re.sub("<[^>]+>"," ",md.get("Artist",{}).get("value",""))).strip()
 if lic!="CCBYSA20" or "Matt Lavin" not in artist or "Category:Hordeum pusillum" not in [c["title"] for c in page.get("categories",[])]:
  raise ValueError("Exact taxon + photographer + CC BY-SA 2.0 must all verify")
 raw=get(info.get("thumburl") or info["url"])
 with Image.open(io.BytesIO(raw)) as im:im.verify()
 with Image.open(io.BytesIO(raw)) as im:
  im=ImageOps.exif_transpose(im).convert("RGB")
  if min(im.size)<1000:raise ValueError("High-resolution image not available")
  pixels=list(im.size);buf=io.BytesIO();im.save(buf,"JPEG",quality=90,optimize=True);binary=buf.getvalue()
 d=json.loads(CARD.read_text());assert d["id"]=="hordeum-pusillum"
 if any(x.get("file")==REL or urllib.parse.unquote(x.get("source_page",""))==SOURCE for x in d["images"]):
  raise ValueError("Already installed — no duplicate")
 dest=ROOT/REL;dest.parent.mkdir(exist_ok=True);dest.write_bytes(binary)
 with Image.open(dest) as im:im.verify()
 sha=hashlib.sha256(binary).hexdigest()
 d["images"].append({"file":REL,"role":"Intact upright green flowering spike at close distance with attached one-sided awned bract/spikelet rows; no proven isolated rachis triad",
   "creator":"Matt Lavin","license":"CC BY-SA 2.0","license_url":"https://creativecommons.org/licenses/by-sa/2.0/",
   "source_page":SOURCE,"source_original_url":info["url"],"source_region":"Charles M. Russell National Wildlife Refuge, Montana; not Texas",
   "modifications":"1900px licensed rendition converted RGB JPEG with EXIF/GPS removed; no burnt-in arrows or dissected units",
   "public_reuse":"Author and individual Commons CC BY-SA 2.0 source verified, attribution and adaptation stated",
   "photo_status":"Real species-specific attached green head; individual glumes/rachis-node triad unresolved",
   "sha256":sha,"pixels":pixels})
 i=len(d["visual_comparison"]["items"])
 d["visual_comparison"]["items"].append({
   "label":"INTACT GREEN SPIKE — overlapping awned flowering units attached to the central axis",
   "scientific_name":"Hordeum pusillum","image_url":str(dest),"image_fit":"contain",
   "image_role":"Genuine species-labelled closeup of attached green H. pusillum flowering spike; narrow bracts and many awns visible, central plus two laterals cannot be independently traced.",
   "caption":"The green little-barley spike is intact, and narrow pointed flowering bracts and long awns overlap in close view. Follow the central upright stalk from base to tip, then compare detached pieces in earlier panels. The photograph does NOT isolate one complete 3-spikelet rachis node with a 1-mm scale, and individual glumes/lemmas should not be labeled from this view.",
   "why_it_matters":"Bridges the detached dried awned units and the distant whole-head photograph with genuine fresh still-attached structure.",
   "creator":"Matt Lavin","license":"CC BY-SA 2.0","license_url":"https://creativecommons.org/licenses/by-sa/2.0/",
   "source_page":SOURCE,"markers":[],
   "photo_status":"Real licensed exact taxon and actual still-attached green seedhead; anatomy limited to gross visible forms, no arrows."
 })
 d["field_id_short_tiles"][0]["photo_panel_indices"].append(i)
 d["field_id_short_tiles"][3]["photo_panel_indices"].append(i)
 d["curation_status"]["photo_files_present"]=len(d["images"])
 d["curation_status"]["photo_metadata_count"]=len(d["images"])
 d["learner_visual_status"]["image_count"]=len(d["images"])
 d.setdefault("lane5_attached_green_head_20261027",{}).update({"gallery_index":i,"source":SOURCE,"sha256":sha,"stage":"FIELD_READY_PHOTO_GAPS",
   "photo_roles":"Fresh attached flowering spike, still needs an intact 1mm-calibrated rachis triad, opened true inner ligule and actual rooted base"})
 CARD.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
 # Append individual credit/license to the file ledger.
 with LEDGER.open(newline="") as f: rd=csv.DictReader(f);fields=rd.fieldnames;rows=list(rd)
 if not any(x["file_name"]==dest.name for x in rows):
  r=dict.fromkeys(fields,"")
  for k,v in {"file_name":dest.name,"role":"Real intact green H. pusillum rachis head, individual 3-spikelet group unproven",
   "creator":"Matt Lavin","license":"CC BY-SA 2.0","source_page":SOURCE,
   "direct_url":info["url"],"study_use":"educational with CC BY-SA credit","public_reuse":"YES; image-level license independently checked"}.items():
   if k in r:r[k]=v
  rows.append(r)
  with LEDGER.open("w",newline="") as f: wr=csv.DictWriter(f,fieldnames=fields);wr.writeheader();wr.writerows(rows)
 report["added"].append({"path":str(dest),"sha256":sha,"pixels":pixels,"bytes":len(binary),"gallery_index":i})
except Exception as e:report["held"].append(str(e))
REPORT.parent.mkdir(exist_ok=True)
REPORT.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
