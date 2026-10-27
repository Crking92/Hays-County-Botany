#!/usr/bin/env python3
"""Archive actual species-specific CC BY-SA4 Paspalum dilatatum reproductive photos.

These are Croatian photographer-identified Paspalum dilatatum sensu Rottensteiner,
not Texas/BONAP or subspecies voucher evidence. Individual glumes and lemmas
cannot be asserted until we inspect local original photo pixels.
"""
import pathlib,urllib.parse,urllib.request,urllib.error,json,io,hashlib,re,time
from PIL import Image,ImageOps
BASE=pathlib.Path("content/taxa/Poaceae/Paspalum/paspalum-dilatatum")
CARD=BASE/"species.json"
API="https://commons.wikimedia.org/w/api.php"
L="https://creativecommons.org/licenses/by-sa/4.0/"
SOURCE=[("10","stefan-lefnaer-sl10-flowering-spikelets.jpg","Real closeup of flowering branch and attached P. dilatatum spikelets"),("11","stefan-lefnaer-sl11-spikelet-detail.jpg","Photographer's isolated reproductive close-up, role pending pixel review"),("12","stefan-lefnaer-sl12-spikelet-plate.jpg","Photographer's multiangle spikelet plate, precise glume and lemma assessment pending pixel review")]
def req(url,limit=13000000):
 err=None
 for k in range(4):
  try:
   r=urllib.request.Request(url,headers={"User-Agent":"Hays-Botany-Lane4/1.0 (licensed botanical field-ID education source verification)"})
   with urllib.request.urlopen(r,timeout=65) as x:z=x.read(limit+1)
   if len(z)>limit:raise ValueError("source exceeds max allowed 13mb")
   return z
  except (urllib.error.URLError,urllib.error.HTTPError,TimeoutError) as e:
   err=e
   if isinstance(e,urllib.error.HTTPError) and e.code not in (429,500,502,503,504):raise
   time.sleep((k+1)*4)
 raise RuntimeError(repr(err))
def source(n):
 title=f"File:Paspalum dilatatum sl{n}.jpg"
 q=urllib.parse.urlencode({"action":"query","prop":"imageinfo","iiprop":"url|extmetadata|size|sha1","iiurlwidth":3000,"titles":title,"format":"json"})
 j=json.loads(req(API+"?"+q,2000000));p=next(iter(j["query"]["pages"].values()))
 assert "missing" not in p and "Paspalum dilatatum" in p["title"],p
 inf=p["imageinfo"][0];meta=inf.get("extmetadata",{})
 lic=re.sub("[^a-z0-9.]","",meta.get("LicenseShortName",{}).get("value","").lower())
 artist=meta.get("Artist",{}).get("value","").lower()
 assert lic in ("ccbysa4.0","ccbysa40"),(n,"license mismatch",lic)
 assert "stefan.lefnaer" in artist,(n,"creator",artist[:200])
 assert int(inf.get("width",0))>=1900 and int(inf.get("height",0))>=1100,(n,"dimensions")
 url=inf.get("thumburl") or inf.get("url")
 assert "wikimedia.org" in url,(n,"non commons media")
 return inf,url
def main():
 d=json.loads(CARD.read_text());assert d["id"]=="paspalum-dilatatum"
 assert len(d["images"])>=5 and len(d["visual_comparison"]["items"])>=6
 new=[]
 for n,filename,role in SOURCE:
  url=f"https://commons.wikimedia.org/wiki/File:Paspalum_dilatatum_sl{n}.jpg"
  try:
   inf,src=source(n);raw=req(src)
   assert raw[:2]==b"\xff\xd8",(n,"not real JPEG")
   image=Image.open(io.BytesIO(raw));image.verify()
   image=ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
   assert image.width>=950 and image.height>=700,(n,"too small",image.size)
   dest=BASE/"images"/filename;dest.parent.mkdir(exist_ok=True,parents=True)
   image.save(dest,"JPEG",quality=91,optimize=True)
   blob=dest.read_bytes();im=Image.open(io.BytesIO(blob))
   assert im.size==image.size and not im.getexif() and "exif" not in im.info
   rel="images/"+filename
   rec={"file":rel,"role":role,"creator":"Stefan.lefnaer","license":"CC BY-SA 4.0","license_url":L,
    "source_page":url,"source_taxon_concept":"Paspalum dilatatum sensu Rottensteiner, Croatia; no local Texas taxon proof",
    "source_original_sha1":inf.get("sha1"),"archived_dimensions":list(image.size),
    "archive_sha256":hashlib.sha256(blob).hexdigest(),
    "modifications":"Uncropped proportional Commons thumbnail or original re-encoded JPEG RGB; source labels unchanged; EXIF/GPS stripped.",
    "public_reuse":"Source-specific CC BY-SA 4.0; preserve author, source link, license and adaptation note; edited-photo ShareAlike.",
    "photo_status":"Exact source license and taxon verified; REAL local JPEG physically archived, diagnostic microstructures not claimed until separate original pixel verification."}
   match=next((x for x in d["images"] if x.get("file")==rel or x.get("source_page")==url),None)
   if match:match.update(rec)
   else:d["images"].append(rec)
   items=d["visual_comparison"]["items"]
   if not any(x.get("source_page")==url for x in items):
    items.append({"label":"TRUE *Paspalum dilatatum* reproductive photo sl"+n+" — precise morphology review pending",
      "scientific_name":"Paspalum dilatatum",
      "image_url":(BASE/rel).as_posix(),"image_fit":"contain",
      "image_role":role,"caption":"Exact species photographed by Stefan.lefnaer on Krk, Croatia. Real reproductive original physically hosted here under CC BY-SA 4.0. Inspect pixels before deciding which glume, lemma, palea or reproductive scale is present; no Texas taxonomic voucher inferred.",
      "why_it_matters":"Potential missing precise reproductive comparison versus Paspalum urvillei; no presumed microanatomy.",
      "creator":"Stefan.lefnaer","license":"CC BY-SA 4.0","license_url":L,"source_page":url,
      "modifications":rec["modifications"],"markers":[],
      "photo_status":"Author/taxon/photo CC BY-SA4 checked, exact byte physically stored; detailed anatomical role and arrows still require human visual review."})
   new.append({"source":url,"file":rel,"dimensions":list(image.size),"sha256":rec["archive_sha256"]})
   print("INSTALLED",n,rel,image.size,flush=True)
  except Exception as e:print("HELD",n,repr(e),flush=True)
 if not new:raise RuntimeError("No verified photos could be installed; leave species card untouched.")
 local=[x for x in d["images"] if x.get("file","").startswith("images/")]
 assert all((BASE/x["file"]).is_file() for x in local)
 d["curation_status"]["photo_metadata_count"]=len(d["images"])
 d["curation_status"]["photo_files_present"]=len(local)
 d["learner_visual_status"]["image_count"]=len(local)
 d["field_id_finish_pass"]["lane4_dallis_reproductive_archive_20261027"]={
  "stage":"FIELD_READY_PHOTO_GAPS","new_licensed_photos_physically_archived":new,
  "rights":"Stefan.lefnaer each Commons photo licensed CC BY-SA4; prior Joey CC BY-NC untouched.",
  "pixel_anatomy_certification":"PENDING; must not count glumes/lemmas by filename.",
  "missing":["source-cleared full individual root+head","verified 1-mm detached glume/sterile-fertile lemma/macros","same-scale vaseygrass compare","Pages live/mobile QA"],
  "new_arrows":0,"public_site_verified":False}
 CARD.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
 print("ARCHIVE RESULT",len(new),"files; total panels",len(d["visual_comparison"]["items"]),flush=True)
if __name__=="__main__":main()
