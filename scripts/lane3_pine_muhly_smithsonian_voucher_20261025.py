#!/usr/bin/env python3
"""Save exact-source CC0 Smithsonian pine-muhly voucher image and provenance.
This is a *pressed specimen*, not proof of 1-mm ligule or dissected floret.
"""
import json,pathlib,urllib.request,io,hashlib
from PIL import Image,ImageOps
root=pathlib.Path("content/taxa/Poaceae/Muhlenbergia/muhlenbergia-dubia")
species=root/"species.json"
d=json.loads(species.read_text());assert d["id"]=="muhlenbergia-dubia"
rpt={"added":[],"holds":[],"target":"GBIF 4418651350 / Smithsonian US 3771355"}
try:
 sources=json.loads(pathlib.Path("reports/lane3-pine-muhly-voucher-rights-20261025.json").read_text())
 v=next(x for x in sources["smithsonian"] if x.get("key")==4418651350)
 assert v.get("scientific")=="Muhlenbergia dubia E.Fourn.",v.get("scientific")
 assert v.get("basis")=="PRESERVED_SPECIMEN" and v.get("institution")=="US"
 assert "publicdomain/zero" in v.get("license","")
 photo=v["media"][0]
 assert "publicdomain/zero" in photo["license"] and photo["creator"]=="Ingrid P. Lin"
 img_url=photo["identifier"]
 req=urllib.request.Request(img_url,headers={"User-Agent":"HaysBotanyVisualLearner/1.0 (Smithsonian Open Access credited specimen research; github.com/Crking92/Hays-County-Botany)"})
 with urllib.request.urlopen(req,timeout=40) as response:raw=response.read(12000001)
 with Image.open(io.BytesIO(raw)) as im:im.verify()
 with Image.open(io.BytesIO(raw)) as im:
  im=ImageOps.exif_transpose(im).convert("RGB")
  if min(im.size)<800:raise ValueError("Voucher scanned image too low resolution")
  original=list(im.size);im.thumbnail((2400,3000))
  mem=io.BytesIO();im.save(mem,"JPEG",quality=87,optimize=True);blob=mem.getvalue()
 rel="images/smithsonian-us3771355-vouchered-cc0.jpg"
 path=root/rel
 if path.exists():raise ValueError("Archive destination already present; no overwriting")
 if any("4418651350" in json.dumps(a) for a in d["images"]):raise ValueError("GBIF voucher already linked")
 path.write_bytes(blob)
 row={"file":rel,"role":"Certified museum herbarium specimen reference with collection accession US 3771355. Pressed flowering material and herbarium label; individual ligule/glume/lemma pixel identities NOT inspected.","creator":"Smithsonian NMNH herbarium; specimen image by Ingrid P. Lin","license":"CC0 1.0","license_url":"https://creativecommons.org/publicdomain/zero/1.0/","source_page":"https://www.gbif.org/occurrence/4418651350","specimen_institution":"National Museum of Natural History, US National Herbarium (US)","specimen_catalog":"US 3771355","original_source_photo_url":img_url,"source_taxon_name":v["scientific"],"verified_source_basis":"PRESERVED_SPECIMEN","archive_sha256":hashlib.sha256(blob).hexdigest(),"original_dimensions":original,"license_verification":"GBIF record and attached specimen-media license both CC0","public_reuse":"CC0 1.0, public website cleared; credit Smithsonian and Ingrid P. Lin retained","photo_review":"A registered source-determined dried specimen. Does not certify the independent identity of earlier needs-ID iNaturalist photos or a measured ligule."}
 d["images"].append(row)
 d["visual_comparison"]["items"].append({"label":"SPECIMEN CHECK — Smithsonian US 3771355 pine muhly voucher","scientific_name":"Muhlenbergia dubia","image_url":str(root/rel),"image_fit":"contain","image_role":"Institutionally catalogued source-labelled PRESERVED SPECIMEN; no microscopic dissection claimed","caption":"Smithsonian US National Herbarium voucher US 3771355. Image Ingrid P. Lin, CC0. Cross-check the pressed habit and inflorescence; not a measured ligule or separated glumes/lemma. Does NOT authenticate unrelated provisional iNaturalist photos.","why_it_matters":"Provides independent museum-vouchered reference for the species when field close-up photographs have unresolved Needs-ID determinations.","creator":"Smithsonian NMNH / Ingrid P. Lin","license":"CC0 1.0","source_page":"https://www.gbif.org/occurrence/4418651350","photo_status":"CC0_ARCHIVED_INSTITUTIONAL_VOUCHER__ANATOMY_PIXEL_REVIEW_HOLD","markers":[]})
 d["curation_status"]["photo_files_present"]=sum(x.get("file","").startswith("images/") for x in d["images"])
 d["curation_status"]["photo_metadata_count"]=len(d["images"])
 d["learner_visual_status"]["image_count"]=len(d["images"])
 d["learner_visual_status"]["status"]="FIELD_READY_PHOTO_GAPS"
 d["learner_visual_status"]["note"]="Six physically stored publicly licensed photographs: two prior habit images, three source-reported Needs-ID close-ups, one independent CC0 Smithsonian herbarium voucher US 3771355. Vouchered specimen is a comparator, not proof of earlier source IDs, nor a measured membrane/glume/lemma."
 d["lane3_voucher_anchor_20261025"]={"catalog":"US 3771355","gbif_key":4418651350,"license":"CC0 1.0","status":"PUBLIC_VOUCHER_REFERENCE_ONLY__NOT_MICRO_COMPLETE","source_photo_rights":"Smithsonian specimen and media license CC0","source_identification_hold":"Registered source taxon M. dubia; earlier three close-up field photos remain iNaturalist Needs ID.","photo_anatomy_hold":"True scale measured attached ligule, separate glumes/lemma and deergrass matched comparison still require expert-verified microscopic photographs.","native_county_hold":"Do not infer Hays County native occurrence from Mexico or outside-Hays voucher."}
 species.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
 rpt["added"].append({"file":str(path),"sha256":hashlib.sha256(blob).hexdigest(),"bytes":len(blob),"dimensions":original,"rights":"CC0 1.0"})
except Exception as e:rpt["holds"].append(str(e)[:360])
pathlib.Path("reports/lane3-pine-muhly-voucher-archive-20261025.json").write_text(json.dumps(rpt,indent=2)+"\n")
print(json.dumps(rpt))
