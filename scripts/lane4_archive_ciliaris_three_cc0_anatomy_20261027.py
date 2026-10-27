#!/usr/bin/env python3
"""Archive verified CC0, observed-exact-species Digitaria ciliaris images.

The iNaturalist observation is 'needs_id' and images are NOT botanist-vouchered.
No microscopic organ identity or arrow until exact pixels inspected afterwards.
"""
import pathlib,json,urllib.request,urllib.parse,time,io,hashlib,re
from PIL import Image,ImageOps
BASE=pathlib.Path("content/taxa/Poaceae/Digitaria/digitaria-ciliaris")
CARD=BASE/"species.json"
OBS_ID=261099989
PHOTO_SPECS=[
 (469014500,"inat-hrosenswdpi-469014500-ligule-region.jpg","True ligule and exterior sheath junction CANDIDATE (needs opened-membrane pixel review)"),
 (469014483,"inat-hrosenswdpi-469014483-collar-sheath.jpg","Leaf sheath/collar hair distribution CANDIDATE (needs exact inner ligule pixel review)"),
 (469014510,"inat-hrosenswdpi-469014510-hidden-glume.jpg","Opposite or hidden spikelet face with upper-glume contrast CANDIDATE (needs glume margin pixel review)")
]
def get(u):
 error=None
 for attempt in range(4):
  try:
   req=urllib.request.Request(u,headers={"User-Agent":"HaysBotanyLane4/1.0 botanical-educational CC0 source audit"})
   with urllib.request.urlopen(req,timeout=60) as f:
    blob=f.read(13_000_001)
   if len(blob)>13_000_000:raise ValueError("max 13MB")
   return blob
  except Exception as e:
   error=e;time.sleep(4*(attempt+1))
 raise RuntimeError(repr(error))
def main():
 card=json.loads(CARD.read_text())
 assert card["id"]=="digitaria-ciliaris"
 query="https://api.inaturalist.org/v1/observations/"+str(OBS_ID)
 obj=json.loads(get(query));rows=obj.get("results",[])
 assert len(rows)==1,"exact observation not returned"
 obs=rows[0]
 tax=obs.get("taxon") or {}
 assert tax.get("id")==76657 and tax.get("name")=="Digitaria ciliaris",(tax, "Wrong source taxon!")
 assert (obs.get("user") or {}).get("login")=="hrosenswdpi","Unexpected original uploader"
 assert obs.get("quality_grade")=="needs_id","Quality changed: independently re-audit source species"
 candidate={p.get("id"):p for p in obs.get("photos",[])}
 assert all(n in candidate for n,_,_ in PHOTO_SPECS),"At least one candidate photo no longer in exact obs"
 for n,_,_ in PHOTO_SPECS:
  assert candidate[n].get("license_code","").lower()=="cc0",(n,candidate[n].get("license_code"))
 installed=[]
 for n,filename,role in PHOTO_SPECS:
  photo=candidate[n];u=photo.get("url","")
  assert u.startswith("https://") and "inaturalist-open-data.s3.amazonaws.com" in u,u
  u=re.sub(r"/(square|small|medium|large|thumb)\.", "/large.",u)
  raw=get(u)
  assert raw[:2]==b"\xff\xd8",(n,"source must be JPEG")
  im=Image.open(io.BytesIO(raw));im.verify()
  im=ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
  assert min(im.size)>=600 and im.width<=6500 and im.height<=6500,(n,im.size)
  out=BASE/"images"/filename
  out.parent.mkdir(parents=True,exist_ok=True)
  im.save(out,"JPEG",quality=92,optimize=True)
  archive=out.read_bytes()
  check=Image.open(io.BytesIO(archive))
  assert check.size==im.size and not check.getexif()
  rel="images/"+filename
  source="https://inaturalist.ala.org.au/photos/"+str(n)
  meta={
   "file":rel,"role":role,"creator":"hrosenswdpi (iNaturalist source observer, photo marked no rights reserved)",
   "license":"CC0 1.0","license_url":"https://creativecommons.org/publicdomain/zero/1.0/",
   "source_page":source,"source_observation":"https://www.inaturalist.org/observations/"+str(OBS_ID),
   "source_photo_id":str(n),"source_observation_taxon":"Digitaria ciliaris","source_observation_taxon_id":76657,
   "source_observation_quality_grade":"needs_id",
   "photo_license_source_code":"cc0","public_reuse":"Image-level public domain CC0 confirmed. Credit original source observer and source URL.",
   "photo_status":"Physical original licensed photo, exact observed-source taxon D. ciliaris, observation needs_id. Diagnostic anatomy subject matter NOT yet inspected. No measured ligule, hidden glume or anatomy arrow is approved solely by caption.",
   "modifications":"Re-encoded uncropped RGB JPEG and stripped metadata/EXIF. No pixel annotations.",
   "archive_sha256":hashlib.sha256(archive).hexdigest(),"image_dimensions":list(im.size)
  }
  found=next((x for x in card["images"] if x.get("source_photo_id")==str(n) or x.get("file")==rel),None)
  if found is None:card["images"].append(meta)
  else:found.update(meta)
  gal=card.setdefault("visual_comparison",{}).setdefault("items",[])
  if not any(str(x.get("source_photo_id"))==str(n) or x.get("source_page")==source for x in gal):
   gal.append({
    "label":role,"scientific_name":"Digitaria ciliaris","image_url":(BASE/rel).as_posix(),
    "image_fit":"contain","image_role":"SOURCE-PROVISIONAL: "+role,
    "caption":"Photographed by iNaturalist observer hrosenswdpi in a photo of source-labeled D. ciliaris, observation 261099989 (currently needs ID). The linked botanist's post teaches collar/sheath and hidden upper glume distinctions. Photo-level CC0 is verified, but exact visible part labels and scale are held until pixel review.",
    "why_it_matters":"Aboveground structure photo candidate; do not mistake hairs adjacent to the blade for a verified true free ligule membrane.",
    "creator":meta["creator"],"license":"CC0 1.0","license_url":meta["license_url"],
    "source_page":source,"source_photo_id":str(n),"markers":[],
    "photo_status":"Original physically present and licensed public domain, source taxon exact but needs_id; unresolved anatomy label and 1mm measurement, pending full-pixel human review."
   })
  installed.append({"id":n,"file":rel,"source":source,"size":list(im.size),"archive_sha256":meta["archive_sha256"]})
  print("ARCHIVED",n,rel,im.size,flush=True)
 assert len(installed)==3 and len(card["images"])>=8
 card["curation_status"]["photo_metadata_count"]=len(card["images"])
 card["curation_status"]["photo_files_present"]=sum((BASE/x["file"]).is_file() for x in card["images"] if x.get("file","").startswith("images/"))
 card["learner_visual_status"]["image_count"]=sum(x.get("file","").startswith("images/") for x in card["images"])
 card["field_id_finish_pass"]["lane4_ciliaris_cc0_collar_archive_20261027"]={
  "stage":"FIELD_READY_PHOTO_GAPS","new_photos":installed,
  "source_observation":query,"source_grade":"needs_id, so source determined not voucher independently verified",
  "source_license":"All 3 individual photos CC0 as recorded by iNaturalist v1 observation 261099989",
  "new_annotations":0,"pixel_anatomy_review":"PENDING","new_true_ligule_character_cleared":False,
  "root_priority":"Later: collar/ligule and upper glume first","live_pages_QA":"UNVERIFIED"
 }
 CARD.write_text(json.dumps(card,ensure_ascii=False,indent=2)+"\n")
 print("DONE 3 real CC0 source photos; total",len(card["images"]),"image records,",len(card["visual_comparison"]["items"]),"panels",flush=True)
if __name__=="__main__":main()
