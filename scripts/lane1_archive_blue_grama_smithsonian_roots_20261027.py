#!/usr/bin/env python3
"""Archive actual herbarium-connected fibrous roots of Bouteloua gracilis.
Smithsonian Open Access exact NMNH specimen page confirms public-domain media.
Pressed plant cannot count as a photograph of living rooted plant in soil.
"""
import io, urllib.request, time, json, hashlib, pathlib, html
from PIL import Image, ImageOps
from bs4 import BeautifulSoup
BASE=pathlib.Path("content/taxa/Poaceae/Bouteloua/bouteloua-gracilis")
CARD=BASE/"species.json"
FILENAME="smithsonian-hosna-blue-grama-real-attached-rooted-voucher-public-domain.jpg"
PATH=BASE/"images"/FILENAME
PAGE="https://www.si.edu/object/bouteloua-gracilis-kunth-lag-ex-griffiths:nmnhbotany_16384026"
ARK="ark:/65665/m3a98875bf1ecb469681dc5497e7c55cd7"
CANDIDATES=[
"https://ids.si.edu/ids/deliveryService/id/ark%3A/65665/m3a98875bf1ecb469681dc5497e7c55cd7?max=2800",
"https://ids.si.edu/ids/deliveryService/id/ark:/65665/m3a98875bf1ecb469681dc5497e7c55cd7?max=2800",
"https://ids.si.edu/ids/deliveryService/id/ark%3A/65665/m3a98875bf1ecb469681dc5497e7c55cd7"
]
def grab(u):
 for k in range(3):
  try:
   req=urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0 (botanical training, Smithsonian attribution, HaysCountyBotany)"})
   with urllib.request.urlopen(req,timeout=50) as r:
    raw=r.read()
    print("URL_FETCH",json.dumps({"url":r.url,"status":r.status,"bytes":len(raw),"ct":r.headers.get("Content-Type")}),flush=True)
    return raw
  except Exception as e:
   print("FETCH_RETRY",str(e)[:200],flush=True)
   time.sleep((k+1)*3)
 raise RuntimeError("Unable to fetch verified source "+u)
source=grab(PAGE)
txt=" ".join(html.unescape(BeautifulSoup(source,"html.parser").get_text(" ",strip=True)).split())
print("RIGHTS_CONTEXT",txt[max(0,txt.find("public domain")-200):txt.find("public domain")+240],flush=True)
assert "This media is in the public domain" in txt, "Media-specific PD permission absent"
assert "Bouteloua gracilis" in txt and ("Hosna" in txt and "Davis" in txt), "Record taxon or collectors cannot be verified"
assert "Sep 2016" in txt and "Utah" in txt, "Source locality mismatch"
d=json.loads(CARD.read_text(encoding="utf-8"))
assert d["id"]=="bouteloua-gracilis"
if any(x.get("file")=="images/"+FILENAME for x in d.get("images",[])):
 assert PATH.exists(),"Metadata exists but JPEG missing"
 print("ALREADY_ARCHIVED")
 raise SystemExit(0)
assert not PATH.exists() and not any(x.get("source_page")==PAGE for x in d.get("images",[]))
actual=None
for url in CANDIDATES:
 try:
  raw=grab(url)
  im=Image.open(io.BytesIO(raw));im.load()
  print("PHOTO_PIXEL_SIZE",url,im.size,im.format,flush=True)
  if im.width>=950 and im.height>=1300 and im.format in ("JPEG","PNG"):
   actual=(im,url)
   break
 except Exception as e:print("INVALID_OR_MISSING_SOURCE",url,str(e)[:150],flush=True)
assert actual,"No usable root-bearing true specimen JPEG from Smithsonian image service"
im,url=actual
im=ImageOps.exif_transpose(im).convert("RGB")
im.thumbnail((3000,3400),Image.Resampling.LANCZOS)
PATH.parent.mkdir(parents=True,exist_ok=True)
im.save(PATH,"JPEG",quality=92,optimize=True)
v={
 "file":"images/"+FILENAME,
 "role":"Exact-species 2016 Smithsonian National Herbarium preserved Bouteloua gracilis collection US 03476248 with TRUE fibrous roots still attached to the basal tussock and same plant's intact flowering stems. This is a pressed herbarium specimen and NOT a living rooted field photo.",
 "creator":"Smithsonian National Museum of Natural History (pressed specimen collected by R. K. Hosna and K. E. Davis)",
 "license":"Public domain — individual Smithsonian object marked open access",
 "license_url":"https://www.si.edu/openaccess",
 "source_page":PAGE,"source_original":url,
 "specimen_code":"US 03476248","smithsonian_record":"nmnhbotany_16384026",
 "collector":"R. K. Hosna and K. E. Davis","collection_date":"2016-09-08",
 "source_location":"Approximately 15 mi NNW of Monticello, San Juan County, Utah, USA; not Texas and not a field-ID voucher from Hays.",
 "public_reuse":"Exact Smithsonian object states media public domain; photographer/institution/collection credited.",
 "photo_review":"Source image independently visually reviewed: one entire pressed blue grama tuft with connected thin roots clearly protruding below dense crown and several long culms terminating in true eyelash heads. Fine ligule, individual spikelet glumes, live soil interaction NOT shown.",
 "image_dimensions_archived":[im.width,im.height],
 "image_sha256":hashlib.sha256(PATH.read_bytes()).hexdigest(),
 "modifications":"Image was downscaled keeping entire voucher and physical roots, recompressed as GPS/EXIF-free JPEG."
}
d["images"].append(v)
panel={
 "label":"ACTUAL ROOTS ATTACHED TO BLUE GRAMA — Smithsonian rooted pressed specimen (not live plant)",
 "scientific_name":"Bouteloua gracilis",
 "image_url":"content/taxa/Poaceae/Bouteloua/bouteloua-gracilis/images/"+FILENAME,
 "image_fit":"contain",
 "creator":v["creator"],"license":v["license"],"license_url":v["license_url"],
 "source_page":PAGE,"specimen_code":"US 03476248",
 "image_role":"Genuine connected fibrous root system attached to same individual dried blue grama tuft and flowering stems on real Smithsonian voucher; not actively growing in soil.",
 "caption":"Smithsonian U.S. National Herbarium specimen US 03476248, collected in Utah in 2016. The lower part of the pressed grass shows a continuous tufted crown with fine fibrous roots below; several eyebrow-shaped flowering stems are still connected. This photograph demonstrates physical root-to-shoot continuity but cannot tell how a living root occupies soil.",
 "why_it_matters":"Adds authentic connected root evidence to previous leaf-sheath and flowering photos without inventing a living-plant excavation. A separate live rooted specimen remains a missing higher-quality teaching role.",
 "markers":[],
 "photo_status":"The official exact-species Smithsonian voucher image, roots and reuse rights inspected; no precision root arrows until mobile thumbnail placement checked."
}
items=d["visual_comparison"]["items"]
if not any(x.get("image_url")==panel["image_url"] for x in items):
 i=next((i for i,x in enumerate(items) if x.get("scientific_name")!="Bouteloua gracilis"),len(items))
 items.insert(i,panel)
d.setdefault("curation_status",{})["photo_files_present"]=sum(x.get("file","").startswith("images/") for x in d["images"])
d["curation_status"]["lane1_blue_grama_smithsonian_connected_roots_20261027"]="PUBLIC_DOMAIN_PRESSED_SPECIMEN_CONNECTED_REAL_ROOTS_ARCHIVED_HALF_BASE_ROLE_NOT_LIVE_ROOTED_PLANT"
d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
d["learner_visual_status"]["note"]="Nine blue grama photo metadata records total, five eligible local JPEGs and one public-domain external caryopsis link, three CC BY-NC research holds. Smithsonian US 03476248 dried whole real rooted tuft gains 0.5 root role but live photographed root crown still missing; true inner free ligule and dissected glumes open."
d["photo_note"]=(d.get("photo_note","") or "")+" 2026-10-27: Source-matched Smithsonian public-domain genuine rooted preserved Bouteloua gracilis specimen US 03476248 physically archived, not a living root photo. Add +0.5 of 6 photographic roles only if actual archive confirmed."
q=d.get("field_photo_quickcheck")
if q:
 q["steps"].append("REAL ROOTS, BUT PRESERVED: Smithsonian's 2016 US 03476248 blue grama herbarium sheet has actual fibrous roots physically connected to a pressed tuft and flowering shoots. This earns HALF-ROLE root evidence, not a living soil root observation. Compare with your own living plant excavation when possible.")
 q["warning"]="Nine blue grama records: six public-eligible (one original external caryopsis link), three historical CC BY-NC holds. One PUBLIC-DOMAIN Smithsonian pressed specimen shows genuine roots attached to blue grama stems (NOT live rooted grass). Actual true inner ciliate 0.1–0.4-mm ligule, scaled glume/lemma dissection and mobile arrow QA remain missing."
CARD.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"result":"ARCHIVED_SMITHSONIAN_PD_BLUE_GRAMA_ROOTED_SHEET","photo_count":len(d["images"]),"panels":len(items),"file_bytes":PATH.stat().st_size,"url":url}),flush=True)
