import io,json,re,html,pathlib,urllib.parse,urllib.request,hashlib
from PIL import Image
p=pathlib.Path("content/taxa/Poaceae/Poa/poa-annua/species.json");s=json.loads(p.read_text());results=[]
def get(u):
 req=urllib.request.Request(u,headers={"User-Agent":"HaysBotany/1.0 Commons archival"})
 with urllib.request.urlopen(req,timeout=45) as f:return f.read()
for panel in s["visual_comparison"]["items"]:
 source=panel.get("source_page","")
 if source not in ["https://commons.wikimedia.org/wiki/File:Annual_Bluegrass_(1294505418).jpg","https://commons.wikimedia.org/wiki/File:Poa_annua_(subsp._annua)_sl11.jpg"]:continue
 if any(im.get("source_page")==source for im in s["images"]):continue
 try:
  name=urllib.parse.unquote(source.split("File:",1)[1]).replace("_"," ")
  url="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({"action":"query","prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":"1600","titles":"File:"+name,"format":"json"})
  info=next(iter(json.loads(get(url))["query"]["pages"].values()))["imageinfo"][0];md=info["extmetadata"]
  lic=re.sub("[^A-Z0-9]","",md.get("LicenseShortName",{}).get("value","").upper())
  artist=html.unescape(re.sub("<[^>]*>","",md.get("Artist",{}).get("value","")))
  expected="CCBY20" if "Annual_Bluegrass_" in source else "CCBYSA40"
  author="Jason Hollinger" if "Annual_Bluegrass_" in source else "Stefan"
  if lic!=expected or author.lower() not in artist.lower():raise ValueError("rights/artist hold: "+lic+" "+artist)
  raw=get(info.get("thumburl") or info["url"]);im=Image.open(io.BytesIO(raw));im.verify();im=Image.open(io.BytesIO(raw)).convert("RGB")
  if min(im.size)<350:raise ValueError("insufficient pixels")
  dst=p.parent/"images"/("commons-poa-annua-"+hashlib.sha256(source.encode()).hexdigest()[:12]+".jpg");im.save(dst,"JPEG",quality=90,optimize=True)
  panel["previous_external_image_url"]=panel["image_url"];panel["image_url"]=str(dst);panel["photo_status"]="Source and image license verified; local JPEG archived, EXIF removed; previous gross arrows kept for site alignment QA."
  s["images"].append({"file":"images/"+dst.name,"role":panel["image_role"],"creator":panel["creator"],"license":panel["license"],"license_url":panel.get("license_url"),"source_page":source,"photo_status":"LOCAL ARCHIVE; microscopy not independently specimen vouched"})
  results.append({"source":source,"file":str(dst),"status":"archived"})
 except Exception as exc:results.append({"source":source,"status":"held","reason":str(exc)[:160]})
if any(x["status"]=="archived" for x in results):
 s["field_id_finish_pass"]["lane5_annua_commons_archive_20261023"]={"results":results,"status":"FIELD_READY_PHOTO_GAPS","remaining":"Local rooted crown and mature bisexual floret with proper magnification and scale; no unseen microscopic arrows"}
 p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n")
pathlib.Path("reports/lane5-poa-annua-open-20261023.json").write_text(json.dumps(results,indent=2)+"\n")
print(json.dumps(results))

# ROOT_ADDENDUM_20261027 — one genuinely exposed, open-license fibrous root system
# Leave palea/lemma microscopy and absent-rhizome inference unverified.
import csv
root_page="https://commons.wikimedia.org/wiki/File:2011-03-22_Poa-annua-roots.JPG"
root_rel="images/sten-porse-poa-annua-exposed-fibrous-roots-ccby-sa30.jpg"
root_image=p.parent/root_rel
if not any(im.get("source_page")==root_page or im.get("file")==root_rel for im in s["images"]):
 try:
  meta_url="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({
   "action":"query","prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":"1800",
   "titles":"File:2011-03-22 Poa-annua-roots.JPG","format":"json"})
  info=next(iter(json.loads(get(meta_url))["query"]["pages"].values()))["imageinfo"][0]
  extra=info["extmetadata"]
  license_raw=html.unescape(re.sub("<[^>]+>","",extra.get("LicenseShortName",{}).get("value","")))
  license_normalized=re.sub("[^A-Z0-9]","",license_raw.upper())
  artist=html.unescape(re.sub("<[^>]+>","",extra.get("Artist",{}).get("value","")))
  if not license_normalized.startswith("CCBYSA30") or "sten" not in artist.lower():
   raise ValueError("Rights/author mismatch: "+license_raw+" / "+artist)
  raw=get(info.get("thumburl") or info["url"])
  im=Image.open(io.BytesIO(raw)); im.verify()
  im=Image.open(io.BytesIO(raw)).convert("RGB")
  if min(im.size)<700:raise ValueError("Insufficient root-photo pixel dimensions")
  im.thumbnail((1800,1800))
  im.save(root_image,"JPEG",quality=89,optimize=True) # strips original GPS/EXIF
  clean=root_image.read_bytes()
  with Image.open(io.BytesIO(clean)) as im2:
   im2.verify()
  with Image.open(root_image) as im2:
   if im2.getexif():raise ValueError("EXIF metadata unexpectedly retained")
  src_image=info.get("thumburl") or info["url"]
  role="Real source-labelled Poa annua vegetative plant with exposed attached fibrous roots and visible leafy basal crown; flower panicle, absence of rhizomes, and Hays County specimen identity not established."
  s["images"].append({
   "file":root_rel,"role":role,"creator":"Sten Porse","license":"CC BY-SA 3.0",
   "license_url":"https://creativecommons.org/licenses/by-sa/3.0/",
   "source_page":root_page,"source_original_url":info["url"],"downloaded_from":src_image,
   "source_region":"Denmark (original source), not Texas",
   "photo_status":"Root and basal leafy crown are visually apparent in source preview, exact taxon determined by original photographer. Original EXIF/GPS stripped on new archive; do not claim root-to-panicle same plant voucher.",
   "public_reuse":"CC BY-SA 3.0; cite Sten Porse/source/license and state re-encoding modification.",
   "sha256":hashlib.sha256(clean).hexdigest(),"dimensions_px":list(im.size)})
  i=len(s["visual_comparison"]["items"])
  s["visual_comparison"]["items"].append({
   "label":"ANNUAL BLUEGRASS — ACTUAL EXPOSED FIBROUS ROOTS AND LEAFY CROWN",
   "scientific_name":"Poa annua","image_url":str(root_image),"image_fit":"contain",
   "image_role":role,
   "caption":"Source-identified Poa annua pulled aside at a stone edge, revealing long white fibrous roots connected to a green leafy crown. This is a Danish vegetative plant, not a Hays County flowering voucher. No visible root system alone proves a complete absence of rhizomes.",
   "why_it_matters":"Shows what an actual tuft, attached crown and fibrous root system look like, complementing the already stored leaf-tip, ligule and flowering photos; compare separately with the perennial rhizomatous native Poa arachnifera.",
   "creator":"Sten Porse","license":"CC BY-SA 3.0",
   "license_url":"https://creativecommons.org/licenses/by-sa/3.0/",
   "source_page":root_page,
   "modifications":"Resized/re-encoded JPEG; removed EXIF/GPS; browser overlays, original source image itself not annotated.",
   "photo_status":"OPEN-LICENSE SOURCE VERIFIED; EXPOSED ROOTS VISIBLE; REGION NOT TEXAS; NO MICRO-ANATOMY CLAIM",
   "markers":[
     {"label":"Leafy basal crown","label_x":69,"label_y":15,"target_x":48,"target_y":40},
     {"label":"Exposed fibrous roots","label_x":4,"label_y":74,"target_x":42,"target_y":64}]})
  for ix in (0,5):
   tiles=s.get("field_id_short_tiles",[])
   if len(tiles)>ix:
    tiles[ix].setdefault("photo_panel_indices",[])
    if i not in tiles[ix]["photo_panel_indices"]:tiles[ix]["photo_panel_indices"].append(i)
  s["field_photo_quickcheck"].setdefault("featured_photo_indices",[])
  if i not in s["field_photo_quickcheck"]["featured_photo_indices"]:
   s["field_photo_quickcheck"]["featured_photo_indices"].append(i)
  s["curation_status"]["photo_metadata_count"]=len(s["images"])
  s["curation_status"]["photo_files_present"]=len(s["images"])
  s["learner_visual_status"]["image_count"]=len(s["images"])
  s["learner_visual_status"]["status"]="field_ready_photo_gaps"
  s["learner_visual_status"]["note"]="Six physical species JPEGs with a new verified CC BY-SA 3.0 source-identified rooted vegetative crown from Denmark; FIVE teaching panels. True local connected flowering/root specimen, mature measured separated glumes/lemmas/palea and verified bisexual floret remain unresolved. Pages rendering not verified."
  s["curation_status"]["visual_finish"]="FIELD_READY_PHOTO_GAPS — six real exact-source images, five educational panels; newly archived root system/crown not paired to flowering culm, so rhizome absence not certified. Detailed measured reproductive anatomy pending."
  s["field_id_short_tiles"][5]["short"]="FIELD_READY_PHOTO_GAPS: six source-identified JPEGs and five teaching panels, plus critical local root-to-floret confirmation remaining."
  s["field_id_short_tiles"][5]["details"]=s["field_id_short_tiles"][5]["details"].replace(
     "five historical image records, four teaching panels","six locally archived images and five teaching panels").replace(
     "all five archived records and four existing teaching panels","all six archived records and five teaching panels")
  s.setdefault("field_id_finish_pass",{})["lane5_poa_annua_real_roots_20261027"]={
   "status":"FIELD_READY_PHOTO_GAPS","root_source":root_page,
   "gallery_index":i,"new_arrows":2,"rooted_plant_not_floriferous":True,
   "missing":"Hays connected root-to-flowering whole voucher, measured separate mature glume/lemma/palea, bisexual floret and live Pages QA"}
  p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n")
  results.append({"source":root_page,"file":str(root_image),"status":"archived","pixels":list(im.size),"sha256":hashlib.sha256(clean).hexdigest(),"gallery_index":i,"new_markers":2,"creator":"Sten Porse","license":"CC BY-SA 3.0"})
 except Exception as e:
  root_image.unlink(missing_ok=True)
  results.append({"source":root_page,"status":"HELD","reason":str(e)[:300]})
else:
 results.append({"source":root_page,"status":"ALREADY_ARCHIVED"})
# Reconcile previously incomplete ledger without changing source rights or inventing permissions.
ledger=p.parent/"image-sources.csv"
with ledger.open(newline="") as fh:
 reader=csv.DictReader(fh);fields=reader.fieldnames;rows=list(reader)
existing={row.get("file_name") for row in rows}
for im in s["images"]:
 name=pathlib.Path(im["file"]).name
 if name in existing:continue
 row={k:"" for k in fields}
 vals={"file_name":name,"role":im.get("role",""),"creator":im.get("creator",""),
       "license":im.get("license",""),"source_page":im.get("source_page",""),
       "direct_url":im.get("source_original_url",im.get("downloaded_from","")),
       "study_use":"Source-attributed botanical learner",
       "public_reuse":im.get("public_reuse","Verify recorded original photo-specific license and relevant sharing terms")}
 for key,val in vals.items():
  if key in row:row[key]=val
 rows.append(row);existing.add(name)
with ledger.open("w",newline="") as fh:
 writer=csv.DictWriter(fh,fieldnames=fields);writer.writeheader();writer.writerows(rows)
pathlib.Path("reports/lane5-poa-annua-open-20261023.json").write_text(json.dumps({
 "date":"2026-10-27","photo_results":results,"ledger_rows":len(rows),
 "status":"FIELD_READY_PHOTO_GAPS","remaining":"True flowering rooted voucher and calibrated floret dissection"
},indent=2)+"\n")
print(json.dumps({"root_and_source_ledger":results,"ledger_rows":len(rows)}))
