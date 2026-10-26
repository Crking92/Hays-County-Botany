#!/usr/bin/env python3
"""Photo-first, rights-gated Phragmites three-lineage review.
Archive candidates only; DO NOT change canonical species JSON until pixel QA.
"""
import io, json, pathlib, urllib.parse, urllib.request, re, html, hashlib, time
from PIL import Image, ImageOps

ROOT=pathlib.Path("content/taxa/Poaceae/Phragmites/phragmites-australis/images")
REPORT=pathlib.Path("reports/phragmites-three-lineage-photo-acquisition-20261026.json")
ROOT.mkdir(parents=True,exist_ok=True);REPORT.parent.mkdir(parents=True,exist_ok=True)
try:
 previous_audit=json.loads(REPORT.read_text()) if REPORT.exists() else {"results":[]}
except Exception:
 previous_audit={"results":[]}
results=[]
USER_AGENT="HaysCountyBotanyVisualLearner/1.0 (credited noncommercial grass identification; github.com/Crking92/Hays-County-Botany)"
def fetch(url):
 req=urllib.request.Request(url,headers={"User-Agent":USER_AGENT,"Accept":"application/json" if "/v1/" in url or "api.php" in url else "image/*"})
 with urllib.request.urlopen(req,timeout=40) as f:return f.read(25_000_001)
def save_image(raw,name,metadata):
 if not (12000<len(raw)<25_000_000):raise ValueError("unexpected image size")
 with Image.open(io.BytesIO(raw)) as im:im.verify()
 with Image.open(io.BytesIO(raw)) as im:
  if im.format not in ("JPEG","PNG") or min(im.size)<450:raise ValueError("not usable diagnostic photograph")
  clean=ImageOps.exif_transpose(im).convert("RGB")
  dims=clean.size
  clean.thumbnail((1600,1600))
  b=io.BytesIO();clean.save(b,format="JPEG",quality=89,optimize=True)
  outfile=ROOT/name
  if outfile.exists():
   with Image.open(outfile) as existing: existing.verify()
   return dict(metadata,archive=str(outfile),archive_sha256=hashlib.sha256(outfile.read_bytes()).hexdigest(),
             source_dimensions=dims,archived_dimensions=list(clean.size),archive_bytes=outfile.stat().st_size,
             modifications="existing archived JPEG retained without overwrite; original EXIF/GPS had been stripped",
             status="ALREADY_ARCHIVED_CANDIDATE",
             anatomical_pixel_review="PREVIOUS_PASS",lineage_certification="SOURCE-IDENTIFIED ONLY; NOT GENETICALLY VERIFIED")
  outfile.write_bytes(b.getvalue())
 with Image.open(outfile) as check:check.verify()
 return dict(metadata,archive=str(outfile),archive_sha256=hashlib.sha256(outfile.read_bytes()).hexdigest(),
             source_dimensions=dims,archived_dimensions=list(clean.size),archive_bytes=outfile.stat().st_size,
             modifications="resized/re-encoded JPEG, original EXIF/GPS stripped; no arrows",
             status="ARCHIVED_CANDIDATE_NOT_ON_PUBLIC_SPECIES_GALLERY",
             anatomical_pixel_review="PENDING",lineage_certification="SOURCE-IDENTIFIED ONLY; NOT GENETICALLY VERIFIED")

# Manually photo-reviewed native exposed internode from exact original Commons JPG.
# Source description identifies americanus despite contradictory Commons basename.
# License individually checked on file page: Matt Lavin CC BY-SA 2.0.
# No new classification of Texas reed, no anatomy arrows.
native_original="https://upload.wikimedia.org/wikipedia/commons/4/43/Phragmites_australis_australis_%2821075794926%29.jpg"
native_page="https://commons.wikimedia.org/wiki/File:Phragmites_australis_australis_(21075794926).jpg"
native_dest=ROOT/"lineage-native-matt-lavin-red-stem-21075794926.jpg"
native_md={"source_page":native_page,"image_url":native_original,"creator":"Matt Lavin",
 "source_taxon":"Phragmites australis subsp. americanus — author-description; Commons basename incorrectly says australis australis",
 "source_location":"Benson County, North Dakota, USA",
 "source_role":"native reed RED EXPOSED MID-STEM INTERNODE with old sheath detached around node; direct visual check before gallery",
 "license":"CC BY-SA 2.0","license_url":"https://creativecommons.org/licenses/by-sa/2.0/",
 "site_rule":"correct source-description vs file-name taxon conflict must be displayed; no genotype, no Texas",
 "original_source_description":"This native subspecies americanus (American common reed) is distinguished in part by its reddish stems that are exposed during late summer/fall as blades/sheaths disarticulate."}
try:
 if native_dest.exists():
  with Image.open(native_dest) as im: im.verify()
  results.append(dict(native_md,status="ALREADY_ARCHIVED_CANDIDATE",
     archive=str(native_dest),archive_sha256=hashlib.sha256(native_dest.read_bytes()).hexdigest(),
     archive_bytes=native_dest.stat().st_size,anatomical_pixel_review="PENDING",
     lineage_certification="AUTHOR-DESCRIBED ONLY, NOT GENETICALLY VERIFIED"))
 else:
  results.append(save_image(fetch(native_original), native_dest.name,native_md))
except Exception as e:
 results.append({"status":"HELD","source_page":native_page,"target":str(native_dest),
                 "license":"CC BY-SA 2.0","creator":"Matt Lavin",
                 "reason":type(e).__name__+": "+str(e)[:350]})

# Exact source-labelled introduced lineage: taxon and photographer on Commons description
title="File:European Reed (Phragmites australis australis) - Oakville, Ontario 2017-05-12.jpg"
page="https://commons.wikimedia.org/wiki/File:"+urllib.parse.quote(title[5:].replace(" ","_"))
try:
 api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","prop":"imageinfo","iiprop":"url|extmetadata","titles":title,"format":"json"})
 data=json.loads(fetch(api))
 info=next(iter(data["query"]["pages"].values()))["imageinfo"][0]
 ext=info["extmetadata"];license=ext["LicenseShortName"]["value"]
 artist=html.unescape(re.sub(r"<[^>]+>","",ext["Artist"]["value"])).strip()
 if "Hodnett" not in artist or re.sub(r"[^a-z0-9]","",license.lower())!="ccbysa40":
  raise ValueError("source artist/license verification mismatch: "+repr((artist,license)))
 results.append(save_image(fetch(info["url"]),"lineage-introduced-ontario-ryan-hodnett.jpg",
  {"source_page":page,"image_url":info["url"],"creator":"Ryan Hodnett","source_taxon":"Phragmites australis subsp. australis",
   "source_location":"Oakville, Ontario, Canada","source_role":"introduced Eurasian lineage source-labelled stand; no DNA determination",
   "license":"CC BY-SA 4.0","license_url":"https://creativecommons.org/licenses/by-sa/4.0/",
   "site_rule":"attribution+ShareAlike, alteration noted; not an authenticated Texas population"}))
except Exception as e:results.append({"status":"HELD","source_page":page,"target":str(ROOT/"lineage-introduced-ontario-ryan-hodnett.jpg"),
                                 "reason":type(e).__name__+": "+str(e)[:350]})
# Gulf candidates are iNaturalist observations source-identified to berlandieri.
# Single-user determinations are only provisional and NEVER lineage-certified.
for obsid in [120001790, 67027636, 47408883]:
 try:
  js=json.loads(fetch("https://api.inaturalist.org/v1/observations/"+str(obsid)))
  obs=js["results"][0]
  taxa=obs.get("taxon") or {}
  name=taxa.get("name","")
  if not ("Phragmites" in name and "berlandieri" in name):raise ValueError("observation currently not identified to berlandieri: "+name)
  quality=obs.get("quality_grade","")
  photos=obs.get("photos") or []
  # Prefer BY/SA/CC0, allow verified NC only for owner's noncommercial educational site.
  permitted=("cc0","cc-by","cc-by-sa","cc-by-nc","cc-by-nc-sa")
  choices=[p for p in photos if p.get("license_code") in permitted and p.get("url")]
  if not choices:raise ValueError("no image-level CC photo on this observation")
  choices.sort(key=lambda p:permitted.index(p["license_code"]))
  ph=choices[0];code=ph["license_code"]
  url=ph["url"].replace("/square.", "/large.").replace("/thumb.","/large.").replace("/small.","/large.").replace("/medium.","/large.")
  if not url.startswith("https://") or "inaturalist" not in urllib.parse.urlparse(url).netloc:
   raise ValueError("unsupported image host")
  credit=ph.get("attribution") or obs.get("user",{}).get("name") or obs.get("user",{}).get("login")
  if not credit:raise ValueError("missing photo creator/attribution")
  fname=f"lineage-gulf-inat-{obsid}-{ph['id']}.jpg"
  results.append(save_image(fetch(url),fname,{"source_page":"https://www.inaturalist.org/observations/"+str(obsid),
    "individual_photo_page":"https://www.inaturalist.org/photos/"+str(ph["id"]),"image_url":url,
    "creator":credit,"source_taxon":name,"source_role":"GULF COAST BERLANDIERI PROVISIONAL SOURCE-IDENTIFIED REFERENCE ONLY",
    "quality_grade":quality,"observation_id":obsid,"photo_id":ph["id"],
    "license":code,"license_url":"https://creativecommons.org/licenses/"+code.replace("cc-","")+"/4.0/",
    "site_rule":"noncommercial site only if NC; no genetics/lineage/haplotype inferred from iNaturalist ID",
    "observation_date":obs.get("observed_on"),"place_guess":obs.get("place_guess")}))
  break
 except Exception as e:
  results.append({"status":"HELD","observation_id":obsid,"source_page":"https://www.inaturalist.org/observations/"+str(obsid),
                  "reason":type(e).__name__+": "+str(e)[:350]})

# Native-lineage organ candidates: the Commons filenames say "australis australis"
# but photographer Matt Lavin's own description explicitly identifies native
# "subspecies americanus" and describes naturally shed old sheaths. NEVER
# trust the misleading file basename to assign these to introduced Eurasian.
for num in ["20915185149","21075794926"]:
 title=f"File:Phragmites australis australis ({num}).jpg"
 page="https://commons.wikimedia.org/wiki/File:"+urllib.parse.quote(title[5:].replace(" ","_"))
 try:
  api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(
   {"action":"query","prop":"imageinfo","iiprop":"url|extmetadata","titles":title,"format":"json"})
  info=next(iter(json.loads(fetch(api))["query"]["pages"].values()))["imageinfo"][0]
  md=info["extmetadata"];artist=html.unescape(re.sub(r"<[^>]+>","",md["Artist"]["value"])).strip()
  lic=md["LicenseShortName"]["value"];desc=html.unescape(re.sub(r"<[^>]+>"," ",md.get("ImageDescription",{}).get("value",""))).lower()
  if "Matt Lavin" not in artist or re.sub(r"[^a-z0-9]","",lic.lower())!="ccbysa20":
   raise ValueError("creator or individual license does not match Matt Lavin / CC BY-SA 2.0")
  if "native subspecies americanus" not in desc:
   raise ValueError("exact author description did not identify native americanus: "+desc[:180])
  results.append(save_image(fetch(info["url"]),f"lineage-native-matt-lavin-{num}.jpg",
   {"source_page":page,"image_url":info["url"],"creator":"Matt Lavin",
    "source_taxon":"Phragmites australis subsp. americanus per PHOTO DESCRIPTION, despite misnamed Commons filename",
    "source_location":"Benson County, North Dakota, USA",
    "source_role":"candidate native exposed culm / old sheath shedding; organ visibility and species identity require visual review",
    "license":"CC BY-SA 2.0","license_url":"https://creativecommons.org/licenses/by-sa/2.0/",
    "site_rule":"photographer describes native americanus in text; DO NOT infer introduced Eurasian based on misleading filename; no genotype confirmation"}))
 except Exception as e: results.append({"status":"HELD","source_page":page,"target":str(ROOT/f"lineage-native-matt-lavin-{num}.jpg"),
                                   "reason":type(e).__name__+": "+str(e)[:350]})
# Preserve earlier good image-level rights evidence even if Wikimedia or iNaturalist
# temporarily returns HTTP 429/5xx on later visits. Never treat a retry failure
# as revocation of an already SHA-verified licensed and attributed local file.
for previous in previous_audit.get("results",[]):
 path=previous.get("archive")
 digest=previous.get("archive_sha256")
 if not path or not digest or not previous.get("license"):continue
 f=pathlib.Path(path)
 if not f.exists() or hashlib.sha256(f.read_bytes()).hexdigest()!=digest:continue
 if any(x.get("archive")==path and x.get("archive_sha256")==digest for x in results):continue
 results.append(dict(previous,status="PREVIOUSLY_ARCHIVED_SOURCE_AND_SHA_VERIFIED",
                     note="Earlier image source/creator/license evidence preserved; archive SHA reverified after later source retry failure"))
REPORT.write_text(json.dumps({"scope":"photo bytes only, NO subspecies identification from photo without additional evidence",
                              "results":results},ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"results":results},ensure_ascii=False))
