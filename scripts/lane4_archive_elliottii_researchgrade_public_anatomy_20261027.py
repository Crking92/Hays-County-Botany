#!/usr/bin/env python3
"""Source- and rights-guarded REAL Sorghastrum elliottii photos; preserve Hays range/ID hold.

All selected records must be original current iNaturalist *research-grade*
exact Sorghastrum elliottii with individual image CC0/CC BY rights.
No source metadata alone proves basal growth, awn length, ligule or Texas range.
Only append provisional photos; review original pixels before arrow or role score.
"""
import csv,hashlib,io,json,pathlib,time,urllib.parse,urllib.request,urllib.error
from PIL import Image,ImageOps
ROOT=pathlib.Path("content/taxa/Poaceae/Sorghastrum/sorghastrum-elliottii")
CARD=ROOT/"species.json";SRC=ROOT/"image-sources.csv"
SELECT=[
 (585848393,323745624,"virginia-long-awn-physical-ruler","True detached mature-looking awns and source centimeter graduated metal ruler; count exact bends/length only after pixel check"),
 (585848432,323745624,"virginia-leaf-collar-first","Actual leaf/sheath collar close-up with source photographer finger; check whether inside ligule membrane itself is shown"),
 (585848445,323745624,"virginia-inner-collar-second","Second photographed source-confirmed collar and green leaf junction, visible narrow ligule extension to check"),
 (745927492,406039275,"virginia-ripe-spikelets-mm-ruler","Real S. elliottii spikelets and awns placed against a physical numbered millimeter ruler; no isolated glume/lemma from source alone"),
 (745927408,406039275,"virginia-collar-awn-attachment","One narrow grass leaf blade meeting stem sheath on research-grade same-observation specimen; may display true ligule/collar after photo pixel review"),
 (700397097,382713379,"florida-whole-field-habit-cc0","Photographer CC0 image of species growing in typical flatwoods with leaves/flowering panicles; exact same rooted crown not exposed"),
 (582983609,322280762,"southcarolina-basal-live-plant-cc0","Live green basal shoots and leaves photographed in situ; roots/rhizome mechanism below soil not exposed")
]
def get(url,limit=11000000):
 error=None
 for n in range(4):
  try:
   q=urllib.request.Request(url,headers={"User-Agent":"Hays-County-Botany/1.0 (public CC source audited field photo atlas; github.com/Crking92/Hays-County-Botany)","Accept":"application/json,image/jpeg,*/*;q=0.8"})
   with urllib.request.urlopen(q,timeout=50) as rs:b=rs.read(limit+1)
   if len(b)>limit:raise ValueError("Source too large")
   return b
  except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as e:
   error=e
   if isinstance(e,urllib.error.HTTPError) and e.code not in (429,500,502,503,504):raise
   time.sleep(n+2)
 raise RuntimeError(str(error))
def main():
 d=json.loads(CARD.read_text(encoding="utf-8"))
 assert d["id"]=="sorghastrum-elliottii"
 os={}
 for _,oid,_,_ in SELECT:
  if oid in os:continue
  result=json.loads(get("https://api.inaturalist.org/v1/observations/"+str(oid),7_000_000))
  o=result["results"][0]
  assert o["taxon"]["name"]=="Sorghastrum elliottii",(oid,o["taxon"]["name"])
  assert o.get("quality_grade")=="research",(oid,o.get("quality_grade"))
  os[oid]=o
 with SRC.open(newline="",encoding="utf-8") as f:
  reader=csv.DictReader(f);hdr=reader.fieldnames;old=list(reader)
 assert hdr is not None
 added=[];held=[];rows=[]
 for pid,oid,tag,role in SELECT:
  fname=f"images/inat-public-{pid}-{tag}.jpg"
  if any(x.get("file")==fname for x in d["images"]):continue
  try:
   o=os[oid];photo=next((p for p in o.get("photos",[]) if p.get("id")==pid),None)
   assert photo,"Not member of validated observation"
   lic=photo.get("license_code")
   assert lic in {"cc0","cc-by","cc-by-sa"},"Not public-photo-rights eligible"
   credit=photo.get("attribution") or ("No rights reserved (CC0)" if lic=="cc0" else "")
   assert credit,"Missing public photographer rights attribution"
   sourceurl=photo.get("url")
   host=urllib.parse.urlparse(sourceurl).hostname
   assert host in {"inaturalist-open-data.s3.amazonaws.com","static.inaturalist.org","inaturalist.s3.amazonaws.com"}
   large=sourceurl.replace("/square.","/large.") if "/square." in sourceurl else sourceurl
   raw=get(large)
   check=Image.open(io.BytesIO(raw));check.verify()
   image=ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
   assert min(image.size)>=440
   path=ROOT/fname;path.parent.mkdir(parents=True,exist_ok=True)
   image.save(path,"JPEG",quality=91,optimize=True)
   binary=path.read_bytes();saved=Image.open(io.BytesIO(binary))
   assert saved.size==image.size and not saved.getexif() and "exif" not in saved.info
   assert binary[:2]==b"\xff\xd8" and binary[-2:]==b"\xff\xd9"
   license={"cc0":"CC0","cc-by":"CC BY","cc-by-sa":"CC BY-SA"}[lic]
   url=f"https://www.inaturalist.org/photos/{pid}"
   locality=(o.get("place_guess") or "")[:160]
   record={"file":fname,"role":role,
    "creator":credit,"license":license,
    "license_version_note":"Original individual iNaturalist photo license code verified per observation photo record; CC license version not presumed.",
    "source_page":url,"source_observation":f"https://www.inaturalist.org/observations/{oid}",
    "source_taxon":"Sorghastrum elliottii","photo_locality":locality,"source_quality_grade":"research",
    "public_reuse":"Photo by source photographer, individual CC0/CC BY/CC BY-SA source license conditions and source URL preserved.",
    "photo_status":"Current original photo/license/taxon observed exact-source research grade, but original pixel anatomy, regional voucher/rights review and fine-structure arrows still provisional. Protected Sorghastrum elliottii Hays county range hold NOT resolved.",
    "modifications":"Uncropped proportional original large photo re-encoded JPEG RGB without original EXIF/GPS.",
    "photo_id":pid,"archive_sha256":hashlib.sha256(binary).hexdigest(),"archived_dimensions":list(image.size)}
   d["images"].append(record)
   d["visual_comparison"]["items"].append({
    "label":"REAL SOURCE PHOTO — "+tag.replace("-"," ").upper(),
    "scientific_name":"Sorghastrum elliottii","image_url":(ROOT/fname).as_posix(),"image_fit":"contain",
    "image_role":role,"caption":"Source-determined research-grade Sorghastrum elliottii photo in "+locality+". "+role+". Source "+credit+"; photo license "+license+". No independent Hays native voucher or species-macro anatomy proof from metadata.",
    "why_it_matters":"Genuine source taxon photograph available under individual CC rights; anatomy only proven after direct saved-pixel review.",
    "creator":credit,"license":license,"source_page":url,
    "modifications":record["modifications"],"photo_status":"True photograph CC source verified; NOT INDEPENDENTLY ANATOMY-ID CLEARED, no microscopic arrows and photo-score increase until original visual review.",
    "markers":[]})
   rows.append({"file_name":path.name,"role":role,"creator":credit,"license":license,"source_page":url,
     "direct_url":large,"study_use":"Public learner if separately photo/organs reviewed","public_reuse":"Preserve author and individual CC photo license; EXIF removed","modifications":record["modifications"],
     "license_url":"https://creativecommons.org/publicdomain/zero/1.0/" if lic=="cc0" else "https://creativecommons.org/licenses/by/"})
   added.append({"id":pid,"file":fname,"license":license,"creator":credit,"locality":locality,"obs":oid,"dimensions":list(image.size),"sha256":hashlib.sha256(binary).hexdigest(),"bytes":len(binary)})
   print("ARCHIVED",pid,license,flush=True)
  except Exception as e:
   held.append({"id":pid,"reason":str(e)[:400]});print("HELD",pid,repr(e),flush=True)
 if added:
  d["curation_status"]["photo_metadata_count"]=len(d["images"])
  d["curation_status"]["photo_files_present"]=len(d["images"])
  d["field_id_finish_pass"]["lane4_elliottii_exact_photo_candidates_20261027"]={
   "photos_added":len(added),"arrows_added":0,"photo_score_gain":0,
   "photo_specific_license":"Only each CC0 or CC BY source verified against current individual photo record, research-grade exact Sorghastrum elliottii taxon",
   "scientific_hold":"County native evidence and independent species ID/voucher still unresolved; no hidden anatomy invented",
   "status":"True source photos physically stored, final organ pixel inspection and site QA pending"}
  d["visual_comparison"]["overlay_note"]+="\n2026-10-27: source-licensed research-grade exact *Sorghastrum elliottii* photographic set expanded. Existing source-ID and regional occurrence range HOLD remains. Photographed macro roles still provisional until actual JPG pixel exam; other species S. nutans comparator photos correctly separate.";
  CARD.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
  with SRC.open("w",newline="",encoding="utf-8") as f:
   w=csv.DictWriter(f,fieldnames=hdr,extrasaction="ignore");w.writeheader();w.writerows(old+rows)
 report={"taxon":"Sorghastrum elliottii","date":"2026-10-27","actual_photo_additions":added,"held":held,"range_hold":"PRESERVED; imagery alone does not authorize Hays county native or voucher conclusion.","anatomy_score":"No role until actual source pixels inspected"}
 path=pathlib.Path("reports/lane4-elliottii-licensed-photo-archive-20261027.json")
 path.parent.mkdir(exist_ok=True);path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print(json.dumps({"added_count":len(added),"held_count":len(held)}),flush=True)
if __name__=="__main__": main()
