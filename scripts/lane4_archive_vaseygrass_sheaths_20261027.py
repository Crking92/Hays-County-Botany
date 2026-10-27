#!/usr/bin/env python3
"""Archive exact photographed Paspalum urvillei anatomy from original CC Wikimedia files.
No fine/true ligule labeling until local pixels are separately reviewed.
"""
import pathlib,json,urllib.parse,urllib.request,urllib.error,re,time,hashlib,io
from PIL import Image,ImageOps
BASE=pathlib.Path("content/taxa/Poaceae/Paspalum/paspalum-urvillei")
CARD=BASE/"species.json"
API="https://commons.wikimedia.org/w/api.php"
SOURCES=[
 ("leaf sheath1","7391817130","harry-rose-vasey-leaf-sheath1.jpg","True leaf/sheath exterior and blade base; actual inner free ligule requires pixel inspection"),
 ("leaf sheath2","7391814972","harry-rose-vasey-leaf-sheath2.jpg","Additional true collar/sheath macro; distinguish hair placements"),
 ("leaf sheath3","7398277156","harry-rose-vasey-leaf-sheath3.jpg","Third true collar/sheath view, source-authenticated; inspect membrane from inner side"),
 ("plant1","7391791236","harry-rose-vasey-whole-plant1.jpg","Photographer-authenticated larger Vaseygrass plant growth and leaf base"),
 ("habit1","7391812884","harry-rose-vasey-habit1.jpg","Original author Vaseygrass whole tuft and full flowering plant habit"),
 ("node1","7391784488","harry-rose-vasey-node1.jpg","Real culm node and projecting hairs; DO NOT infer roots or ligule from node")
]
LICS={"ccby2.0":("CC BY 2.0","https://creativecommons.org/licenses/by/2.0/"),
      "ccby4.0":("CC BY 4.0","https://creativecommons.org/licenses/by/4.0/"),
      "ccbysa4.0":("CC BY-SA 4.0","https://creativecommons.org/licenses/by-sa/4.0/")}
def get(url,limit=13000000):
 err=None
 for i in range(4):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 licensed photographic education source audit"})
   with urllib.request.urlopen(req,timeout=65) as f:b=f.read(limit+1)
   if len(b)>limit:raise ValueError("Image >13MB bound")
   return b
  except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as e:
   err=e
   if isinstance(e,urllib.error.HTTPError) and e.code not in (429,500,502,503,504):raise
   time.sleep(3*(i+1))
 raise RuntimeError(repr(err))
def individual_source(topic,photo_id):
 title=f"File:Paspalum urvillei {topic} ({photo_id}).jpg"
 q=urllib.parse.urlencode({"action":"query","titles":title,"prop":"imageinfo","iiprop":"url|extmetadata|size|sha1","iiurlwidth":1920,"format":"json"})
 j=json.loads(get(API+"?"+q,2000000))
 page=next(iter(j["query"]["pages"].values()))
 assert "missing" not in page,(photo_id,"Commons page absent")
 assert page.get("title","").casefold()==title.casefold(),(photo_id,page.get("title"))
 info=page["imageinfo"][0];meta=info.get("extmetadata",{})
 lic=re.sub(r"[^a-z0-9.]","",meta.get("LicenseShortName",{}).get("value","").lower())
 artist=(meta.get("Artist",{}).get("value","")+" "+meta.get("Credit",{}).get("value","")).lower()
 assert lic in LICS,(photo_id,"license not approved",lic)
 assert "harry rose" in artist or "macleay grass man" in artist,(photo_id,"creator mismatch",artist[:160])
 assert int(info.get("width",0))>=1000,(photo_id,"not full resolution")
 img=info.get("thumburl") or info.get("url")
 assert img and "wikimedia.org" in img,(photo_id,"bad thumbnail URL")
 return title,info,img,LICS[lic]
def main():
 d=json.loads(CARD.read_text())
 assert d["id"]=="paspalum-urvillei"
 assert len(d["images"])>=3 and len(d["visual_comparison"]["items"])>=6
 new=[];held=[]
 for topic,pid,filename,role in SOURCES:
  source=f"https://commons.wikimedia.org/wiki/File:Paspalum_urvillei_{topic.replace(' ','_')}_({pid}).jpg"
  try:
   title,inf,url,(label,licurl)=individual_source(topic,pid)
   raw=get(url);assert raw[:2]==b"\xff\xd8",(pid,"non-JPEG")
   photo=Image.open(io.BytesIO(raw));photo.verify()
   photo=ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
   assert photo.width>=600 and photo.height>=500,(pid,photo.size)
   target=BASE/"images"/filename;target.parent.mkdir(parents=True,exist_ok=True)
   photo.save(target,"JPEG",quality=91,optimize=True)
   saved=target.read_bytes();assert saved[:2]==b"\xff\xd8" and saved[-2:]==b"\xff\xd9"
   clean=Image.open(io.BytesIO(saved));assert clean.size==photo.size and not clean.getexif() and "exif" not in clean.info
   rel="images/"+filename
   rec={"file":rel,"role":role,"creator":"Harry Rose (Macleay Grass Man)",
     "license":label,"license_url":licurl,"source_page":source,
     "source_original_sha1":inf.get("sha1"),"archived_dimensions":list(photo.size),
     "archive_sha256":hashlib.sha256(saved).hexdigest(),
     "public_reuse":f"Individual file {label} verified on Commons; photographer, source and adaptation notice required.",
     "modifications":"Uncropped proportional Wikimedia thumbnail resized and re-encoded RGB JPEG; EXIF/GPS removed; no new arrows.",
     "photo_status":"Individual photo copyright and exact source taxon verified; physically locally archived original; precise anatomical feature remains unverified until full pixel review. No local Hays voucher inferred."}
   prior=next((x for x in d["images"] if x.get("source_page")==source or x.get("file")==rel),None)
   if prior:prior.update(rec)
   else:d["images"].append(rec)
   gallery=d["visual_comparison"]["items"]
   found=next((x for x in gallery if x.get("source_page")==source),None)
   if found:
    found["image_url"]=(BASE/rel).as_posix()
    found["license"]=label;found["license_url"]=licurl;found["creator"]="Harry Rose (Macleay Grass Man)"
    found["photo_status"]="Original same photo now physically archived and linked locally. Existing labels/arrows preserved; anatomical pixel review not yet completed."
   else:
    gallery.append({"label":f"Vaseygrass {topic}: photographed same-species anatomical candidate",
      "scientific_name":"Paspalum urvillei","image_url":(BASE/rel).as_posix(),"image_fit":"contain",
      "image_role":role,"caption":f"Actual *Paspalum urvillei* source-original photographed by Harry Rose. Authenticated photographic source; true free INNER ligule, roots and precise mm characters must be assessed from image pixels, not this photo title.",
      "why_it_matters":"Species-specific attached collar, sheath or growth evidence candidate; not another generic flowering head.","creator":"Harry Rose (Macleay Grass Man)",
      "license":label,"license_url":licurl,"source_page":source,"modifications":rec["modifications"],"markers":[],
      "photo_status":"Individually verified Commons photograph, now hosted in same GitHub repository. Pixel review pending."})
   new.append({"source_photo_id":pid,"file":rel,"license":label,"sha256":rec["archive_sha256"],"pixels":list(photo.size)})
   print("INSTALLED",pid,filename,photo.size,label,flush=True)
  except Exception as e:
   held.append({"id":pid,"reason":repr(e)})
   print("HELD",pid,repr(e),flush=True)
 if not new:raise RuntimeError("No rights-verified photo bytes installed; no card edited")
 assert all((BASE/x["file"]).is_file() for x in d["images"] if x.get("file","").startswith("images/"))
 d["curation_status"]["photo_metadata_count"]=len(d["images"])
 d["curation_status"]["photo_files_present"]=sum(x.get("file","").startswith("images/") for x in d["images"])
 d["learner_visual_status"]["image_count"]=len(d["images"])
 d["field_id_finish_pass"]["lane4_vasey_aboveground_cc_archive_20261027"]={
 "new_species_photo_files":new,"held":held,"new_arrows":0,
 "photo_source":"Harry Rose individually CC licensed source, South West Rocks Australia, no Texas voucher",
 "diagnostic_anatomy_roles":"PENDING independent actual pixel review; no free ligule inferred yet",
 "source_compare":"existing 3 source Harry Rose files retained, two earlier external panels now locally linked when source matches",
 "release_checks":"Individual source CC verified. Pages mobile and arrow QA unverified."}
 CARD.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
 print("DONE",len(new),"new local species files;",len(d["images"]),"species image records and",len(d["visual_comparison"]["items"]),"gallery panels")
if __name__=="__main__":main()
