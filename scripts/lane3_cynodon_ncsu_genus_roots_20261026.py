#!/usr/bin/env python3
"""Archive explicitly GENERIC rooted Cynodon shoots, CC BY-NC 2.0 NC State photo.
No false species attribution and no claimed underground rhizome identity.
"""
import io,json,hashlib,pathlib,urllib.request
from PIL import Image,ImageOps
root=pathlib.Path("content/taxa/Poaceae/Cynodon/cynodon-dactylon")
card=root/"species.json"
report=pathlib.Path("reports/lane3-cynodon-ncsu-rooted-turf-reference-20261026.json")
site="https://plants.ces.ncsu.edu/plants/cynodon/"
source="https://s3.amazonaws.com/eit-planttoolbox-prod/media/images/Cynodon_form_Scott_Z_n9KMXxw0VMxL.jpeg"
relative="images/scott-zona-cynodon-genus-rooted-shoots-ncsu-nc2.jpg"
dest=root/relative
rights="https://creativecommons.org/licenses/by-nc/2.0/"
result={"status":"HOLD","species_card":"cynodon-dactylon","source":site,"image_source":source,"rights":"Scott Zona, CC BY-NC 2.0","scientific_source_precision":"Cynodon genus page, photo of rhizomatous shoots potentially turf hybrid, NOT pure Cynodon dactylon voucher","added":[],"holds":[]}
def get(url,maxbytes=14000000):
 req=urllib.request.Request(url,headers={"User-Agent":"Hays-Botany-Botanical-Education/1.0 (github.com/Crking92/Hays-County-Botany; original author credit kept)","Accept":"image/jpeg,image/*,text/html"})
 with urllib.request.urlopen(req,timeout=40) as h:
  mime=h.headers.get("content-type","")
  b=h.read(maxbytes+1)
 assert len(b)<=maxbytes
 return mime,b
try:
 d=json.loads(card.read_text())
 assert d["id"]=="cynodon-dactylon"
 assert not any(x.get("file")==relative for x in d["images"]), "Already archived; no duplicate"
 assert not dest.exists(), "Already archived, don't overwrite"
 mime,html=get(site,maxbytes=3000000)
 page=html.decode("utf8",errors="replace")
 if "Scott Zona" not in page or "CC BY-NC 2.0" not in page or "Cynodon_form_Scott_Z" not in page:
  raise ValueError("NC State photo-specific creator/license/photo match not established")
 mime,blob=get(source)
 if not ("image" in mime or blob[:3]==b"\xff\xd8\xff"):raise ValueError("No image MIME")
 with Image.open(io.BytesIO(blob)) as im:
  assert im.format=="JPEG"
  im.verify()
 with Image.open(io.BytesIO(blob)) as im:
  im=ImageOps.exif_transpose(im).convert("RGB")
  assert min(im.size)>400
  dims=list(im.size)
  im.thumbnail((1800,1800),Image.Resampling.LANCZOS)
  buf=io.BytesIO()
  im.save(buf,"JPEG",quality=90,optimize=True)
  jpg=buf.getvalue()
 with Image.open(io.BytesIO(jpg)) as im:
  assert not im.getexif().get(34853)
  im.verify()
 dest.parent.mkdir(parents=True,exist_ok=True)
 dest.write_bytes(jpg)
 sha=hashlib.sha256(jpg).hexdigest()
 d["images"].append({
  "file":relative,"role":"OTHER TAXON OR UNSPECIFIED CYDONON GENUS PHOTO REFERENCE — real roots on creeping stems, source may depict Cynodon hybrid; never count as C. dactylon exact photo",
  "creator":"Scott Zona","license":"CC BY-NC 2.0","license_url":rights,
  "source_page":site,"source_image_url":source,"source_taxon_precision":"Cynodon (not pure Cynodon dactylon confirmed)",
  "photo_status":"NCSU photo original physically archived and credited; shows connected nodes/root shoots but distinction rhizome/stolon, pure species identity and mm scale not certified",
  "public_reuse":"CONDITIONAL NONCOMMERCIAL public botanical education only, proper Scott Zona source+license and adaptation notice",
  "original_sha256":hashlib.sha256(blob).hexdigest(),"archived_sha256":sha,
  "source_dimensions":dims,"modifications":"Original RGB resized and reencoded JPEG with GPS/EXIF removed; no image edits or pixel arrows"
 })
 panel={"label":"CYNODON GENUS COMPARISON ONLY — creeping shoot with real node roots",
    "scientific_name":"Cynodon spp. (hybrid/unknown turf possible)",
    "image_url":str(root/relative),"image_fit":"contain",
    "image_role":"DIFFERENT or UNRESOLVED TAXON: photographed creeping connected shoots and actual roots, NOT a voucher-proven wild Cynodon dactylon photo and NOT definitive true underground rhizome photo.",
    "caption":"Scott Zona's image on NC State Extension Cynodon (Bermuda turf/hybrid) shows slender connected shoots, blades and roots emerging near stem nodes. This is NOT identified as pure C. dactylon in its source and cannot tell which segments were originally belowground; inspect exact specimen and soil context before calling anything a rhizome.",
    "why_it_matters":"A true licensed photographic example of nodal rooting missing from our exact-species archive. It teaches what connected roots look like without falsely claiming the exact species or buried stem.",
    "creator":"Scott Zona","license":"CC BY-NC 2.0","license_url":rights,
    "source_page":site,"source_image_url":source,
    "photo_status":"PHYSICALLY ARCHIVED licensed comparative reference; C. dactylon four-role rooted-node and rhizome PHOTO GAP REMAINS OPEN; no arrows until user-visible original inspected","markers":[]}
 assert not any(x.get("source_image_url")==source for x in d["visual_comparison"]["items"])
 d["visual_comparison"]["items"].append(panel)
 d["curation_status"]["photo_metadata_count"]=len(d["images"])
 d["curation_status"]["photo_files_present"]=sum(x.get("file","").startswith("images/") for x in d["images"])
 d["curation_status"]["lane3_scott_zona_cynodon_genus_20261026"]="Source-rights verified NCSU Scott Zona CC BY-NC 2.0 generic Cynodon turf rooted shoot comparison physically archived; species-diagnostic C. dactylon rooted node/rhizome remains unfilled; no photo arrows yet."
 d["learner_visual_status"]["image_count"]=len(d["images"])
 d["field_id_finish_pass"]["genus_rooted_shoot_comparison_20261026"]={
    "source_page":site,"source_author":"Scott Zona","license":"CC BY-NC 2.0","taxon":"Cynodon genus hybrid/unknown",
    "status":"OTHER-TAXON GROWTH-STRUCTURE REFERENCE ONLY, NOT A FOUR-ROLE SPECIES FINISH",
    "true_exact_species_gaps":["Species-authenticated rooted stolon node with 1-mm scale","Actual exposed subterranean rhizome with intact bud, scale leaf, and attached plant"] }
 card.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
 result.update({"status":"ARCHIVED_GENUS_REFERENCE_NOT_EXACT_SPECIES","added":[{"local_file":str(dest),"sha256":sha,"dimensions":dims,"creator":"Scott Zona","license":"CC BY-NC 2.0"}],"card_image_records":len(d["images"]),"gallery_panels":len(d["visual_comparison"]["items"])})
except Exception as e:result["holds"].append(str(e)[:300])
report.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
print(json.dumps(result,indent=2))
