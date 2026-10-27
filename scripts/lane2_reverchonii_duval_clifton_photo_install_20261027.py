#!/usr/bin/env python3
"""Install two exact-species same-observation Clifton Ladd Duval field photographs.
Original pixels reviewed in Lane 2 2026-10-27 run 40525994845; gross arrows only.
"""
from pathlib import Path
from urllib.request import urlopen,Request
from PIL import Image,ImageOps
import json,hashlib,io
ROOT=Path(__file__).resolve().parents[1];B=ROOT/"content/taxa/Poaceae/Setaria/setaria-reverchonii"
CARD=B/"species.json";REPORT=ROOT/"reports/lane2-reverchonii-duval-whole-attached-head-20261027.json"
OBS=372988761;UA={"User-Agent":"HaysBotanyVisualLearner/1.0 exact photo-level licensed original"}
DATA=[
{"photo":681610420,"file":"clifton-ladd-duval-living-flowering-tuft-681610420.jpg",
 "label":"DUVAL COUNTY · one living tuft with narrow blades and attached green flowering heads",
 "role":"Real field-growing clump with multiple above-ground culms, leaves and attached sparse flowering panicles; soil-surface rooting connection partially covered by photographer's hand",
 "caption":"Clifton Ladd photographed Setaria reverchonii in Duval County, Texas. The living tuft has several narrow blades emerging low on the shoots and at least three upright, interrupted green flowering heads. The hand holds basal culms together; it does NOT expose actual nodal rhizomes, fibrous roots or inner ligule. This same observation supplies the next closer photo.",
 "why":"A real same-specimen whole-plant context, unlike the prior isolated seedhead close-ups: crew can see vegetative growth AND its distinctive interrupted flowering architecture together.",
 "markers":[{"label":"Attached slender flowering heads","label_x":68,"label_y":12,"target_x":59,"target_y":44},
            {"label":"Tuft of narrow blades (roots hidden)","label_x":6,"label_y":81,"target_x":51,"target_y":88}]},
{"photo":681610423,"file":"clifton-ladd-duval-attached-spikelets-681610423.jpg",
 "label":"DUVAL COUNTY · matched flowering head showing widely separated green spikelets",
 "role":"Actual attached spikelet-bearing axes from the same verified field observation as the whole tuft; glumes, bristle attachment and lengths not resolved",
 "caption":"Close view by Clifton Ladd of the SAME species and observation as the living tuft photo. Narrow green heads show separated oval spikelets along small branched portions of the flowering axes. Fingers or foliage are not a millimeter ruler; do not count sterile-branch bristles or label individual glumes without dissection.",
 "why":"Provides field-to-detail matching from one documented observation for crew learners.",
 "markers":[{"label":"Separated attached green spikelets","label_x":74,"label_y":12,"target_x":60,"target_y":44}]}
]
def fetch(url):
 with urlopen(Request(url,headers=UA),timeout=45) as h: return h.read(10000001)
def main():
 j=json.loads(CARD.read_text());assert j["scientific_name"]=="Setaria reverchonii"
 photo_ids={p["image_url"] for p in j["visual_comparison"]["items"]}
 if all("content/taxa/Poaceae/Setaria/setaria-reverchonii/images/"+p["file"] in photo_ids for p in DATA):
  print("ALREADY_INSTALLED");return
 response=json.loads(fetch(f"https://api.inaturalist.org/v1/observations/{OBS}"))["results"][0]
 assert response["taxon"]["name"]=="Setaria reverchonii" and response["quality_grade"]=="research"
 new_p=[];new_i=[];report=[]
 for a in DATA:
  p=next((p for p in response["photos"] if p["id"]==a["photo"]),None)
  if p is None or p.get("license_code")!="cc-by" or "Clifton Ladd" not in p.get("attribution",""):raise RuntimeError(f"Photo rights/taxon uncertainty: {a['photo']}")
  b=fetch(f"https://inaturalist-open-data.s3.amazonaws.com/photos/{a['photo']}/original.jpg")
  if len(b)>10000000:raise RuntimeError("Too large")
  with Image.open(io.BytesIO(b)) as img:
   assert img.format=="JPEG";im=ImageOps.exif_transpose(img).convert("RGB");dim=list(im.size)
   if min(dim)<1000:raise RuntimeError("Insufficient source dimensions")
   f=io.BytesIO();im.save(f,format="JPEG",quality=89,optimize=True)
  data=f.getvalue()
  local=B/"images"/a["file"]
  if local.exists():raise RuntimeError(f"Existing unexpected archive: {local}")
  local.write_bytes(data)
  url="https://www.inaturalist.org/photos/"+str(a["photo"])
  rel="content/taxa/Poaceae/Setaria/setaria-reverchonii/images/"+a["file"]
  meta={"creator":"Clifton Ladd, C.W.B.","license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/",
    "source_page":url,"source_observation":"https://www.inaturalist.org/observations/"+str(OBS),
    "public_reuse":"yes — CC BY 4.0 attribution", "modifications":"EXIF/GPS removed by JPEG RGB re-encode; only separate CSS/SVG overlay arrows",
    "original_dimensions_px":dim,"sha256":hashlib.sha256(data).hexdigest()}
  new_i.append({"file":"images/"+a["file"],"role":a["role"],**meta})
  new_p.append({"label":a["label"],"scientific_name":"Setaria reverchonii","image_url":rel,
     "image_fit":"contain","image_role":a["role"],"caption":a["caption"],"why_it_matters":a["why"],
     "markers":a["markers"],"photo_status":"Original pixels manually inspected on 2026-10-27; gross visible structures only, no identified inner ligule/roots/individual glumes.",**meta})
  report.append({"photo_id":a["photo"],"source":url,"stored_image":rel,"bytes":len(data),"sha256":meta["sha256"],"dimensions":dim,"arrows":len(a["markers"])})
 ix=next((i for i,p in enumerate(j["visual_comparison"]["items"]) if p.get("scientific_name")!="Setaria reverchonii"),len(j["visual_comparison"]["items"]))
 j["visual_comparison"]["items"][ix:ix]=new_p;j["images"]+=new_i
 j["visual_comparison"]["subtitle"]="Five local archive exact-species photos including matched Duval County flowering tuft and visible attached spikelets. Inner ligule, actual connected roots and measured glume/sterile bristle insertions remain missing."
 j["curation_status"]["lane2_reverchonii_attached_whole_field_20261027"]={"status":"FIELD_READY_PHOTO_GAPS","new_archived_jpegs":2,"new_arrows":3,"total_species_photos":len(j["images"]),"whole_plant_habit":"PRESENT — field-growing tuft and attached heads in same view","reproductive_detail":"PARTIAL — matched same-observation spikelets but no separated glumes or mm-scale","true_ligule":"MISSING","root_growth":"MISSING","pages":"not independently verified"}
 j["photo_note"]+="\n2026-10-27 Lane2: 2 full-resolution CC BY Clifton Ladd Duval county research grade photos archived, with 3 gross only arrows, authentic flowering tuft + matched attached spikelet closeup, no claim to roots, ligule or glume dissection."
 REPORT.write_text(json.dumps({"species":"Setaria reverchonii","observation":OBS,"source_locality":"Duval County, Texas","photos":report,"new_photos":2,"new_arrows":3,"status":"FIELD_READY_PHOTO_GAPS","publication":"await controlled Pages preflight"},indent=2)+"\n")
 CARD.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n")
 print("ARCHIVE_COMPLETED",json.dumps(report))
if __name__=="__main__":main()
