#!/usr/bin/env python3
"""Strict original CC Digitaria cognata actual leaf collar photographic archiver.

A candidate alone cannot establish true ~0.5 mm erose membranous ligule:
confirm actual inside sheath in SOURCE PIXELS independently before adding arrows.
"""
import csv,hashlib,io,json,pathlib,time,urllib.parse,urllib.request,urllib.error
from PIL import Image,ImageOps
ROOT=pathlib.Path("content/taxa/Poaceae/Digitaria/digitaria-cognata")
CARD=ROOT/"species.json";SOURCES=ROOT/"image-sources.csv"
CANDIDATES=[
 (746801460,406472426,"virginia-leaf-sheath-close","True source-labelled grass photographed close at leaf-sheath junction; whether the actual free inner ligule is exposed must be inspected."),
 (746801441,406472426,"virginia-basal-leaf-sheaths","Several upright slender leaf sheaths and lower green shoot bases, source species shown; true ligule and root mechanism unresolved."),
 (745183717,405676644,"georgia-leaf-joint-view","Actual living Digitaria cognata green culm leaf blade-sheath joint; interior ligule not independently proven."),
 (659273697,361255585,"texas-leaf-junction","Source research-grade Clay County Texas narrow blade base and stem joint, potential membranous ligule target for pixel review.")
]
def fetch(url,cap=11_000_000):
 error=None
 for n in range(4):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 (exact source CC-by source taxon proof; github.com/Crking92/Hays-County-Botany)","Accept":"application/json,image/jpeg,*/*;q=0.8"})
   with urllib.request.urlopen(req,timeout=45) as f:b=f.read(cap+1)
   if len(b)>cap:raise ValueError("photo too large")
   return b
  except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as e:
   error=e
   if isinstance(e,urllib.error.HTTPError) and e.code not in (429,500,502,503,504):raise
   time.sleep(n+2)
 raise RuntimeError(str(error))
def main():
 d=json.loads(CARD.read_text(encoding="utf-8"));assert d["id"]=="digitaria-cognata"
 check={}
 for _,oid,_,_ in CANDIDATES:
  if oid in check:continue
  response=json.loads(fetch("https://api.inaturalist.org/v1/observations/"+str(oid),8_000_000))
  obs=response["results"][0]
  assert obs.get("taxon",{}).get("name")=="Digitaria cognata",(oid,obs.get("taxon"))
  assert obs.get("quality_grade")=="research",(oid,"not research grade")
  check[oid]=obs
 with SOURCES.open("r",newline="",encoding="utf-8") as f:
  rows=list(csv.DictReader(f));fields=list(rows[0].keys()) if rows else list(csv.DictReader(f).fieldnames or [])
 assert fields
 installed=[];held=[];extra=[]
 for pid,oid,slug,role in CANDIDATES:
  rel=f"images/inat-cc-{pid}-{slug}.jpg"
  if any(i.get("file")==rel for i in d["images"]):continue
  try:
   o=check[oid]
   ph=next((p for p in o["photos"] if p["id"]==pid),None)
   assert ph is not None
   lic=ph.get("license_code")
   assert lic in ("cc0","cc-by","cc-by-sa"),"individual photo not public"
   at=ph.get("attribution")
   assert at,"creator absent"
   url=ph.get("url")
   assert urllib.parse.urlparse(url).hostname in ("static.inaturalist.org","inaturalist-open-data.s3.amazonaws.com","inaturalist.s3.amazonaws.com")
   large=url.replace("/square.","/large.") if "/square." in url else url
   raw=fetch(large,9_000_000)
   source=Image.open(io.BytesIO(raw));source.verify()
   pic=ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
   assert min(pic.size)>=600,"Source lacks useful pixel resolution"
   path=ROOT/rel;path.parent.mkdir(exist_ok=True,parents=True)
   pic.save(path,"JPEG",quality=91,optimize=True)
   b=path.read_bytes();filecheck=Image.open(io.BytesIO(b))
   assert filecheck.size==pic.size and not filecheck.getexif() and not filecheck.info.get("exif")
   assert b[:2]==b"\xff\xd8" and b[-2:]==b"\xff\xd9"
   license={"cc0":"CC0","cc-by":"CC BY","cc-by-sa":"CC BY-SA"}[lic]
   sp=f"https://www.inaturalist.org/photos/{pid}"
   obsurl=f"https://www.inaturalist.org/observations/{oid}"
   rec={"file":rel,"role":role,"creator":at,"license":license,
     "license_version_note":"Individual photo API CC code verified, exact license version not asserted.",
     "source_page":sp,"source_observation":obsurl,"source_taxon":"Digitaria cognata",
     "source_quality_grade":"research","source_locality":o.get("place_guess"),
     "public_reuse":"Per-photo Creative Commons author/license and source credit; preserve adaptation note; no restricted ND or NC material.",
     "modifications":"Proportional large original re-encoded JPEG RGB and EXIF/GPS stripped.",
     "photo_status":"Original CC source and JPEG bytes VERIFIED; anatomical inner 0.5mm free membrane NOT yet independently pixel certified.",
     "photo_id":pid,"archive_sha256":hashlib.sha256(b).hexdigest(),"archived_dimensions":list(pic.size)}
   d["images"].append(rec)
   d["visual_comparison"]["items"].append({"label":"PROVISIONAL SOURCE VERIFIED — "+slug.replace("-"," ").upper(),
     "scientific_name":"Digitaria cognata","image_url":(ROOT/rel).as_posix(),"image_fit":"contain",
     "image_role":role,"caption":"Actual research-grade source-labelled Digitaria cognata photo by "+at+" ("+str(o.get("place_guess"))+"). "+role+" Original individual photo "+license+"; inside 0.5mm ligule not assumed.",
     "why_it_matters":"Original actual licensed source species collar candidate, no generic other-taxon substitution.",
     "creator":at,"license":license,"source_page":sp,
     "modifications":rec["modifications"],"photo_status":"Original archive source, CC rights and pixel integrity proven, true inner membrane/measurements unverified.",
     "markers":[]})
   extra.append({"file_name":path.name,"role":role,"creator":at,"license":license,"source_page":sp,"direct_url":large,
     "study_use":"Public education with CC source credit","public_reuse":"Each original CC BY/CC0 iNaturalist photo with attribution, link, no EXIF/GPS",
     "observation_id":oid,"photo_id":pid})
   installed.append({"pid":pid,"obs":oid,"file":rel,"source":sp,"license":license,"creator":at,"dims":list(pic.size),"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)})
   print("SAVED CC EXACT",pid,lic,pic.size,flush=True)
  except Exception as e:
   held.append({"id":pid,"reason":str(e)[:350]})
   print("HELD",pid,str(e)[:250],flush=True)
 if installed:
  d["curation_status"]["photo_metadata_count"]=len(d["images"])
  d["curation_status"]["photo_files_present"]=len(d["images"])
  d["field_id_finish_pass"]["lane4_cognata_real_cc_collar_archive_20261027"]={
    "exact_source_photo_bytes_new":len(installed),"photo_pixels_organ_review_pending":True,
    "scientific_scope":"taxon research-grade exact species, no Hays County voucher native conclusion",
    "ligule":"Do not score true 0.5mm erose inner membrane from metadata or external hairs",
    "new_arrows":0,"photo_role_gain":0}
  d["visual_comparison"]["overlay_note"]+="\n2026-10-27: Four exact research-grade Digitaria cognata individual-public-CC photograph originals physically archived with source, creator and EXIF-free JPEG. Physical blade/sheath free membrane remains an anatomy hold pending direct pixel inspection; no unverified arrows."
  CARD.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
  with SOURCES.open("w",newline="",encoding="utf-8") as f:
   wr=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore");wr.writeheader();wr.writerows(rows+extra)
 rep=pathlib.Path("reports/lane4-cognata-true-collar-cc-photo-archive-20261027.json")
 rep.parent.mkdir(exist_ok=True)
 rep.write_text(json.dumps({"species":"Digitaria cognata","new_public_cc_photos":installed,"held":held,"new_anatomy_role_credit":0,"label":"Photo source and rights archived; actual organism pixels must be reviewed."},indent=2)+"\n",encoding="utf-8")
 print(json.dumps({"new_count":len(installed),"held":held}),flush=True)
if __name__=="__main__":main()
