#!/usr/bin/env python3
"""Licensed feather-fingergrass diagnostic macrophotographs.
Two photographer-original Jim Conrad images (express public domain) and
a Harry Rose Wikimedia Commons CC BY 2.0 authentic two-awn floret image.
No inferred floret attachment or fake millimeter measurements.
"""
import hashlib, html, io, json, pathlib, re, time, urllib.parse, urllib.request, urllib.error
from PIL import Image
ROOT=pathlib.Path("content/taxa/Poaceae/Chloris/chloris-virgata")
CARD=ROOT/"species.json"
S=json.loads(CARD.read_text())
REPORT=pathlib.Path("reports/lane5-feather-fingergrass-anatomy-archive-20261025.json")
BACKYARD="https://backyardnature.net/mexnat/qto/chloris.htm"
PD_GRANT="https://www.backyardnature.net/j/copyrite.htm"
COMMONS="https://commons.wikimedia.org/wiki/File:Chloris_virgata_florets_(6774086110).jpg"
def get(url):
 req=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 (licensed educational botanical photo archive)","Accept":"image/jpeg,text/html,application/json,*/*"})
 for attempt in range(5):
  try:
   with urllib.request.urlopen(req,timeout=50) as f:return f.read()
  except urllib.error.HTTPError as ex:
   if ex.code not in (429,500,502,503) or attempt==4:raise
   time.sleep(2**attempt+2)
def jpg(src,dest):
 try:
  data=get(src)
 except urllib.error.HTTPError as exc:
  if exc.code in (429,503) and ("6774086110" in src or "Chloris_virgata_florets" in src):
   # Same Harry Rose image linked as original Flickr source by Commons;
   # preserves photographer and Commons-verified CC BY 2.0 rights.
   data=get("https://live.staticflickr.com/7188/6774086110_322984fc6d_o.jpg")
  else:
   raise
 check=Image.open(io.BytesIO(data));check.verify()
 im=Image.open(io.BytesIO(data)).convert("RGB")
 if min(im.size)<340:raise ValueError("Insufficient diagnostic image size: "+str(im.size))
 dest.parent.mkdir(parents=True,exist_ok=True)
 # Preserve aspect; pixel overlays live in separate metadata only; EXIF/GPS stripped.
 if max(im.size)>1920:
  im.thumbnail((1920,1920),Image.Resampling.LANCZOS)
 im.save(dest,"JPEG",quality=91,optimize=True)
 return list(im.size),hashlib.sha256(dest.read_bytes()).hexdigest()
grant=re.sub(r"<[^>]+>"," ",get(PD_GRANT).decode("utf-8","replace"))
page=get(BACKYARD).decode("utf-8","replace")
if not re.search(r"PUBLIC\s+DOMAIN\s+all\s+images\s+produced\s+by\s+myself",grant,re.I):
 raise RuntimeError("Cannot verify explicit public-domain grant; do not publish Jim Conrad photos")
if "Jim Conrad" not in page or not re.search(r"CHLORIS\s+VIRGATA",page,re.I):
 raise RuntimeError("Jim Conrad original source page/taxon cannot be confirmed")
specs=[
 {
  "source":"https://backyardnature.net/mexnat/qto/chloriu.jpg",
  "file":"jim-conrad-chloris-virgata-loose-florets-and-glumes.jpg",
  "title":"LOOSE FLORET UNITS — long awns and persistent glumes",
  "role":"Photographer-identified Chloris virgata shed reproductive units in hand and spikelets on attached flowering branch; ciliate hair tufts and paired long awns; loose units are not whole fruits.",
  "caption":"Jim Conrad's original 2024 Mexico photograph shows shed two-awned reproductive UNITS at left and a still-attached spikelet-bearing raceme at right. Persistent narrow glumes remain along the rachis while the florets separate; use the fine white hair tufts and long awns as gross clues. No calibrated ruler and no independently traced fertile-versus-sterile lemma origins.",
  "why":"Teaches how detachable paired florets differ from a bare caryopsis or an entire spikelet, and shows where persistent glumes remain.",
  "markers":[
    {"label":"Shed two-awned floret unit","label_x":3,"label_y":73,"target_x":22,"target_y":62},
    {"label":"Spikelet-bearing branch","label_x":80,"label_y":6,"target_x":83,"target_y":40}
  ],"artist":"Jim Conrad","license":"Public domain — express author release",
  "license_url":PD_GRANT,"source_page":BACKYARD,
  "status":"ORIGINAL AUTHOR IDENTIFIED; no independent dissection, not Hays voucher"
 },
 {
  "source":"https://backyardnature.net/mexnat/qto/chloriv.jpg",
  "file":"jim-conrad-chloris-virgata-two-awn-fertile-sterile-floret.jpg",
  "title":"FLORET MACRO — two awns and distinctive pale hair crown",
  "role":"Real source-described Chloris virgata separated reproductive floret unit with attached second smaller sterile part, dense spreading white marginal hairs and two stiff awns.",
  "caption":"Jim Conrad identifies the larger fertile and attached smaller sterile floret in this true macro. Clearly visible: TWO projecting long awns, a pale seed-enclosing body and a dense spray of white hairlike structures beside its apex. These white hairs agree with the diagnostic fertile-lemma hair crown, but the photograph lacks a ruler and individual awn insertion sites are not independently resolved. Original Mexico specimen, not a Hays voucher.",
  "why":"Real close image of the feather-fingergrass fine-hair character rather than an unresolved distant feathery seedhead.",
  "markers":[
    {"label":"Fine white hair crown","label_x":66,"label_y":77,"target_x":61,"target_y":34},
    {"label":"Long stiff awn","label_x":9,"label_y":9,"target_x":40,"target_y":31}
  ],"artist":"Jim Conrad","license":"Public domain — express author release",
  "license_url":PD_GRANT,"source_page":BACKYARD,
  "status":"SOURCE IDENTIFIED but ruler and isolated lemma attachments unavailable"
 },
 {
  "source":"https://backyardnature.net/mexnat/qto/chloris.jpg",
  "file":"jim-conrad-chloris-virgata-low-rooted-habit.jpg",
  "title":"ROOTED ANNUAL HABIT — stems radiating from shallow crown",
  "role":"Original ground-growing Feather Fingergrass in dry Mexican reservoir with stems spreading outward from rooted central plant",
  "caption":"The original photograph documents the rooting base and repeatedly spreading low culms in a very dry reservoir bed in Querétaro, Mexico. Source identifies this as an annual but annual life cycle is not established by one photo; underground rhizomes are not exposed. Do not use habit alone to distinguish tufted annual from other Chloris.",
  "why":"Adds actual rooting and growth-form context absent from previous floating flowerhead-only photos.",
  "markers":[{"label":"Rooted central base","label_x":8,"label_y":37,"target_x":41,"target_y":50},
             {"label":"Spreading flowering culms","label_x":69,"label_y":12,"target_x":67,"target_y":39}],
  "artist":"Jim Conrad","license":"Public domain — express author release",
  "license_url":PD_GRANT,"source_page":BACKYARD,
  "status":"SOURCE IDENTIFIED regional Mexico habit; root attachment partly obscured in photo"
 }
]
# Verify Commons source rights individually before adding.
file_name="Chloris virgata florets (6774086110).jpg"
query=urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata","titles":"File:"+file_name})
info=next(iter(json.loads(get("https://commons.wikimedia.org/w/api.php?"+query))["query"]["pages"].values()))["imageinfo"][0]
meta=info.get("extmetadata",{})
lic=re.sub(r"[^A-Z0-9]","",meta.get("LicenseShortName",{}).get("value","").upper())
artist=html.unescape(re.sub(r"<[^>]*>"," ",meta.get("Artist",{}).get("value",""))).strip()
description=html.unescape(re.sub(r"<[^>]*>"," ",meta.get("ImageDescription",{}).get("value",""))).strip()
if lic!="CCBY20" or "Harry Rose" not in artist or not re.search(r"(?:2|two)\s+long-awned\s+florets",description,re.I) or not re.search(r"lower\s+lemma",description,re.I):
 raise RuntimeError("Commons fertile floret source/rights mismatch "+lic+" / "+artist+" / "+description[:160])
specs.append({
 "source":info["url"],"source_page":COMMONS,
 "file":"harry-rose-chloris-virgata-two-awn-florets.jpg",
 "title":"FERTILE FLORET HAIR CROWN — two long-awned florets photographed",
 "role":"Harry Rose labelled separated Chloris virgata florets showing two very long awns and fine 2–3mm hairs beside lower fertile lemma apex (length reported by author, not measured from pixels)",
 "caption":"Harry Rose's original Australian source describes TWO long-awned florets and a hairy LOWER fertile lemma apex. The photograph itself shows two broad enclosing structures, two long brown awns and a spray of long fine hairs immediately beside the shared apex. The 2–3 mm length is the photographer's original caption, NOT a photographed ruler measurement; individual awn-to-lemma attachment still not certified.",
 "why":"Direct source-explained reproductive close-up confirming the position of the conspicuous fertile-lemma hair crown, a much more reliable cue than mere head featheriness.",
 "markers":[{"label":"Fine lemma-apex hair crown","label_x":78,"label_y":20,"target_x":60,"target_y":49},
            {"label":"Long awn on left unit","label_x":6,"label_y":13,"target_x":39,"target_y":33},
            {"label":"Second projecting awn","label_x":64,"label_y":4,"target_x":60,"target_y":37}],
 "artist":"Harry Rose (Macleay Grass Man)","license":"CC BY 2.0",
 "license_url":"https://creativecommons.org/licenses/by/2.0/",
 "status":"EXACT COMMONS SOURCE LABEL; ruler and independently separated awn attachments absent"
})
out=[]
for spec in specs:
 try:
  if spec["source"].startswith("https://backyardnature.net/"):
   filename=spec["source"].rsplit("/",1)[-1]
   if filename not in page:raise ValueError("Source name not documented on Jim Conrad's original species page")
  dest=ROOT/"images"/spec["file"]
  # Do not re-download or alter already archived approved assets.
  present=next((x for x in S["images"] if x.get("file")=="images/"+spec["file"]),None)
  pictured=next((x for x in S["visual_comparison"]["items"] if x.get("image_url")==str(dest)),None)
  if dest.exists() and present and pictured:
   out.append({"name":spec["file"],"status":"previously_archived","pixels":present.get("image_dimensions"),"license":spec["license"],"new_arrows":len(spec["markers"])})
   continue
  size,sha=jpg(spec["source"],dest)
  rel="images/"+spec["file"]
  if not any(x.get("file")==rel for x in S["images"]):
   S["images"].append({
    "file":rel,"role":spec["role"],"creator":spec["artist"],"license":spec["license"],
    "license_url":spec["license_url"],"source_page":spec["source_page"],"source_image":spec["source"],
    "photo_status":spec["status"],
    "modifications":"Reencoded RGB JPEG, EXIF removed; browser annotations as separate markup only",
    "image_dimensions":size,"sha256_local":sha,
    "public_reuse":"Original photographer public-domain dedication or Commons CC BY 2.0, credit and source links maintained"
   })
  if not any(x.get("image_url")==str(dest) for x in S["visual_comparison"]["items"]):
   S["visual_comparison"]["items"].insert(4+len(out),{
    "label":spec["title"],"scientific_name":"Chloris virgata",
    "image_url":str(dest),"image_fit":"contain","image_role":spec["role"],
    "caption":spec["caption"],"why_it_matters":spec["why"],
    "creator":spec["artist"],"license":spec["license"],
    "license_url":spec["license_url"],"source_page":spec["source_page"],
    "markers":spec["markers"],
    "photo_status":"Original photo preview reviewed; overlays restricted to gross visibly supported features; no measured lemma/ligule proof; mobile QA pending."
   })
  out.append({"name":spec["file"],"status":"archived","pixels":size,"sha256":sha,"license":spec["license"],"new_arrows":len(spec["markers"])})
 except Exception as exc:
  out.append({"name":spec["file"],"status":"HELD","reason":str(exc)[:240]})
# Public gallery: existing Joey Santore C. verticillata comparison licensed
# CC BY-NC is not cleared as public-reuse under current site-wide CC policy.
for panel in S["visual_comparison"]["items"]:
 if panel.get("scientific_name")=="Chloris verticillata" and "BY-NC" in str(panel.get("license","")):
  panel["image_url"]="content/taxa/Poaceae/Chloris/chloris-verticillata/images/douglas-goldman-verticillata-spikelet-raceme.jpg"
  panel["creator"]="Douglas Goldman"
  panel["license"]="CC BY-SA 4.0";panel["license_url"]="https://creativecommons.org/licenses/by-sa/4.0/"
  panel["source_page"]="https://commons.wikimedia.org/wiki/File:ChlorisV1.jpg"
  panel["image_role"]="OTHER species: actual open-licensed tumble-windmillgrass unilateral awned raceme macro; not C. virgata."
  panel["caption"]="TUMBLE WINDMILLGRASS, NOT FEATHER FINGERGRASS: Douglas Goldman's source-verified CC BY-SA 4.0 macro shows individual awned units along a narrow one-sided branch. Compare with the C. virgata separately source-photographed fluffy long-hair crown; do not infer a species from presence of awns alone."
  panel["photo_status"]="Locally archived rights-cleared source-identified OTHER-species image; original noncommercial source metadata remains in the other species card; no microscope arrow claims."
S["field_id_finish_pass"]["lane5_virgata_reproductive_macros_20261025"]={
 "stage":"FIELD_READY_PHOTO_GAPS",
 "license_sources":[PD_GRANT,COMMONS],
 "archive_results":out,
 "anatomy_accomplished":"Actual loose two-awned floret units, fertile lemma white hair crown in two real macro photographs, source-labelled two-unit morphology, rooted spreading habit.",
 "still_missing":[
  "Same mature voucher at mm scale fully separated fertile lemma and first sterile lemma with each individual awn traced to original insertion",
  "Second sterile reduction verified by separate dissection (if present)",
  "Actual 0.2–1 mm true ciliate membranous ligule with millimeter ruler",
  "Local same-specimen full habit + magnified crown and fertile spikelet sequence",
  "On-page mobile arrows and live Pages rendering verification"],
 "no_false_claims":"Jim Conrad photos from Mexico and Harry Rose from Australia, not Texas Hays vouchers; paper source lengths not photo-derived; retain taxonomy and region holds."
}
CARD.write_text(json.dumps(S,ensure_ascii=False,indent=2)+"\n")
REPORT.write_text(json.dumps(S["field_id_finish_pass"]["lane5_virgata_reproductive_macros_20261025"],indent=2)+"\n")
print(json.dumps({"archive_results":out,"gallery_panels":len(S["visual_comparison"]["items"])}))
