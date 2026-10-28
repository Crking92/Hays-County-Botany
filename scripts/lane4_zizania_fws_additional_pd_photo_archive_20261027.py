#!/usr/bin/env python3
"""USFWS public-domain exact endangered Zizania texana original PHOTO archiver.

No additional reproduction or location-sensitive details; no new arrows until
actual photo pixels reviewed, and no instructions to disturb wild protected plants.
"""
import csv,hashlib,io,json,pathlib,re,time,urllib.parse,urllib.request,urllib.error
from PIL import Image,ImageOps
ROOT=pathlib.Path("content/taxa/Poaceae/Zizania/zizania-texana")
CARD=ROOT/"species.json";SOURCES=ROOT/"image-sources.csv"
PHOTOS=[
 ("20561","usfws-hagerty-20561-official-river-study.jpg","Official 2016 USFWS source photo of Texas wild-rice, reserved for habitat/source verification pending pixel review"),
 ("20576","usfws-hagerty-20576-reproductive-study.jpg","Official 2016 USFWS source photo of Texas wild-rice, potential flowering-sex detail pending actual pixel review"),
 ("20578","usfws-hagerty-20578-reproductive-study.jpg","Official 2016 USFWS source photo of Texas wild-rice, potential sex-separated flowering structure pending actual pixel review")
]
def grab(url,size=18_000_000):
 exc=None
 for attempt in range(4):
  try:
   request=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 (USFWS public domain metadata, original species-only noncontact field education; github.com/Crking92/Hays-County-Botany)","Accept":"application/json,image/jpeg,*/*;q=0.8"})
   with urllib.request.urlopen(request,timeout=55) as response:
    payload=response.read(size+1)
   if len(payload)>size:raise ValueError("oversize")
   return payload
  except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as e:
   exc=e
   if isinstance(e,urllib.error.HTTPError) and e.code not in [429,500,502,503,504]:raise
   time.sleep(attempt+2)
 raise RuntimeError(str(exc))
def clean(s):
 return re.sub(r"[^a-z0-9]","",re.sub("<[^>]*>","",s or "").lower())
def main():
 d=json.loads(CARD.read_text(encoding="utf-8"))
 assert d["id"]=="zizania-texana"
 with SOURCES.open(newline="",encoding="utf-8") as f:
  reader=csv.DictReader(f);headers=reader.fieldnames;old=list(reader)
 assert headers
 new=[];held=[];rows=[]
 for id,filename,role in PHOTOS:
  path=ROOT/"images"/filename
  if any(i.get("file")=="images/"+filename for i in d["images"]):continue
  title="Zizania texana (Texas wild rice) FWS "+id+".jpg"
  query=urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata|size|sha1","iiurlwidth":1900,"titles":"File:"+title})
  source="https://commons.wikimedia.org/wiki/File:"+urllib.parse.quote(title.replace(" ","_"),safe="()-.")
  try:
   j=json.loads(grab("https://commons.wikimedia.org/w/api.php?"+query,4_000_000))
   page=next(iter(j["query"]["pages"].values()))
   assert page.get("title","").casefold()==("File:"+title).casefold(),("Page title mismatch",page.get("title"),title)
   meta=page["imageinfo"][0];right=meta.get("extmetadata",{})
   license_label=right.get("LicenseShortName",{}).get("value","")
   artist=right.get("Artist",{}).get("value","")
   author_re=re.sub("<[^>]*>"," ",artist)
   assert ("publicdomain" in clean(license_label) or clean(license_label)=="pd"),("Individual license unsupported",license_label)
   assert "Hagerty" in author_re or "FWS" in author_re or "Hagerty" in str(right.get("Credit",{})),("Wrong original federal author",artist)
   assert meta["width"]>=3000 and meta["height"]>=2400,("Small original file not expected",meta["width"],meta["height"])
   url=meta.get("thumburl") or meta["url"]
   host=urllib.parse.urlparse(url).hostname
   assert host and (host=="upload.wikimedia.org" or host.endswith(".wikimedia.org"))
   raw=grab(url,12_000_000)
   im=Image.open(io.BytesIO(raw));im.verify()
   photo=ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
   assert min(photo.size)>=1000 and max(photo.size)<=2500,("Thumbnail size unexpected",photo.size)
   path.parent.mkdir(exist_ok=True,parents=True)
   photo.save(path,"JPEG",quality=89,optimize=True)
   binary=path.read_bytes()
   saved=Image.open(io.BytesIO(binary))
   assert saved.size==photo.size and not saved.getexif() and not saved.info.get("exif")
   assert binary[:2]==b"\xff\xd8" and binary[-2:]==b"\xff\xd9"
   rec={"file":"images/"+filename,"role":role,
    "creator":"Ryan Hagerty / U.S. Fish and Wildlife Service","license":"Public domain — original U.S. federal government employee photograph",
    "source_page":source,"source_file_sha1":meta.get("sha1"),
    "source_taxon":"Zizania texana","source_locality":"San Marcos River conservation photo series (precise protected stand coordinate NOT recorded).",
    "modifications":"Uncropped resized source JPEG to max 1900px, EXIF/GPS stripped. No synthesized anatomy, no in-pixel arrows.",
    "photo_status":"Original Commons file is exact species and USFWS author, individual original work explicitly PUBLIC DOMAIN; bytes verified. Human PHOTO PIXEL/REPRODUCTIVE SEX audit pending; do not imply authorized crew plant manipulation.",
    "public_reuse":"USFWS U.S.-government public-domain photo, source and credit documented, no collection activity encouraged.",
    "source_original_url":meta["url"],"archived_sha256":hashlib.sha256(binary).hexdigest(),
    "archived_dimensions":list(photo.size)}
   d["images"].append(rec)
   # Provisional gallery panels pending photo morphology audit; no arrows yet.
   d["visual_comparison"]["items"].append({
    "label":"USFWS Z. texana source-verified study "+id+" — anatomy pending",
    "scientific_name":"Zizania texana","image_url":(ROOT/"images"/filename).as_posix(),
    "image_fit":"contain","image_role":role,
    "caption":"Actual USFWS Texas wild-rice photo by Ryan Hagerty. "+role+". Public domain original. No new male/female branch identification, root or ligule claimed without direct pixel review. PROTECTED SPECIES: observe from safe authorized positions; DO NOT handle or collect.",
    "why_it_matters":"Actual authoritative source species and public-domain photo; cannot claim hidden ligule, root, precise female awn or touching.",
    "creator":"Ryan Hagerty / U.S. Fish and Wildlife Service","license":"Public domain","source_page":source,
    "modifications":rec["modifications"],
    "photo_status":"Rights, source and archived original JPEG verified, visual anatomy audit still needed; do not increment photo role yet.",
    "markers":[]})
   rows.append({"file_name":filename,"role":role,"creator":rec["creator"],"license":"Public domain","source_page":source,
    "direct_url":meta["url"],"study_use":"Noncontact endangered species field education","public_reuse":"Original U.S. Federal USFWS public domain, credited source"})
   new.append({"photo":"FWS "+id,"file":rec["file"],"source":source,"license_label":license_label,
    "creator":author_re[:190],"sha256":hashlib.sha256(binary).hexdigest(),
    "dimensions":list(photo.size),"bytes":len(binary)})
   print("ARCHIVED",id,photo.size,flush=True)
  except Exception as e:
   held.append({"file":title,"reason":repr(e)[:500]})
   print("HELD",id,repr(e)[:250],flush=True)
 if new:
  d["curation_status"]["photo_metadata_count"]=len(d["images"])
  d["curation_status"]["photo_files_present"]=len(d["images"])
  d["field_id_finish_pass"]["lane4_20261027_additional_USFWS_photo_archive"]={
   "new_source_photos":len(new),"photo_roles_gained":0,"new_arrows":0,
   "source":"Commons original federal Hagerty USFWS files, per-file public domain rights verified",
   "pixels":"Original photo human anatomy review pending.",
   "protected_species_knowledge":"Never disturb wild plants, never divulge precise stands, USFWS collection permitted to qualified professionals only.",
   "public_pages":"No live deployment confirmed from this archiver."}
  d["visual_comparison"]["overlay_note"]+="\n2026-10-27: archived additional exact-species Hagerty USFWS public-domain source photos. Do NOT use new source photos to assert male/female or rooted/ligule microanatomy before actual saved-pixel review; do not alter endangered plant noncontact instructions."
  CARD.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
  with SOURCES.open("w",newline="",encoding="utf-8") as f:
   writer=csv.DictWriter(f,fieldnames=headers,extrasaction="ignore");writer.writeheader();writer.writerows(old+rows)
 report={"taxon":"Zizania texana","new":new,"held":held,"safety_hold":"No collection, touching, entering protected stand or revealing sensitive coordinate; historic existing research photos allowed with proper source rights."}
 p=pathlib.Path("reports/lane4-zizania-extra-fws-public-domain-20261027.json");p.parent.mkdir(exist_ok=True)
 p.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({"archived_count":len(new),"held_count":len(held)}),flush=True)
if __name__=="__main__": main()
