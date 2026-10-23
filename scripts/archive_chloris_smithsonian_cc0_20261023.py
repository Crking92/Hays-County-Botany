#!/usr/bin/env python3
"""Archive Smithsonian exact-species CC0 herbarium specimen via IIIF, or write explicit hold."""
import json,re,io,pathlib,urllib.request,html,hashlib
from urllib.parse import urljoin
from PIL import Image,ImageOps
BASE=pathlib.Path("content/taxa/Poaceae/Chloris/chloris-andropogonoides")
SPECIES=BASE/"species.json"
SOURCE="https://www.si.edu/object/chloris-andropogonoides-e-fourn:nmnhbotany_10607789"
REPORT=pathlib.Path("reports/chloris-smithsonian-cc0-20261023.json")
report={"source":SOURCE,"added":[],"holds":[]}
def fetch(url):
 req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyHerbariumArchive/1.0 (educational repository; provenance retained)","Accept":"application/json,text/html,*/*"})
 with urllib.request.urlopen(req,timeout=50) as res:
  payload=res.read(24000001)
 if len(payload)>24000000:raise ValueError("Too large")
 return payload
try:
 page=fetch(SOURCE).decode("utf-8")
 # Institution page must be exact-species and indicate open-access/CC0.
 if not re.search(r"Chloris\s+andropogonoides",html.unescape(page),re.I):raise ValueError("Exact species name absent")
 if not re.search(r"CC0|public domain",page,re.I):raise ValueError("CC0/public-domain statement absent")
 # Discovery is conservative: only explicit IIIF presentation manifests in page markup.
 candidates=re.findall(r'https?[^"\s<>]+(?:manifest(?:\.json)?|/manifest)[^"\s<>]*',html.unescape(page),re.I)
 candidates=[x.replace("&amp;","&") for x in candidates if "iiif" in x.lower() or "si.edu" in x.lower()]
 if not candidates:raise ValueError("No resolvable IIIF manifest found on specimen page")
 manifest=None
 for u in candidates[:10]:
  try:
   j=json.loads(fetch(u))
   if "nmnhbotany_10607789" in json.dumps(j).lower() or "chloris andropogonoides" in json.dumps(j).lower():
    manifest=j;break
  except Exception:continue
 if not manifest:raise ValueError("IIIF manifests did not prove target specimen identity")
 # IIIF v2 and v3 image descriptors; take only actual service URLs.
 text=json.dumps(manifest)
 ids=re.findall(r'https?://(?:ids|iiif)\.si\.edu/[^"\s]+',text)
 ids=[u.replace("\\/","/") for u in ids]
 image_urls=[u for u in ids if u.endswith(".jpg") or "default.jpg" in u]
 if not image_urls:
  service=[u for u in ids if "/iiif/" in u]
  if service:image_urls=[service[0].rstrip("/")+"/full/1200,/0/default.jpg"]
 if not image_urls:raise ValueError("No Smithsonian IIIF image candidate")
 raw=fetch(image_urls[0])
 with Image.open(io.BytesIO(raw)) as im:im.verify()
 with Image.open(io.BytesIO(raw)) as im:
  im=ImageOps.exif_transpose(im).convert("RGB")
  if min(im.size)<600:raise ValueError("Image resolution inadequate")
  im.thumbnail((1800,1800))
  out=io.BytesIO();im.save(out,"JPEG",quality=88,optimize=True);binary=out.getvalue()
 dest=BASE/"images/chloris-andropogonoides-smithsonian-victor-cory-1946-cc0.jpg"
 dest.parent.mkdir(exist_ok=True);dest.write_bytes(binary)
 with Image.open(dest) as im:im.verify()
 d=json.loads(SPECIES.read_text())
 assert d["id"]=="chloris-andropogonoides"
 if not any(x.get("source_page")==SOURCE for x in d["images"]):
  d["images"].append({"file":"images/"+dest.name,"role":"Source-identified historic Texas herbarium voucher; inspect specimen image before marking anatomy","creator":"Smithsonian NMNH; specimen collected Victor L. Cory, 5 Oct 1946","license":"CC0 / public domain (Smithsonian item)", "source_page":SOURCE,"publication_scope":"PUBLIC-WEB-CLEARED","modifications":"Resized and stripped metadata","sha256":hashlib.sha256(binary).hexdigest(),"photo_status":"VOUCHER_REFERENCE_NOT_YET_ANATOMY_REVIEWED"})
  d["curation_status"]["photo_files_present"]=len(d["images"])
  d["curation_status"]["photo_metadata_count"]=len(d["images"])
  d["learner_visual_status"]["image_count"]=len(d["images"])
  SPECIES.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
 report["added"].append(dest.as_posix())
except Exception as e:
 report["holds"].append(str(e))
REPORT.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
