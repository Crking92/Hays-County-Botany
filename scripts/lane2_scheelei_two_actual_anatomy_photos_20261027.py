#!/usr/bin/env python3
"""Exact-species pixel-reviewed Setaria scheelei aboveground photo upgrade.
Images checked in source-specific inat research-grade contact sheet and original
JPEGs; install only if original license, species, and bytes pass readback checks.
"""
from pathlib import Path
from urllib.request import Request,urlopen
import json,hashlib,io
from PIL import Image, ImageOps

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"content/taxa/Poaceae/Setaria/setaria-scheelei"
CARD=BASE/"species.json"
REPORT=ROOT/"reports/lane2-scheelei-aboveground-photo-pass-20261027.json"
UA={"User-Agent":"HaysBotanyVisualLearner/1.0 (exact species photo provenance and license validation)"}
PHOTO=[
 {"id":746135170,"obs":406143723,"login":None,"license":"cc-by","creator":"Jane Weeden",
  "file":"jane-weeden-scheelei-external-blade-sheath-746135170.jpg",
  "label":"FIELD PHOTO · real exterior blade–sheath junction (inner ligule NOT exposed)",
  "role":"Outer collar/sheath V-junction with actual green blade and surrounding culm, not inner membranous/ciliate ligule",
  "caption":"Jane Weeden's source-identified Scheele's bristlegrass field photo displays the true outer blade-to-sheath opening and smooth culm; the tiny INNER ligule is concealed. The photo cannot prove a measured ciliate membrane or 1–2 mm hairs. It teaches where to gently bend a leaf back and photograph the inside for identification.",
  "why":"More valuable than another distant head: crews can locate the junction where the species-level ligule must be inspected.",
  "arrows":[{"label":"OUTER blade/sheath junction — not inner ligule","label_x":6,"label_y":52,"target_x":36,"target_y":78}]},
 {"id":728484502,"obs":397188831,"login":None,"license":"cc-by-nc","creator":"Tom Groves",
  "file":"tom-groves-scheelei-attached-pale-spikelets-bristles-728484502.jpg",
  "label":"FLOWERING CLOSEUP · real attached spikelets and long projecting bristles",
  "role":"Flowering axis, pale attached seed-bearing spikelets, and long subtending bristles; no physical mm ruler or isolated lemma",
  "caption":"Tom Groves's photographed flowering head shows numerous pale narrow, attached spikelets and separate projecting bristles along the green central axis. The long bristles are sterile branchlets, not floret awns. No ruler, separated lemma/glumes, or exact per-spikelet insertion count is visible; keep reproductive dissections provisional.",
  "why":"Higher resolution close view for real mature reproductive structure, improving the crew's eye for bristles versus spikelets.",
  "arrows":[{"label":"Visible attached spikelets","label_x":9,"label_y":12,"target_x":51,"target_y":40},
            {"label":"Long projecting bristles","label_x":66,"label_y":80,"target_x":63,"target_y":60}]}
]
def getjson(url):
 with urlopen(Request(url,headers=UA),timeout=40) as h:return json.load(h)
def getphoto(url):
 with urlopen(Request(url,headers=UA),timeout=40) as h:return h.read(10000001)
def main():
 j=json.loads(CARD.read_text())
 assert j["scientific_name"]=="Setaria scheelei"
 gallery=j["visual_comparison"]["items"]
 existing={p["image_url"] for p in gallery}
 if all(f'content/taxa/Poaceae/Setaria/setaria-scheelei/images/{x["file"]}' in existing for x in PHOTO):
  print("ALREADY_INSTALLED: no changes");return
 cache={}
 records=[];new_panels=[];new_images=[]
 for spec in PHOTO:
  id=spec["id"];obs_id=spec["obs"]
  if obs_id not in cache:cache[obs_id]=getjson("https://api.inaturalist.org/v1/observations/"+str(obs_id))["results"][0]
  obs=cache[obs_id]
  if obs.get("quality_grade")!="research" or obs.get("taxon",{}).get("name")!="Setaria scheelei":raise ValueError(f"Species or grade changed {obs_id}")
  p=next((x for x in obs["photos"] if x["id"]==id),None)
  if not p or p.get("license_code")!=spec["license"] or spec["creator"].lower() not in p.get("attribution","").lower():raise ValueError(f"Rights no longer match on photo {id}")
  raw=getphoto(f"https://inaturalist-open-data.s3.amazonaws.com/photos/{id}/original.jpg")
  if len(raw)>10000000:raise ValueError("too many bytes")
  with Image.open(io.BytesIO(raw)) as x:
   if x.format not in ("JPEG","PNG"):raise ValueError("Not a JPEG/PNG")
   im=ImageOps.exif_transpose(x).convert("RGB")
   width,height=im.size
   if width<1000 or height<1000:raise ValueError(f"Insufficient source resolution {id}")
   out=io.BytesIO();im.save(out,"JPEG",quality=91,optimize=True)
  b=out.getvalue()
  dest=BASE/"images"/spec["file"]
  rel="content/taxa/Poaceae/Setaria/setaria-scheelei/images/"+spec["file"]
  if dest.exists() or rel in existing:raise ValueError(f"Partial/conflicting prior install {dest}")
  dest.write_bytes(b)
  license_label={"cc-by":"CC BY 4.0","cc-by-nc":"CC BY-NC 4.0"}[spec["license"]]
  license_url={"cc-by":"https://creativecommons.org/licenses/by/4.0/","cc-by-nc":"https://creativecommons.org/licenses/by-nc/4.0/"}[spec["license"]]
  src="https://www.inaturalist.org/photos/"+str(id)
  profile={
   "creator":spec["creator"],"license":license_label,"license_url":license_url,
   "source_page":src,"source_observation_id":obs_id,"public_reuse":"yes — conditional noncommercial educational website and credit" if spec["license"]=="cc-by-nc" else "yes — CC BY terms",
   "modifications":"Original EXIF/GPS removed by RGB JPEG conversion; browser overlay arrows only",
   "photo_level_verified":"Research Grade correct species and actual individually licensed original image",
   "image_sha256":hashlib.sha256(b).hexdigest(),"original_dimensions_px":[width,height]
  }
  new_images.append({"file":"images/"+spec["file"],"role":spec["role"],**profile})
  new_panels.append({"label":spec["label"],"scientific_name":"Setaria scheelei","image_url":rel,"image_fit":"contain",
    "image_role":spec["role"],"caption":spec["caption"],"why_it_matters":spec["why"],
    "markers":spec["arrows"],"photo_status":"Actual original full-resolution photo pixel inspected; markers only on visible gross organs. Not a measured ligule, root, or true glume dissection.",**profile})
  records.append({"photo_id":id,"observation_id":obs_id,"source":src,"license":license_label,"creator":spec["creator"],
    "original_dimensions_px":[width,height],"bytes_stored":len(b),"sha256":hashlib.sha256(b).hexdigest(),"arrows":len(spec["arrows"])})
 insert=next((i for i,p in enumerate(gallery) if p.get("scientific_name")!="Setaria scheelei"),len(gallery))
 gallery[insert:insert]=new_panels
 j["images"]+=new_images
 j["curation_status"]["lane2_actual_photo_pass_20261027"]={"stage":"FIELD_READY_PHOTO_GAPS","new_local_species_photos":2,"new_photo_supported_arrows":3,
  "archived_same_species_photos":len(j["images"]),"role_improvement":["outside collar/sheath junction, PARTIAL","actual high-resolution spikelet and bristles, PARTIAL"],
  "not_fixed":["true inner ligule","connected rooted growth","glumes/lemmas at mm scale"],"website":"Needs controlled Pages deployment"}
 j["photo_note"]+="\n2026-10-27 Lane2: archived same-species Jane Weeden CC BY full-resolution outer sheath/blade photo and Tom Groves CC BY-NC original spikelet/bristle closeup; 3 gross-only arrows. Not a true ligule or complete root structure."
 REPORT.write_text(json.dumps({"status":"FIELD_READY_PHOTO_GAPS","photos":records,"new_photo_files":2,"new_arrows":3,
  "role_flags":{"sheath_exterior":"PARTIAL","inner_ligule":"MISSING","reproductive_spikelets":"PARTIAL","rooted_base":"MISSING"},
  "license_policy":"workflow/PUBLIC_PHOTO_REUSE_POLICY_20261019.md (noncommercial CC BY-NC conditional)","public_pages_status":"unverified"},indent=2)+"\n")
 CARD.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n")
 print("SAVED",json.dumps(records))
if __name__=="__main__": main()
