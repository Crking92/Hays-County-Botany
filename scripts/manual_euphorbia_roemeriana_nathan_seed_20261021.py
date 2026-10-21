#!/usr/bin/env python3
"""Exact observation from Nathan Taylor's 2019 iNaturalist seed morphology journal.

Source observation 22577311; images 34980028 and 34980021 are labelled as
Euphorbia roemeriana SEEDS in the article. Individual media license must be
verified from the LIVE iNaturalist API before file download and publication.
"""
from pathlib import Path
from PIL import Image, ImageOps
from io import BytesIO
import requests, json, hashlib, re
BASE=Path("content/taxa/Euphorbiaceae/Euphorbia/euphorbia-roemeriana")
CARD=BASE/"species.json"
REPORT=Path("reports/euphorbia-roemeriana-nathan-seed-source-20261021.json")
SOURCE_OBS=22577311
SEED_IDS={34980028,34980021}
ALLOWED={
"cc0":("CC0 1.0","https://creativecommons.org/publicdomain/zero/1.0/"),
"cc-by":("CC BY 4.0","https://creativecommons.org/licenses/by/4.0/"),
"cc-by-sa":("CC BY-SA 4.0","https://creativecommons.org/licenses/by-sa/4.0/"),
"cc-by-nc":("CC BY-NC 4.0","https://creativecommons.org/licenses/by-nc/4.0/"),
"cc-by-nc-sa":("CC BY-NC-SA 4.0","https://creativecommons.org/licenses/by-nc-sa/4.0/")
}
def run():
 j=json.loads(CARD.read_text(encoding="utf-8"))
 assert j["scientific_name"]=="Euphorbia roemeriana"
 assert 5<=len(j["images"])<=7
 if any(x["file"].startswith("images/nathan-roemeriana-seed-") for x in j["images"]):
  print("Seed photo files already canonical; idempotent no-op");return
 ss=requests.Session()
 ss.headers["User-Agent"]="HaysCountyBotanyEducationalPhotoVerifier/1.0 (https://github.com/Crking92/Hays-County-Botany)"
 resp=ss.get("https://api.inaturalist.org/v1/observations/"+str(SOURCE_OBS),timeout=45)
 resp.raise_for_status()
 arr=resp.json().get("results") or []
 assert len(arr)==1,("Exact source observation missing",SOURCE_OBS)
 obs=arr[0]
 assert obs.get("taxon",{}).get("name")=="Euphorbia roemeriana",obs.get("taxon",{})
 report={"obs_id":SOURCE_OBS,"taxon":obs["taxon"]["name"],"source_journal":"https://www.inaturalist.org/projects/euphorbia-species-of-the-united-states/journal",
  "photo_candidates":[],"downloaded_photo_count":0,"copyright_rule":"Only exact individually CC licensed media eligible for a genuinely noncommercial educational website.","microscopic_arrows":"Pending genuine photo inspection"}
 new=[]
 for ph in obs.get("photos") or []:
  if ph.get("id") not in SEED_IDS:continue
  code=(ph.get("license_code") or "").lower()
  entry={"photo_id":ph["id"],"photo_license_code":code,"accepted":False}
  report["photo_candidates"].append(entry)
  if code not in ALLOWED:
   entry["reason"]="Photo-specific license not permitted, no download/public use"
   continue
  creator=ph.get("attribution") or ""
  if not creator.strip():
   entry["reason"]="Creator credit absent";continue
  photo_url=ph.get("url") or ""
  if not photo_url.startswith("https://"):
   entry["reason"]="Invalid source URL";continue
  url=re.sub(r"/(?:square|small|medium|large|thumb)\.", "/original.",photo_url)
  binary=None
  for u in [url,re.sub(r"/original\.", "/large.",url)]:
   try:
    res=ss.get(u,timeout=50);res.raise_for_status()
    data=res.content
    if not 12000<len(data)<14000000:continue
    with Image.open(BytesIO(data)) as raw:
     raw.load()
     if min(raw.size)<400:continue
     im=ImageOps.exif_transpose(raw).convert("RGB")
     source_dims=list(raw.size)
    im.thumbnail((1800,1800),Image.Resampling.LANCZOS)
    out=BytesIO(); im.save(out,format="JPEG",quality=91,optimize=True)
    binary=out.getvalue()
    with Image.open(BytesIO(binary)) as check:check.verify()
    break
   except Exception as exc:
    entry["last_retry_error"]=str(exc)[:130]
  if binary is None:
   entry["reason"]="Unable to verify original image bytes";continue
  filename="images/nathan-roemeriana-seed-"+str(ph["id"])+".jpg"
  lic,licurl=ALLOWED[code]
  record={"file":filename,"role":"Exact-species detached seed reference from Nathan Taylor's advanced seed morphology comparison; anatomy details pending manual saved JPEG check",
   "creator":creator,"license":lic,"license_url":licurl,"source_page":"https://www.inaturalist.org/photos/"+str(ph["id"]),
   "source_platform":"iNaturalist, direct observation 22577311 linked in Nathan Taylor's 2019 Euphorbia seed journal","observation_url":"https://www.inaturalist.org/observations/"+str(SOURCE_OBS),
   "photo_id":ph["id"],"observation_id":SOURCE_OBS,"study_use":"yes","public_reuse":"yes",
   "public_site_use_scope":"noncommercial-only" if "-nc" in code else "Creative Commons by license",
   "photo_review":"Exact species source observation and individual photo licensing checked, real image downloaded and validated. Actual individual pitted seed/caruncle arrows PENDING manual visual examination.",
   "anatomy_arrows":[],"source_sha256":hashlib.sha256(data).hexdigest(),"image_dimensions":list(im.size),"original_dimensions":source_dims}
  new.append((filename,binary,record))
  entry.update({"accepted":True,"creator":creator,"license":lic,"file":filename})
 assert len(new)<=2
 if new:
  for name,data,record in new:
   target=BASE/name;assert not target.exists()
   target.write_bytes(data)
   j["images"].append(record)
  j["learner_visual_status"]["image_count"]=len(j["images"])
  j["learner_visual_status"]["note"]="Existing roemeriana field lesson plus "+str(len(new))+" exact-source seed photos from Nathan Taylor's morphology journal; seed surface and caruncle require manual saved JPEG inspection before claims."
  j["field_id_finalization"]["seed_photo_source_status"]="Photo binaries downloaded and rights-verified; individual anatomy arrows not yet manually placed."
  j["curation_status"]["photo_metadata_count"]=len(j["images"])
  j["curation_status"]["photo_files_present"]=len(j["images"])
  CARD.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 report["downloaded_photo_count"]=len(new)
 REPORT.parent.mkdir(parents=True,exist_ok=True)
 REPORT.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
 print("Downloaded",len(new),"individually licensed exact-species seed images. Original card sources preserved.")
if __name__=="__main__":run()
