#!/usr/bin/env python3
"""Archive source-licensed Paspalum distichum anatomical photographs, including a second ligule angle."""
import io,json,pathlib,urllib.request,urllib.error,urllib.parse,hashlib,time
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Paspalum/paspalum-distichum")
p=base/"species.json"; d=json.loads(p.read_text());assert d["id"]=="paspalum-distichum"
for filename,role in [
 ("Paspalum distichum ligule1 (8251276202).jpg","True membranous ligule at the blade/sheath collar; source reports 0.5–1.5 mm"),
 ("Paspalum distichum spikelets1 (8250207803).jpg","Source-labelled close-up of two-rowed elliptic spikelets; use to distinguish actual spikelets from raceme branches"),
 ("Paspalum distichum ligule2 (8250242625).jpg","Second independently photo-licensed macro showing translucent true inner membranous ligule projecting from the broad green sheath mouth; no 1-mm scale")
]:
 try:
  title="File:"+filename
  url="https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url%7Cextmetadata&format=json&titles="+urllib.parse.quote(title)
  for attempt in range(5):
   try:
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Hays-County-Botany/1.0 (grass field education)"}),timeout=55) as response: pages=json.load(response)["query"]["pages"]
    break
   except urllib.error.HTTPError as e:
    if e.code!=429 or attempt==4: raise
    time.sleep(25*(attempt+1))
  info=next(iter(pages.values()))["imageinfo"][0]
  license=info.get("extmetadata",{}).get("LicenseShortName",{}).get("value","").upper().replace("-","").replace(" ","")
  assert "CCBY2.0" in license,(filename,license)
  for attempt in range(5):
   try:
    with urllib.request.urlopen(urllib.request.Request(info["url"],headers={"User-Agent":"Hays-County-Botany/1.0"}),timeout=70) as response: raw=response.read()
    break
   except urllib.error.HTTPError as e:
    if e.code!=429 or attempt==4: raise
    time.sleep(25*(attempt+1))
  if "8250242625" in filename:
   assert hashlib.sha1(raw).hexdigest()=="40f600583aa8e47a958446fcac4cfb3e0c6acabc", "New ligule2 exact Commons source hash mismatch"
  image=Image.open(io.BytesIO(raw));image.verify()
  image=Image.open(io.BytesIO(raw)).convert("RGB")
  assert image.width>=300 and image.height>=300
  name="harry-rose-"+hashlib.sha256(filename.encode()).hexdigest()[:12]+".jpg"
  dest=base/"images"/name;dest.parent.mkdir(parents=True,exist_ok=True)
  image.save(dest,"JPEG",quality=91,optimize=True)
  page="https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_"))
  record={"file":"images/"+name,"role":role,"creator":"Harry Rose","license":"CC BY 2.0","license_url":"https://creativecommons.org/licenses/by/2.0/","source_page":page,"public_reuse":"Attribution required","photo_status":"PROVISIONAL — USER PHOTO REVIEW PENDING; source-identified anatomy, no new unverified arrows"}
  if "8250242625" in filename:
   record.update({"source_photo_id":"Flickr 8250242625","source_original_sha1":"40f600583aa8e47a958446fcac4cfb3e0c6acabc","archive_sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),"archive_dimensions":[image.width,image.height],"photo_status":"Original 1600x1200 licensed CC BY 2.0 Harry Rose image personally examined via Commons original 2026-10-26: translucent separate projecting free ligule segment visibly rises from sheath mouth; no physical mm scale, so no numeric length inferred.","modifications":"Re-encoded RGB JPEG, EXIF/GPS stripped; arrow is separate browser overlay; photo pixels otherwise not cropped."})
  if not any(x.get("file")==record["file"] or x.get("source_page")==record["source_page"] for x in d.get("images",[])):d["images"].append(record)
  print("ARCHIVED",filename)
 except Exception as e: print("HELD",filename,repr(e))
# The additional full-size ligule2 macro is an independently verified, genuinely distinct
# photographic angle. Append to the END of the gallery to preserve all existing photo
# indices; never append an image entry when the JPEG itself was not downloaded.
new_id="8250242625"
match=next((r for r in d["images"] if new_id in r.get("source_page","")),None)
if match and (base/match["file"]).is_file():
 items=d.setdefault("visual_comparison",{}).setdefault("items",[])
 if not any(new_id in q.get("source_page","") for q in items):
  items.append({
   "label":"TRUE LIGULE, SECOND ANGLE — actual projecting translucent membrane",
   "scientific_name":"Paspalum distichum",
   "image_url":(base/match["file"]).as_posix(),
   "image_fit":"contain",
   "image_role":"Full 1600×1200 real photographed free inner membranous ligule arising behind the green sheath rim, fringed sheath hairs distinguished; no millimeter ruler in frame.",
   "caption":"Harry Rose's separate close-up of the upper grass sheath plainly shows a thin translucent tongue projecting above the sheath rim, plus longer peripheral sheath hairs. This confirms the morphology of a true inner MEMBRANOUS ligule rather than an outer hair tuft; the photographer reports 0.5–1.5 mm, but this unscaled photo cannot verify the numeric height. See original licensed photo, not a diagram.",
   "why_it_matters":"With the existing first ligule macro, gives the crew two genuine source-identified angles of the free membrane; rooting aboveground stolons and mature glume/lemma dissection remain missing.",
   "creator":"Harry Rose (Macleay Grass Man)",
   "license":"CC BY 2.0",
   "license_url":"https://creativecommons.org/licenses/by/2.0/",
   "source_page":match["source_page"],
   "original_flickr":"https://www.flickr.com/photos/73840284@N04/8250242625",
   "modifications":"Re-encoded RGB JPEG with EXIF/GPS removed; browser annotation separate, no crop.",
   "markers":[{"label":"Real projecting membranous ligule — not hairs","label_x":3,"label_y":13,"target_x":54,"target_y":34}],
   "photo_status":"2026-10-26: source original visually checked; exact 1600x1200 Commons SHA1 enforced by archive script, CC BY 2.0 separately verified via FlickreviewR; gross ligule arrow only, no millimeter measurement or claim of soil-rooting stolon."
  })
  d.setdefault("field_id_finish_pass",{}).setdefault("lane4_ligule2_archive_20261026",{}).update({
   "new_original_photo":match["file"],
   "licensed_source":match["source_page"],
   "new_panel_gallery_index":len(items)-1,
   "photo_rights":"Harry Rose original CC BY 2.0 source verified via Wikimedia Commons FlickreviewR, attribution and adaptation notice retained",
   "image_source_sha1":match.get("source_original_sha1"),
   "image_archive_sha256":match.get("archive_sha256"),
   "photo_role":"Actual exposed free ligule, second angle. Published 0.5–1.5mm but UNMEASURED; no ruler in this image.",
   "visible_only_new_arrows":1,
   "remaining":["Live aboveground surface stolon actually rooting into wet soil","Calibrated free ligule height","Dissected spikelet glumes/sterile-fertile lemmas","Live Pages/mobile QA"],
   "stage":"FIELD_READY_PHOTO_GAPS"
  })
  print("INSTALLED ligule2 real gallery panel",len(items)-1)
else:
 print("HELD ligule2 gallery because verified JPEG missing")
d.setdefault("curation_status",{})["photo_metadata_count"]=len(d["images"])
d["curation_status"]["photo_files_present"]=sum(str(x.get("file","")).startswith("images/") for x in d["images"])
d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
