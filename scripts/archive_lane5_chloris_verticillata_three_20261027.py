#!/usr/bin/env python3
"""Archive three anatomically useful Douglas Goldman / Wikimedia Commons
photographs of Chloris verticillata, leaving duplicate V8 uninstalled.
V3 = flowering axis; V6 = real outside blade/sheath; V7 = culm NODE.
Do NOT claim inner ciliate ligule, nodes rooting, or scale-verified florets.
"""
import csv,hashlib,html,io,json,pathlib,re,time,urllib.parse,urllib.request,urllib.error
from PIL import Image,ImageOps
ROOT=pathlib.Path("content/taxa/Poaceae/Chloris/chloris-verticillata")
CARD=ROOT/"species.json"
CSV=ROOT/"image-sources.csv"
OUT=pathlib.Path("reports/lane5-chloris-verticillata-three-anatomy-20261027.json")
TARGETS=[
 {"name":"ChlorisV3.jpg","dest":"douglas-goldman-verticillata-attached-head-3.jpg",
 "label":"ATTACHED HEAD — windmill whorls along the flowering axis",
 "role":"True species-labeled multiple radiating one-sided racemes attached at distinct positions along the main flowering axis; base/root not in frame.",
 "caption":"Actual tumble windmillgrass flowering axis, with many fine rays spreading from a central stalk at multiple levels. Follow where each raceme joins the axis; do not assume a nearby green leaf belongs to the same shoot or that the detached head has roots.",
 "why":"Teaches tiers on a real attached flowering head, not a detached tumblehead or a different species.","tile":0},
 {"name":"ChlorisV6.jpg","dest":"douglas-goldman-verticillata-outer-sheath-6.jpg",
 "label":"ACTUAL LEAF SHEATH — green blade and sheath wrapping the culm",
 "role":"External leaf blade and overlapping green enclosing sheath against true culm; minute inner ligule membrane hidden.",
 "caption":"A real green grass sheath wrapping a flowering culm; the blade comes off along its upper edge and another sheath overlaps below. This is an exterior leaf/sheath view, not the exposed INNER collar or a photograph of the approximately 1–2 mm ciliate membrane.",
 "why":"Helps a beginner locate the sheath and distinguish outer overlapping tissue from the inner ligule still needing macro proof.","tile":1},
 {"name":"ChlorisV7.jpg","dest":"douglas-goldman-verticillata-culm-node-7.jpg",
 "label":"TRUE CULM NODE — joint and internodes (not a ligule)",
 "role":"Visible stem joint with pale circumferential node and green internodes above and below; roots absent.",
 "caption":"This photograph shows a genuine culm NODE, the pale ring across the grass stem, and long internodes on either side. This is NOT the inner leaf ligule and there is no photographed adventitious root at this node.",
 "why":"Prevents confusing a stem node ring with the blade–sheath collar and helps check lower rooting nodes later.","tile":1}
]
REPORT={"species":"Chloris verticillata","date":"2026-10-27","source_series":"Douglas Goldman source-labeled Wikimedia Commons ChlorisV1-V8","photos":[],"new_markers":0,"not_claimed":["Inner free ciliate ligule with mm scale","Root emergence from an actual lower node","Glume vs fertile and upper sterile lemma dissection with individual awn insertions"],"duplicate_not_promoted":"ChlorisV8.jpg — mature unilateral raceme macro role already well illustrated in existing gallery"}
def get(url):
 req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyOpenLicenseAnatomy/1.0 (educational botanical photo archive)"})
 for i in range(5):
  try:
   with urllib.request.urlopen(req,timeout=45) as r:raw=r.read(11000000)
   if len(raw)>10500000:raise ValueError("Response too large")
   return raw
  except urllib.error.HTTPError as ex:
   if ex.code not in (429,500,502,503,504) or i==4:raise
   time.sleep(2*(i+1))
data=json.loads(CARD.read_text());assert data["id"]=="chloris-verticillata"
for target in TARGETS:
 title=target["name"];source="https://commons.wikimedia.org/wiki/File:"+title
 rel="images/"+target["dest"]
 if any(v.get("file")==rel for v in data.get("images",[])):
  REPORT["photos"].append({"source":source,"status":"previously_archived"});continue
 try:
  q=urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo|categories",
     "cllimit":"max","iiprop":"url|extmetadata","iiurlwidth":"1800","titles":"File:"+title})
  page=next(iter(json.loads(get("https://commons.wikimedia.org/w/api.php?"+q))["query"]["pages"].values()))
  if "imageinfo" not in page:raise ValueError("Individual Commons file missing")
  info=page["imageinfo"][0];meta=info["extmetadata"]
  lic=re.sub(r"[^A-Z0-9]","",meta.get("LicenseShortName",{}).get("value","").upper())
  author=html.unescape(re.sub("<[^>]*>"," ",meta.get("Artist",{}).get("value",""))).strip()
  cats={x["title"] for x in page.get("categories",[])}
  if lic!="CCBYSA40" or "Douglas" not in author or "Category:Chloris verticillata" not in cats:
   raise ValueError("Individual author, CC BY-SA 4.0 license or species category gate failed: "+str([lic,author]))
  raw=get(info.get("thumburl") or info["url"])
  with Image.open(io.BytesIO(raw)) as im:im.verify()
  with Image.open(io.BytesIO(raw)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   if min(im.size)<750:raise ValueError("Image too low resolution "+str(im.size))
   pixels=list(im.size);buf=io.BytesIO();im.save(buf,"JPEG",quality=90,optimize=True);clean=buf.getvalue()
  if len(clean)<60000:raise ValueError("Unexpected small JPEG")
  dest=ROOT/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(clean)
  with Image.open(dest) as im:im.verify()
  sha=hashlib.sha256(clean).hexdigest()
  mod="RGB JPEG re-encoded from Commons width-1800 thumbnail; source EXIF/GPS removed, no burnt-in arrows"
  data["images"].append({"file":rel,"role":target["role"],"creator":"Douglas Goldman",
      "license":"CC BY-SA 4.0","license_url":"https://creativecommons.org/licenses/by-sa/4.0/",
      "source_page":source,"source_original_url":info["url"],
      "source_taxon":"Chloris verticillata, individually Wikimedia Commons category/source verified",
      "modifications":mod,"public_reuse":"Permitted under image-specific CC BY-SA 4.0; creator, source and version linked; modifications recorded",
      "sha256":sha,"pixels":pixels,
      "photo_status":"Actual source-verified photograph; anatomical description based on preview; no 1-mm fine-feature arrows"})
  idx=len(data["visual_comparison"]["items"])
  data["visual_comparison"]["items"].append({
      "label":target["label"],"scientific_name":"Chloris verticillata",
      "image_url":str(dest),"image_fit":"contain","image_role":target["role"],
      "caption":target["caption"],"why_it_matters":target["why"],"creator":"Douglas Goldman",
      "license":"CC BY-SA 4.0","license_url":"https://creativecommons.org/licenses/by-sa/4.0/",
      "source_page":source,"markers":[],
      "photo_status":"Real original photographic source pixel preview checked 2026-10-27; role is coarse visible anatomy, true ligule and microscopic details not marked."})
  tile=data["field_id_short_tiles"][target["tile"]]
  tile["photo_panel_indices"].append(idx)
  REPORT["photos"].append({"source":source,"status":"archived","file":str(dest),
      "pixels":pixels,"bytes":len(clean),"sha256":sha,"gallery_index":idx,"license":"CC BY-SA 4.0"})
 except Exception as exc:REPORT["photos"].append({"source":source,"status":"HELD","reason":str(exc)[:350]})
added=[x for x in REPORT["photos"] if x["status"]=="archived"]
if added:
 data.setdefault("lane5_douglas_goldman_three_20261027",{}).update({
  "photographs":added,"status":"FIELD_READY_PHOTO_GAPS",
  "photo_roles":"actual attached inflorescence, external true leaf sheath, actual culm node",
  "not_photographically_proven":REPORT["not_claimed"],
  "score_guidance":"Do not increase six-role score for unexposed ligule or unattached awn anatomy; existing root-crown photographed elsewhere."})
 data.setdefault("curation_status",{})["photo_metadata_count"]=len(data["images"])
 data["curation_status"]["photo_files_present"]=len(data["images"])
 data.setdefault("learner_visual_status",{})["image_count"]=len(data["images"])
 CARD.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
 # Keep source ledger current without overwriting existing rows or changing their rights.
 if CSV.exists():
  with CSV.open(newline="") as f:rd=csv.DictReader(f);columns=rd.fieldnames;rows=list(rd)
  assert "file_name" in columns
  existing_names={r.get("file_name") for r in rows}
  for spec in TARGETS:
   rec=next((r for r in added if r["source"].endswith(spec["name"])),None)
   if rec and spec["dest"] not in existing_names:
    row=dict.fromkeys(columns,"")
    fields={"file_name":spec["dest"],"role":spec["role"],"creator":"Douglas Goldman",
       "license":"CC BY-SA 4.0","source_page":rec["source"],
       "direct_url":"","study_use":"educational botanical photo lesson",
       "public_reuse":"Permitted under image-level CC BY-SA 4.0",
       "license_url":"https://creativecommons.org/licenses/by-sa/4.0/","modifications":mod}
    for k,v in fields.items():
     if k in row:row[k]=v
    rows.append(row)
  with CSV.open("w",newline="") as f:wr=csv.DictWriter(f,fieldnames=columns);wr.writeheader();wr.writerows(rows)
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(REPORT,indent=2)+"\n")
print(json.dumps(REPORT))
