#!/usr/bin/env python3
"""Archive Jim Conrad's public-domain Texas Chloris cucullata macro photographs.
Public-domain grant: https://www.backyardnature.net/j/copyrite.htm
Exact species page: https://www.backyardnature.net/n/h/windmill.htm
Photo anatomy annotated only at visible gross structure/pixel locations.
"""
import hashlib, io, json, pathlib, re, time, urllib.request, urllib.error
from PIL import Image
P=pathlib.Path("content/taxa/Poaceae/Chloris/chloris-cucullata/species.json")
S=json.loads(P.read_text())
RESULT={"taxon":"Chloris cucullata","photos":[],"errors":[]}
PAGE="https://www.backyardnature.net/n/h/windmill.htm"
GRANT="https://www.backyardnature.net/j/copyrite.htm"
BASE="https://www.backyardnature.net/n/13/"
def get(url):
 req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; HaysBotanyEdu/1.0; licensed botanical archive)", "Accept":"text/html,image/jpeg,*/*"})
 for attempt in range(4):
  try:
   with urllib.request.urlopen(req,timeout=40) as resp:return resp.read()
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503) or attempt==3:raise
   time.sleep(2*(attempt+1))
page=get(PAGE).decode("utf-8","replace")
grant=get(GRANT).decode("utf-8","replace")
assert re.search(r"Chloris\s+cucullata",page,re.I),"Species-page identity hold"
assert "Jim Conrad" in page,"Original photographer page author not proven"
assert re.search(r"PUBLIC\s+DOMAIN\s+all\s+images\s+produced\s+by\s+myself",re.sub(r"<[^>]+>"," ",grant),re.I),"Author's public-domain grant not confirmed"
specs=[
 {"filename":"131103cn.jpg","dest":"jim-conrad-texas-hooded-spikelet-ciliate-margins.jpg",
  "label":"TEXAS CLOSE-UP — two genuine hairy spikelets (Frio Canyon)",
  "role":"Source-labelled same-species 2013 Uvalde two mature spikelets showing prominent hairs along visible scales; rounded sterile lemma attribution NOT microdissected",
  "caption":"Actual Jim Conrad photograph from northern Uvalde County, Texas. Two intact spikelet units reveal dense translucent white marginal hairs and projecting fine points on the bracts. The source identifies this taxon as hooded windmillgrass. While the broad inflated-looking bracts are visible, we cannot identify an individual upper STERILE hood, separate glumes, or prove an awn's exact origin in this undissected close-up. No metric ruler.",
  "why":"Strong actual macro of hair-bearing exact-species reproductive units, replacing inference from a distant head.",
  "markers":[{"label":"White ciliate margins","label_x":5,"label_y":12,"target_x":29,"target_y":42},{"label":"Intact spikelet (left)","label_x":3,"label_y":83,"target_x":24,"target_y":65}]},
 {"filename":"131103cm.jpg","dest":"jim-conrad-texas-hooded-one-sided-spikelets.jpg",
  "label":"TEXAS HEAD DETAIL — crowded one-sided real spikelet rows",
  "role":"Actual Texas mounted mature flowering racemes, clearly repeated compact one-sided spikelets on branch",
  "caption":"Source-identified real flowering head from northern Uvalde County. Tight spikelet rows crowd the actual racemes around their common hub. No claim that any green unit on the head exposes a separate glume or sterile lemma; species ID still benefits from the adjacent close-up.",
  "why":"Shows how true intact spikelets are arranged along the short flowering branches in the same locality as the reproductive macro.",
  "markers":[{"label":"One-sided spikelet row","label_x":4,"label_y":11,"target_x":29,"target_y":24},{"label":"Raceme attachment hub","label_x":69,"label_y":69,"target_x":49,"target_y":44}]},
 {"filename":"131103co.jpg","dest":"jim-conrad-texas-hooded-dark-mature-grains.jpg",
  "label":"TEXAS MATURE HEAD — dark grains emerging from glumes",
  "role":"Actual source-determined ripened spikelet row showing dark swollen exposed ripe grains between pale glume/lemma bracts",
  "caption":"Real Texas Chloris cucullata seed-bearing raceme, photographed by Jim Conrad. Mature dark, shiny caryopses visibly protrude between widely opened pale scales. White/pale pointed structures are not individually dissected or measured; don't label them as confirmed sterile hood, fertile lemma or glume just from this photograph.",
  "why":"Shows what fruiting spikelets look like, separate from an immature windmill head; a meaningful actual reproductive detail.",
  "markers":[{"label":"Exposed dark ripe grains","label_x":64,"label_y":83,"target_x":57,"target_y":70},{"label":"Spikelets aligned on rachis","label_x":3,"label_y":14,"target_x":35,"target_y":41}]},
]
archive_count=0
for spec in specs:
 try:
  if spec["filename"] not in page:raise ValueError("Image filename absent from authenticated photographer's species page")
  url=BASE+spec["filename"]
  raw=get(url)
  im=Image.open(io.BytesIO(raw));im.verify()
  im=Image.open(io.BytesIO(raw)).convert("RGB")
  if min(im.size)<350:raise ValueError("Image below 350px minimum")
  dest=P.parent/"images"/spec["dest"]
  im.save(dest,"JPEG",quality=92,optimize=True)
  rel="images/"+spec["dest"]
  if not any(x.get("file")==rel for x in S["images"]):
   S["images"].append({"file":rel,"role":spec["role"],"creator":"Jim Conrad","license":"Public domain — express photographer dedication","source_page":PAGE,"source_image":url,"permission_page":GRANT,"public_reuse":"Jim Conrad's express public-domain release of photographs personally produced for Backyard Nature. Proper source/creator credited.","location":"Dry Frio River valley, northern Uvalde County, Texas; source 2013 newsletter","photo_status":"ACTUAL SOURCE-IDENTIFIED TEXAS PHOTO; original pixels examined for visible structure only; no independent dissected lemma voucher","archived_dimensions":list(im.size),"sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),"modifications":"JPEG RGB reencode; no added burned-in markings, EXIF/GPS removed"})
  localpath=str(dest)
  if not any(x.get("image_url")==localpath for x in S["visual_comparison"]["items"]):
   S["visual_comparison"]["items"].insert(3+archive_count,{"label":spec["label"],"scientific_name":"Chloris cucullata","image_url":localpath,"image_fit":"contain","image_role":spec["role"],"caption":spec["caption"],"why_it_matters":spec["why"],"creator":"Jim Conrad","license":"Public domain — author release","source_page":PAGE,"source_image":url,"permission_page":GRANT,"markers":spec["markers"],"photo_status":"Texas Uvalde 2013 original viewed, diagnostic gross/hair/caryopsis arrows checked against real photo; still no individually measured glumes, hood or ligule."})
  archive_count+=1
  RESULT["photos"].append({"source":url,"local_file":localpath,"pixels":list(im.size),"license":"Public domain","status":"archived"})
 except Exception as exc:
  RESULT["photos"].append({"source":BASE+spec["filename"],"status":"HELD","reason":str(exc)[:240]})
# Do not display an NC-only comparison in the public gallery when a species-matched
# locally archived Commons CC BY-SA photograph is available.
for item in S["visual_comparison"]["items"]:
 if item.get("scientific_name")=="Chloris verticillata" and "BY-NC" in str(item.get("license","")):
  item["image_url"]="content/taxa/Poaceae/Chloris/chloris-verticillata/images/commons-chloris-verticillata-87b04d3bcaff.jpg"
  item["creator"]="Matt Lavin";item["license"]="CC BY-SA 2.0";item["license_url"]="https://creativecommons.org/licenses/by-sa/2.0/"
  item["source_page"]="https://commons.wikimedia.org/wiki/File:Chloris_verticillata_-_windmillgrass_-_51679981311.jpg"
  item["caption"]="OTHER species: authenticated locally archived tumble windmillgrass shows its long radiating racemes. The prior Joey Santore CC BY-NC media record is preserved in its source card, but is no longer this public comparison panel. Head habit alone cannot establish parentage or hybrid identity."
  item["photo_status"]="Licensed species-matched locally archived CC BY-SA replacement for former noncommercial comparison; no new microanatomy arrows."
S["field_id_finish_pass"]["lane5_public_domain_texas_macros_20261025"]={
 "status":"FIELD_READY_PHOTO_GAPS","archived_count":archive_count,"photos":RESULT["photos"],"license_basis":GRANT,
 "diagnostic_new_roles":"Texas source identified ciliate spikelet close-up, ripe exposed caryopses, crowded actual one-sided racemes",
 "still_missing":["Truly detached 1–1.5mm upper sterile lemma shown in two views and metric scale","Fully separated individually identified glumes and fertile lemma with short awn attachment","True measured 0.7–1mm ciliate membrane at inner ligule/collar","Rooted specimen with all anatomical stages tied to same voucher","Mobile on-page arrow alignment and live deployed site QA"],
 "anatomy_boundary":"Conrad photos verify gross hairs and dark mature fruits, NOT independently dissected upper sterile hood."
}
P.write_text(json.dumps(S,indent=2,ensure_ascii=False)+"\n")
pathlib.Path("reports/lane5-hooded-windmillgrass-conrad-macros-20261025.json").write_text(json.dumps(RESULT,indent=2)+"\n")
print(json.dumps(RESULT))
