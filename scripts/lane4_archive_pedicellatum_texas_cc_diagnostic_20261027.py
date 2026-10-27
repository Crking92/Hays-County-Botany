#!/usr/bin/env python3
"""Archive individually CC-licensed exact D. pedicellatum Texas organ photos.

Photo identification: source observation MUST currently be research-grade, EXACT
Dichanthelium pedicellatum, source photo record CC0/CC BY/CC BY-SA.
Do NOT grant anatomical score nor unverified arrows from metadata alone.
"""
import csv,hashlib,io,json,pathlib,time,urllib.request,urllib.parse,urllib.error
from PIL import Image,ImageOps
ROOT=pathlib.Path("content/taxa/Poaceae/Dichanthelium/dichanthelium-pedicellatum")
CARD=ROOT/"species.json";SOURCES=ROOT/"image-sources.csv"
SELECTION=[
(367178078,207571258,"garner-leaf-sheath-macro","true external blade/sheath attachment and visible hairs; inside ligule must be judged separately"),
(269595287,155937516,"central-texas-collar","photographed real narrow leaf blade and stem sheath junction, possible hair placement"),
(269595387,155937516,"central-texas-spikelet-macro","actual source-labelled green oval spikelet on narrow threadlike pedicel; no dissected glume"),
(272971502,157909667,"texas-magnified-spikelets","several attached small spikelets viewed beside a handheld magnifier; magnification is NOT physical mm scale"),
(396643818,223834467,"pedernales-basal-sheaths","real in-situ sheath and live perennial-looking shoots among dry leaf litter; roots remain hidden"),
(636924738,349172886,"glen-rose-plant-habit","source documented real leafy plant growing among rocks; roots not photographed"),
(367177996,207571258,"garner-narrow-leaves","attached narrow leaf blades held by source photographer; collar and inflorescence not enough for mm-scored details"),
(272971387,157909667,"texas-spikelet-pair","detached actual source-identified oval green spikelets on small pedicels, no clear inner florets")
]
def get(url,limit=12_000_000):
 error=None
 for i in range(4):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotanyFieldLearner/1.0 (CC diagnostic photographs; github.com/Crking92/Hays-County-Botany)","Accept":"application/json,image/jpeg,*/*;q=0.7"})
   with urllib.request.urlopen(req,timeout=45) as resp: data=resp.read(limit+1)
   if len(data)>limit:raise ValueError("image too large")
   return data
  except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as e:
   error=e
   if isinstance(e,urllib.error.HTTPError) and e.code not in (429,500,502,503,504):raise
   time.sleep(2+i)
 raise RuntimeError(str(error))
def obs(id):
 raw=get("https://api.inaturalist.org/v1/observations/"+str(id),8_000_000)
 return json.loads(raw)["results"][0]
def main():
 d=json.loads(CARD.read_text(encoding="utf-8"))
 assert d["id"]=="dichanthelium-pedicellatum"
 cached={}
 for _,oid,_,_ in SELECTION:
  if oid not in cached:
   cached[oid]=obs(oid)
   x=cached[oid]
   assert x.get("taxon",{}).get("name")=="Dichanthelium pedicellatum",(oid,"wrong source taxon",x.get("taxon",{}))
   assert x.get("quality_grade")=="research",(oid,"not research grade")
 with SOURCES.open(newline="",encoding="utf-8") as f:
  reader=csv.DictReader(f);headers=reader.fieldnames;old=list(reader)
 assert headers is not None
 added=[];held=[];newrows=[]
 for pid,oid,suffix,role in SELECTION:
  file=f"images/texas-cc-{pid}-{suffix}.jpg"
  if any(i.get("file")==file for i in d["images"]):continue
  try:
   o=cached[oid];ph=next((a for a in o["photos"] if a["id"]==pid),None)
   assert ph is not None,"photo not present in verified observation"
   lic=ph.get("license_code")
   assert lic in ("cc0","cc-by","cc-by-sa"),"photo-level restricted rights"
   maker=ph.get("attribution","")
   assert maker and "some rights reserved" in maker.lower(),"Need attributable source"
   url=ph["url"];name=urllib.parse.urlparse(url).hostname
   assert name in ("inaturalist-open-data.s3.amazonaws.com","static.inaturalist.org","inaturalist.s3.amazonaws.com"),f"Non-iNat source {name}"
   large=url.replace("/square.","/large.") if "/square." in url else url
   raw=get(large,9_000_000)
   img=Image.open(io.BytesIO(raw));img.verify()
   pic=ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
   assert min(pic.size)>=480
   path=ROOT/file;path.parent.mkdir(exist_ok=True,parents=True)
   pic.save(path,"JPEG",quality=91,optimize=True)
   data=path.read_bytes();chk=Image.open(io.BytesIO(data))
   assert chk.size==pic.size and data[:2]==b"\xff\xd8" and data[-2:]==b"\xff\xd9"
   assert not chk.getexif() and "exif" not in chk.info
   license={"cc0":"CC0","cc-by":"CC BY","cc-by-sa":"CC BY-SA"}[lic]
   source=f"https://www.inaturalist.org/photos/{pid}"
   observation=f"https://www.inaturalist.org/observations/{oid}"
   place=(o.get("place_guess") or "")[:160]
   credit={
     "file":file,"role":role,"creator":maker,"license":license,
     "license_version_note":"Exact individual iNaturalist image CC code verified by observation-photo API; no source version inferred.",
     "source_page":source,"source_observation":observation,"source_taxon_name":"Dichanthelium pedicellatum",
     "source_quality_grade":"research","photo_locality":place,
     "public_reuse":"CC BY or CC0 on original individual source image. Reuse requires photo creator, link, license, and processing disclosure.",
     "modifications":"Source large image proportional RGB JPEG recompressed with EXIF/GPS removed; no crop or generated anatomical content.",
     "photo_status":"Archive bytes and original source photo-level CC rights verified. Anatomic structure and arrow positions provisional until saved pixels independently inspected.",
     "photo_id":pid,"archive_sha256":hashlib.sha256(data).hexdigest(),"archived_dimensions":list(pic.size)}
   d["images"].append(credit)
   d["visual_comparison"]["items"].append({
     "label":"SOURCE VERIFIED — "+suffix.replace("-"," ").upper(),
     "scientific_name":"Dichanthelium pedicellatum","image_url":(ROOT/file).as_posix(),
     "image_fit":"contain","image_role":role,
     "caption":"Genuine source-determined pedicellate panicgrass photographed by "+maker+" in "+place+". "+role+". True inner ligule, tiny corm and individually separate glumes remain unconfirmed until organ pixel review.",
     "why_it_matters":"Correct photographer and research-grade source make real photo potentially useful, never assume microscopic anatomy or county nativity.",
     "creator":maker,"license":license,"source_page":source,
     "photo_status":"PHYSICALLY ARCHIVED source rights verified; visual-organ arrows and scoring pending.",
     "modifications":credit["modifications"],"markers":[]})
   newrows.append({"file_name":path.name,"role":role,"creator":maker,"license":license,"source_page":source,"direct_url":large,"study_use":"Public field learner original licensed source with attribution","public_reuse":"Individual photo CC BY/CC0, original source and RGB EXIF removal documented","observation_id":oid,"photo_id":pid})
   added.append({"id":pid,"file":file,"by":maker,"license":license,"obs":oid,"dims":list(pic.size),"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()})
   print("ARCHIVED",pid,place,pic.size,flush=True)
  except Exception as e:
   held.append({"id":pid,"reason":str(e)[:350]})
   print("HELD",pid,str(e)[:250],flush=True)
 if added:
  d["curation_status"]["photo_metadata_count"]=len(d["images"])
  d["curation_status"]["photo_files_present"]=len(d["images"])
  d["learner_visual_status"]["image_count"]=len(d["images"])
  d["field_id_finish_pass"]["lane4_pedicellatum_texas_cc_real_photo_archive_20261027"]={
    "new_real_exact_species_photo_files":len(added),"new_anatomic_arrows":0,"score_gain":0,
    "license":"Verified exact individual photo public-use CC0/CC BY/CC BY-SA, versions unconfirmed; all sources research-grade D. pedicellatum original photos from Texas.",
    "status":"EXACT PHOTOS ARCHIVED, pixel/role audit required; do not invent true ciliate ligule."}
  d["visual_comparison"]["overlay_note"]+="\n2026-10-27: physically archived Texas exact-source research grade D. pedicellatum original CC BY photos. Real ligule 0.25-0.5mm cannot be established from generic outside collar. No scientific role or accurate arrows until pixels inspected. Existing Harms photos remain original credited educational-use only (not CC) and should not be presumed freely publishable."
  CARD.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
  with SOURCES.open("w",newline="",encoding="utf-8") as f:
   w=csv.DictWriter(f,fieldnames=headers,extrasaction="ignore")
   w.writeheader();w.writerows(old+newrows)
 report={"species":"Dichanthelium pedicellatum","date":"2026-10-27","new_photos":added,"held":held,
    "note":"No scored anatomy role until original archived pixels independently inspected. Public page publishing gated by source photo rights."}
 p=pathlib.Path("reports/lane4-pedicellatum-texas-cc-photo-archive-20261027.json")
 p.parent.mkdir(exist_ok=True);p.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print(json.dumps({"count":len(added),"held":held},indent=2),flush=True)
if __name__=="__main__":main()
