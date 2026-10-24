#!/usr/bin/env python3
"""Guarded exact-specimen open-license photo archival; no inferred microscopic anatomy."""
import json,re,html,urllib.request,urllib.parse,io,hashlib,pathlib
from PIL import Image,ImageOps
root=pathlib.Path("content/taxa/Poaceae/Festuca/festuca-versuta")
card=root/"species.json";d=json.loads(card.read_text());assert d["id"]=="festuca-versuta"
source="https://artsandculture.google.com/asset/festuca-versuta-common-name-texas-fescue-specimen-unspecified/5AEb1fxhx838ig?hl=en"
report={"source":source,"catalog":"BRIT1072863","added":[],"holds":[]}
def fetch(url,maxbytes=16000000):
 req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; HaysBotany/1.0; source-credited herbarium study)","Accept":"text/html,image/*"})
 with urllib.request.urlopen(req,timeout=35) as h:
  out=h.read(maxbytes+1)
 if len(out)>maxbytes:raise ValueError("download exceeds size policy")
 return out
try:
 page=fetch(source).decode("utf-8",errors="replace")
 if "BRIT1072863" not in page or "Festuca versuta" not in page:raise ValueError("exact specimen record and taxon name absent in retrieved source HTML")
 if not ("creativecommons.org/licenses/by/4.0" in page or "CC-BY" in page):raise ValueError("attributed CC BY 4.0 rights not confirmed in retrieved record")
 candidates=re.findall(r'<meta[^>]+(?:property|name)=["\\\'](?:og:image|twitter:image)["\\\'][^>]+content=["\\\']([^"\\\']+)',page,re.I)
 candidates+=re.findall(r'<meta[^>]+content=["\\\']([^"\\\']+)["\\\'][^>]+(?:property|name)=["\\\'](?:og:image|twitter:image)',page,re.I)
 candidates=[html.unescape(u).replace("&amp;","&") for u in candidates]
 if not candidates:raise ValueError("No stable image URL in original specimen-page metadata")
 # Try high-resolution variants of the same Google-hosted image before the small preview.
 candidates=[variant for base in candidates for variant in ([base+"=w1800",base+"=s1800",base+"=w1400",base] if "googleusercontent.com/" in base else [base])]
 for url in candidates:
  if not url.startswith("https://"):continue
  try:
   raw=fetch(url)
   with Image.open(io.BytesIO(raw)) as image:image.verify()
   with Image.open(io.BytesIO(raw)) as image:
    image=ImageOps.exif_transpose(image).convert("RGB")
    if min(image.size)<450:raise ValueError("Image resolution insufficient")
    image.thumbnail((2000,2000));out=io.BytesIO();image.save(out,"JPEG",quality=88,optimize=True);blob=out.getvalue()
   rel="images/brit1072863-herbarium-ccby4.jpg";dest=root/rel
   if dest.exists():raise ValueError("Already exists; preserve existing version")
   dest.write_bytes(blob)
   d["images"].append({"file":rel,"role":"BRIT1072863 exact-species herbarium sheet; individual ligule and mature spikelet anatomy not verified","creator":"Botanical Research Institute of Texas (BRIT Collections)","license":"CC BY 4.0","source_page":source,"source_image_url":url,"source_catalog":"BRIT1072863","photo_status":"SPECIMEN_ARCHIVED_ANATOMY_HOLD","sha256":hashlib.sha256(blob).hexdigest(),"modifications":"resized with EXIF removed"})
   d["visual_comparison"]["items"].append({"label":"BRIT1072863 — Texas fescue voucher sheet","scientific_name":"Festuca versuta","image_url":str(root/rel),"image_fit":"contain","image_role":"Exact-species institutional herbarium voucher; not field-life photograph","caption":"Catalogued Festuca versuta sheet from BRIT Collections. Inspect original scale for mature flowering features. Individual glume and ligule anatomy not verified.","creator":"BRIT Collections","license":"CC BY 4.0","source_page":source,"markers":[]})
   d["learner_visual_status"]["image_count"]=len(d["images"])
   d["curation_status"]["photo_files_present"]=len(d["images"])
   d["curation_status"]["photo_metadata_count"]=len(d["images"])
   card.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
   report["added"].append({"file":str(dest),"sha256":hashlib.sha256(blob).hexdigest(),"image_url":url})
   break
  except Exception as e:report["holds"].append({"image_url":url,"reason":str(e)[:150]})
 if not report["added"]:raise ValueError("No acceptable specimen photo downloaded from source")
except Exception as e:report["holds"].append({"stage":"verification","reason":str(e)[:300]})
pathlib.Path("reports/lane3-festuca-brit-photo-20261023.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
