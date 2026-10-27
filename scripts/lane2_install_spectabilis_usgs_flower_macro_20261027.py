#!/usr/bin/env python3
"""Install one source-verified USGS PD original E. spectabilis actual flower macro."""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import quote
from PIL import Image,ImageOps
import io,json,hashlib
R=Path(__file__).resolve().parents[1]
B=R/"content/taxa/Poaceae/Eragrostis/eragrostis-spectabilis"
CARD=B/"species.json"
SCORES=R/"reports/lane2-six-role-photo-score-20261027.json"
REPORT=R/"reports/lane2-spectabilis-usgs-flower-macro-20261027.json"
MARK=R/"workflow/field-id-publication/lane2-spectabilis-usgs-flower-macro-20261027.json"
NAME="Purple love grass, MD, PG County 2013-08-20-17.02.10 ZS PMax (9615071149).jpg"
PAGE="https://commons.wikimedia.org/wiki/File:"+quote(NAME.replace(" ","_"),safe="(),")
SRC="https://upload.wikimedia.org/wikipedia/commons/1/13/Purple_love_grass%2C_MD%2C_PG_County_2013-08-20-17.02.10_ZS_PMax_%289615071149%29.jpg"
FILE="usgs-biml-eragrostis-spectabilis-real-flower-macro-9615071149.jpg"
REL="content/taxa/Poaceae/Eragrostis/eragrostis-spectabilis/images/"+FILE
def req(u):
 with urlopen(Request(u,headers={"User-Agent":"Mozilla/5.0 HaysCountyBotanyEducationalPhotoValidation"}),timeout=45) as f:return f.read(8000000)
def out(p,x):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def main():
 c=json.loads(CARD.read_text())
 assert c["id"]=="eragrostis-spectabilis"
 imgs=c["images"];panels=c["visual_comparison"]["items"]
 if any(x.get("file")=="images/"+FILE for x in imgs):
  assert (R/REL).is_file() and any(x.get("image_url")==REL for x in panels)
  print("ALREADY_PRESENT");return
 assert not (R/REL).exists(),"Partial existing install: stop"
 page=req(PAGE).decode(errors="replace").lower()
 for needle in ("eragrostis spectabilis","usgs bee inventory","public domain","attribution 2.0","9615071149"):
  assert needle in page,"rights/species check failed: "+needle
 raw=req(SRC)
 assert raw.startswith(b"\xff\xd8\xff")
 with Image.open(io.BytesIO(raw)) as original:
  assert original.format=="JPEG"
  image=ImageOps.exif_transpose(original).convert("RGB")
  w,h=image.size
  assert min(w,h)>=1500,"not full-size original"
  b=io.BytesIO();image.save(b,"JPEG",quality=92,optimize=True)
 b=b.getvalue();dest=R/REL;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
 sha=hashlib.sha256(b).hexdigest()
 meta={
  "creator":"USGS Bee Inventory and Monitoring Lab",
  "license":"Public domain (USGS federal photograph); Wikimedia Commons also lists CC BY 2.0",
  "license_url":PAGE,"source_page":PAGE,"source_image":SRC,
  "original_flickr_photo_id":"9615071149","source_taxon_name":"Eragrostis spectabilis",
  "public_reuse":"yes — USGS public domain; original Commons alternate CC BY 2.0 retained",
  "modifications":"Re-encoded RGB JPEG, removed EXIF/GPS; no deceptive crop; two source-pixel-checked browser annotations",
  "source_pixel_dimensions":[w,h],"archived_sha256":sha
 }
 imgs.append({"file":"images/"+FILE,"role":"True purple flower photographed using 5x focus-stacked macro, NOT complete seedhead, calibrated ruler or same plant dissection",**meta})
 ix=next((i for i,x in enumerate(panels) if "LOOK-ALIKE" in x.get("label","")),len(panels))
 panels.insert(ix,{
  "label":"USGS MICRO-MACRO · photographed purple reproductive flower",
  "scientific_name":"Eragrostis spectabilis",
  "image_url":REL,"image_fit":"contain",
  "image_role":"True actual reproductive macro, beyond distant panicle",
  "caption":"Actual tiny purple bloom, photographed with a 5x macro lens and focus stacking by the USGS Bee Inventory and Monitoring Lab. This is a flower-scale view, not the entire mature panicle. No ruler or dissection identifiers accompany this original; do not mislabel glume versus lemma based on guesswork.",
  "why_it_matters":"Learn the difference between a field-scale purple cloud and the real miniature reproductive unit.",
  "markers":[{"label":"Feathery stigma extending from purple flower","label_x":6,"label_y":11,"target_x":34,"target_y":20},{"label":"Enclosing purple floral bracts — individual glumes not resolved","label_x":68,"label_y":77,"target_x":60,"target_y":46}],"photo_status":"Full original USGS pixels inspected; two verified gross-anatomy targets (stigma and purple bracts), no unsupported glume/lemma distinction",
  **meta
 })
 c.setdefault("curation_status",{})["lane2_usgs_real_flower_20261027"]={
  "status":"FIELD_READY_PHOTO_GAPS","new_archived_jpegs":1,"new_verified_arrows":2,
  "local_species_photo_records":len(imgs),"provisional_six_role_score":"5/6 (83%)",
  "still_missing":["exposed inner 0.2–0.4 mm ligule","excavated rootstock/rhizome","measured glumes/lemma dissection"],"pages":"unverified"
 }
 c["photo_note"]=c.get("photo_note","")+"\n2026-10-27 Lane2: archive exact USGS Bee Inventory 5x focus-stacked purple lovegrass reproductive flower original, public domain per Commons, alternate CC BY 2.0. Only two photo-visible gross structure arrows (feathery stigma and purple bracts); no invented fine glume/lemma IDs. Reproductive closeup 0.5→1; rooted crown and true ligule still partial."
 out(CARD,c)
 s=json.loads(SCORES.read_text());v=next(x for x in s["records"] if x["canonical_id"]=="eragrostis-spectabilis")
 assert v["after_total"]==4.5 and v["roles"]["reproductive_closeup"]==0.5
 v["roles"]["reproductive_closeup"]=1;v["after_total"]=5;v["after_percentage"]=83;v["change_percentage_points"]=8
 v["new_source_report"]="reports/lane2-spectabilis-usgs-flower-macro-20261027.json"
 v["gaps_warning"]="USGS real flowering macro obtained; no calibrated lemma/glume dissection. True tiny ligule and connected rhizome still unphotographed."
 s["summary"]["mean_after_percent"]=round(sum(x["after_total"] for x in s["records"])/len(s["records"])*100/6,1)
 dist={}
 for x in s["records"]:
  k=f'{x["after_total"]:.1f}/6';dist[k]=dist.get(k,0)+1
 s["summary"]["distribution"]=dist
 s["summary"]["latest_purple_usgs_20261027"]={"new_real_photos":1,"arrows":2,"rights":"USGS PD; Commons CC BY 2.0 alternate","photo_score":83,"pages":"unverified"}
 out(SCORES,s)
 out(REPORT,{"species":"Eragrostis spectabilis","photographer":"USGS Bee Inventory and Monitoring Lab","status":"FIELD_READY_PHOTO_GAPS","new_photo_path":REL,"source":PAGE,"origin":SRC,"license":"USGS public domain and Commons CC BY 2.0 alternate","source_bytes":len(raw),"archive_bytes":len(b),"original_dimensions":[w,h],"archive_sha256":sha,"new_panels":1,"new_arrows":2,"before_roles":4.5,"after_roles":5,"percent":83,"pages":"unverified"})
 out(MARK,{"type":"manual_field_id_publication","date":"2026-10-27","species":"Eragrostis spectabilis","source_report":str(REPORT.relative_to(R)),"status":"FIELD_READY_PHOTO_GAPS","pages":"guarded release required"})
 print("INSTALLED_USGS",len(imgs),w,h,sha,s["summary"]["mean_after_percent"])
if __name__=="__main__":main()
