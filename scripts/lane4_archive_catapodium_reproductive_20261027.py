#!/usr/bin/env python3
"""Rights-checked photographic macro sources for exact Catapodium rigidum.

Never use a source image of the wrong subspecies. Archive only exact CC BY-SA4
Stefan.lefnaer Commons originals or proportional thumbnails. Individual structure
annotations are withheld until actual archived pixels have been inspected.
"""
import json,io,pathlib,urllib.request,urllib.parse,urllib.error,time,hashlib,re
from PIL import Image,ImageOps
BASE=pathlib.Path("content/taxa/Poaceae/Catapodium/catapodium-rigidum")
CARD=BASE/"species.json"
API="https://commons.wikimedia.org/w/api.php"
LICENSE="https://creativecommons.org/licenses/by-sa/4.0/"
SPECS=[
 ("17","stefan-lefnaer-sl17-reproductive-a.jpg","Species-labelled reproductive detail, actual spikes/spikelets; check pixels for glume and lemma anatomy"),
 ("26","stefan-lefnaer-sl26-spikelet-plate.jpg","Wide source botanical plate of mature reproductive units, candidate real glumes and florets with scale"),
 ("28","stefan-lefnaer-sl28-floret-plate.jpg","Wide source specimen multi-view plate, candidate dissected reproductive units with visible source labels")
]
def fetch(u,max_bytes=15000000):
 err=None
 for k in range(4):
  try:
   req=urllib.request.Request(u,headers={"User-Agent":"Hays-County-Botany-Lane4/1.0 (exact-source CC botanical study)"})
   with urllib.request.urlopen(req,timeout=75) as f:raw=f.read(max_bytes+1)
   if len(raw)>max_bytes:raise ValueError("Image exceeds bounded size")
   return raw
  except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as e:
   err=e
   if isinstance(e,urllib.error.HTTPError) and e.code not in (429,500,502,503,504):raise
   time.sleep((k+1)*4)
 raise RuntimeError(repr(err))
def meta(number):
 title=f"File:Catapodium rigidum sl{number}.jpg"
 args=urllib.parse.urlencode({"action":"query","titles":title,"prop":"imageinfo","iiprop":"url|extmetadata|sha1|size","iiurlwidth":2000,"format":"json"})
 ob=json.loads(fetch(API+"?"+args,1700000))
 page=next(iter(ob["query"]["pages"].values()))
 assert "missing" not in page,(number,page)
 info=page["imageinfo"][0];e=info.get("extmetadata",{})
 lic=re.sub("[^a-z0-9.]","",(e.get("LicenseShortName",{}).get("value","").lower()))
 artist=e.get("Artist",{}).get("value","").lower()
 assert lic in ("ccbysa4.0","ccbysa40"),(number,"wrong license",lic)
 assert "stefan.lefnaer" in artist,(number,"wrong creator",artist[:180])
 assert int(info.get("width",0))>=1200 and int(info.get("height",0))>=1200,(number,"too small")
 u=info.get("thumburl")
 assert u and "wikimedia.org" in u,(number,"no thumbnail")
 return info,u
def main():
 d=json.loads(CARD.read_text())
 assert d["id"]=="catapodium-rigidum"
 assert len(d["images"])>=3 and len(d["visual_comparison"]["items"])>=5
 new=[]
 for n,filename,role in SPECS:
  page=f"https://commons.wikimedia.org/wiki/File:Catapodium_rigidum_sl{n}.jpg"
  try:
   info,url=meta(n)
   raw=fetch(url)
   assert raw[:2]==b"\xff\xd8",(n,"source must be JPEG")
   im=Image.open(io.BytesIO(raw));im.verify()
   im=ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
   assert im.width>=800 and im.height>=700,(n,"dimensions",im.size)
   target=BASE/"images"/filename
   target.parent.mkdir(parents=True,exist_ok=True)
   im.save(target,"JPEG",quality=90,optimize=True,progressive=False)
   bb=target.read_bytes()
   checked=Image.open(io.BytesIO(bb))
   assert checked.size==im.size and not checked.getexif()
   rel="images/"+filename
   r={"file":rel,"role":role,"creator":"Stefan.lefnaer",
      "license":"CC BY-SA 4.0","license_url":LICENSE,"source_page":page,
      "public_reuse":"Yes, exact Commons per-photo CC BY-SA 4.0; preserve author/source, license and derivative change notices",
      "source_original_sha1":info.get("sha1"),"original_dimensions":[info.get("width"),info.get("height")],
      "archived_dimensions":list(im.size),"archived_sha256":hashlib.sha256(bb).hexdigest(),
      "modifications":"Wikimedia proportionally resized derivative RGB JPEG, re-encoded and stripped EXIF/GPS; original label pixels untouched; no crop or overlays",
      "photo_status":"New exact species, verified licensed original PHYSICALLY ARCHIVED; role provisional until full-resolution pixel inspection. Do not claim any specifically labelled glume, lemma or physical scale before inspection."}
   prev=next((a for a in d["images"] if a.get("source_page")==page or a.get("file")==rel),None)
   if prev is None:d["images"].append(r)
   else:prev.update(r)
   gall=d["visual_comparison"]["items"]
   if not any(a.get("source_page")==page for a in gall):
    gall.append({"label":f"Catapodium rigidum — exact licensed reproductive photo sl{n} (detail review pending)",
       "scientific_name":"Catapodium rigidum","image_url":(BASE/rel).as_posix(),"image_fit":"contain",
       "image_role":role,"caption":"New source-identified real Catapodium rigidum specimen photograph by Stefan.lefnaer; actual glume/lemma anatomy and any visible scale must be assigned only after independent pixel inspection. Original source CC BY-SA4, author credited.",
       "why_it_matters":"Real photographic reproductive evidence, not a diagram or another species; precise anatomy pending pixel review.",
       "creator":"Stefan.lefnaer","license":"CC BY-SA 4.0","license_url":LICENSE,
       "source_page":page,"markers":[],
       "modifications":r["modifications"],"photo_status":"Exact Commons source identity and photo CC BY-SA4 verified, local JPEG exists. No unverified anatomy arrows."})
   new.append({"sl":n,"path":rel,"sha256":r["archived_sha256"],"dimensions":r["archived_dimensions"]})
   print("ARCHIVED",n,rel,im.size,flush=True)
  except Exception as e:print("HELD",n,repr(e),flush=True)
 if not new:raise RuntimeError("No verified photos archived; all blocked; old gallery left untouched")
 assert all((BASE/r["file"]).is_file() for r in d["images"] if r.get("file","").startswith("images/"))
 d.setdefault("field_id_finish_pass",{})["lane4_catapodium_verified_macro_sources_20261027"]={
   "new_files":new,"source":"Wikimedia Commons Stefan.lefnaer original individual CC BY-SA4",
   "anatomical_role_verification":"PENDING full pixel review; no new arrows, no micro score gain yet",
   "pending":["Check if one truly measured multi-floret spikelet and glumes/lemma are visible","True fully open inner ligule edge already partial from sl15/sl16","Exact rooted annual with flowering head","Live Pages/mobile QA"],
   "rights":"Attribution, exact license and crop/resizing changes preserved, no source sublicensing",
   "scientific_scope":"Species-level exact original; no Hays County locality or BONAP changes",
   "publication":"NOT VERIFIED"}
 d["curation_status"]["photo_metadata_count"]=len(d["images"])
 d["curation_status"]["photo_files_present"]=len([r for r in d["images"] if r.get("file","").startswith("images/")])
 d["learner_visual_status"]["image_count"]=len(d["images"])
 CARD.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
 print("DONE",len(new),"source licensed physical photos, gallery",len(d["visual_comparison"]["items"]),flush=True)
if __name__=="__main__":main()
