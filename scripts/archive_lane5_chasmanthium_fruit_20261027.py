#!/usr/bin/env python3
"""Archive verified Commons CC BY-SA 4.0 fruit/floret photos of inland sea oats.
Only use the exact photographer's labeled taxa, no guessed micromorphology arrows.
Do not modify existing photo rights or county/native status.
"""
import hashlib, html, io, json, pathlib, re, time
import urllib.parse, urllib.request, urllib.error
from PIL import Image, ImageOps
ROOT=pathlib.Path("content/taxa/Poaceae/Chasmanthium/chasmanthium-latifolium")
CARD=ROOT/"species.json"
REPORT=pathlib.Path("reports/lane5-chasmanthium-diagnostic-fruit-20261027.json")
SOURCES=[
 ("Chasmanthium latifolium14.jpg","douglas-goldman-fruiting-florets-14.jpg","REAL FRUITING FLORETS — overlapping mature floral scales","Source-labeled fruiting florets of inland sea oats. This shows floret-scale arrangement in ripe material. A floret is not a bare grain, and this photograph alone does not prove basal glume identity.","Learn what real maturing florets look like before attempting finer glume versus lemma dissection."),
 ("Chasmanthium latifolium15.jpg","douglas-goldman-single-fruiting-floret-15.jpg","ONE FRUITING FLORET — mature exterior view","Photographer-labeled single fruiting floret of Chasmanthium latifolium. Use this alongside the separate actual grain photo; do not mistake the enclosing bract for the naked caryopsis.","Supports field and hand-lens study of one reproductive unit without relying on copyrighted research plates."),
 ("Chasmanthium latifolium16.jpg","douglas-goldman-caryopsis-16.jpg","ACTUAL CARYOPSIS — grass grain from a floret","A photographer-labeled actual caryopsis (grass grain) of inland sea oats. The grain forms inside a fertile floret and is different from the many overlapping lemmas seen on a whole hanging spikelet. No unverified internal structure arrows or numeric scale claims.","Shows the distinct mature grain rather than labeling an entire hanging spikelet a seed.")
]
def fetch(url):
 request=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyEducationalPhotoArchiver/1.0 (open-license source-verification)"})
 for n in range(5):
  try:
   with urllib.request.urlopen(request,timeout=45) as reply:
    raw=reply.read(16000001)
   if len(raw)>16000000:raise ValueError("Oversize image or API payload")
   return raw
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or n==4:raise
   time.sleep(3*(n+1))
out={"source_collection":"Douglas Goldman, Chasmanthium latifolium Congaree SC (not Hays County)","date":"2026-10-27","photos":[],"critical_gaps_retained":["No source-verified photograph of the true inner ligule membrane tip with millimeter scale","No open-license physically exposed rooted rhizome connected to flowering shoot","No verified separately dissected two basal glumes with 1mm scale"],"new_markers":0}
d=json.loads(CARD.read_text())
assert d["id"]=="chasmanthium-latifolium"
items=d["visual_comparison"]["items"]
for name,destname,label,caption,why in SOURCES:
 source="https://commons.wikimedia.org/wiki/File:"+name.replace(" ","_")
 rel="images/"+destname
 if any(i.get("file")==rel for i in d["images"]):
  out["photos"].append({"source":source,"status":"already_archived"});continue
 try:
  q=urllib.parse.urlencode({"action":"query","prop":"imageinfo|categories","format":"json","iiprop":"url|extmetadata","cllimit":"max","iiurlwidth":"1800","titles":"File:"+name})
  obj=next(iter(json.loads(fetch("https://commons.wikimedia.org/w/api.php?"+q))["query"]["pages"].values()))
  ii=obj["imageinfo"][0]
  md=ii.get("extmetadata",{})
  lic=re.sub(r"[^A-Z0-9]","",md.get("LicenseShortName",{}).get("value","").upper())
  artist=html.unescape(re.sub("<[^>]*>"," ",md.get("Artist",{}).get("value",""))).strip()
  desc=html.unescape(re.sub("<[^>]*>"," ",md.get("ImageDescription",{}).get("value",""))).strip()
  categories={c["title"] for c in obj.get("categories",[])}
  if lic!="CCBYSA40" or "Douglas" not in artist or "Category:Chasmanthium latifolium" not in categories:
   raise ValueError("Exact creator, species, or CC BY-SA 4.0 check failed: "+str([lic,artist]))
  if name.endswith("14.jpg") and not re.search(r"floret",desc,re.I):raise ValueError("Source lacks fruiting floret description")
  if name.endswith("15.jpg") and not re.search(r"floret",desc,re.I):raise ValueError("Source lacks floret description")
  if name.endswith("16.jpg") and not re.search(r"caryops",desc,re.I):raise ValueError("Source lacks caryopsis description")
  raw=fetch(ii.get("thumburl") or ii["url"])
  with Image.open(io.BytesIO(raw)) as im:im.verify()
  with Image.open(io.BytesIO(raw)) as im:im=ImageOps.exif_transpose(im).convert("RGB")
  if min(im.size)<650:raise ValueError("Insufficient pixel resolution: "+str(im.size))
  ROOT.joinpath("images").mkdir(exist_ok=True)
  dest=ROOT/"images"/destname
  im.save(dest,"JPEG",quality=90,optimize=True)
  with Image.open(dest) as im2:im2.verify()
  sha=hashlib.sha256(dest.read_bytes()).hexdigest()
  d["images"].append({"file":rel,"role":"Photographer-source-labeled "+desc[:140]+"; fine floret identification not arrow-verified",
   "creator":"Douglas Goldman","license":"CC BY-SA 4.0","license_url":"https://creativecommons.org/licenses/by-sa/4.0/",
   "source_page":source,"source_original_url":ii["url"],"source_location":"Congaree River floodplain, South Carolina — not Hays voucher",
   "modifications":"RGB JPEG re-encoded, source EXIF/GPS stripped; no arrows added",
   "public_reuse":"CC BY-SA 4.0 individually source-verified, creator credited and license linked",
   "sha256":sha,"pixels":list(im.size),"photo_status":"REAL SOURCE-LABELED FRUIT/REPRODUCTIVE MACRO — any fine feature arrows await pixel QA"})
  insert=next((i for i,v in enumerate(items) if v.get("scientific_name")!="Chasmanthium latifolium"),len(items))
  for tile in d.get("field_id_short_tiles",[]):
   if "photo_panel_indices" in tile:tile["photo_panel_indices"]=[n+1 if n>=insert else n for n in tile["photo_panel_indices"]]
  items.insert(insert,{"label":label,"scientific_name":"Chasmanthium latifolium","image_url":str(dest),
   "image_fit":"contain","image_role":"Source-confirmed "+desc[:120],"caption":caption,
   "why_it_matters":why,"creator":"Douglas Goldman","license":"CC BY-SA 4.0",
   "license_url":"https://creativecommons.org/licenses/by-sa/4.0/","source_page":source,
   "markers":[],"photo_status":"Original image/source species/rights checked; zero microscopic arrows; source photograph is not a local Hays voucher."})
  if len(d.get("field_id_short_tiles",[]))>3:
   tile=d["field_id_short_tiles"][3]
   tile.setdefault("photo_panel_indices",[]).append(insert)
  out["photos"].append({"source":source,"path":str(dest),"status":"archived","pixels":list(im.size),"sha256":sha,"license":"CC BY-SA 4.0","gallery_index":insert})
 except Exception as e:out["photos"].append({"source":source,"status":"HELD","reason":str(e)[:300]})
if any(p["status"]=="archived" for p in out["photos"]):
 d.setdefault("field_id_finish_pass",{})["lane5_real_fruit_photos_20261027"]={
 "new_photos":out["photos"],"status":"FIELD_READY_PHOTO_GAPS",
 "interpretation":"Open-license floret and/or fruit proof available; true ligule and rooted rhizome remain open. No misleading arrows or 100% score."}
 CARD.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
REPORT.parent.mkdir(exist_ok=True)
REPORT.write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out))
