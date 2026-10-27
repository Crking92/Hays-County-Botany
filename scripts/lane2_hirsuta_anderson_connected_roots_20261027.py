#!/usr/bin/env python3
"""Licensed exact-species full-flowering and attached root-crown photos, Eragrostis hirsuta.
TgarrisonPlateau research-grade observation, real original pixels separately inspected.
"""
from pathlib import Path
from urllib.request import Request,urlopen
import io,json,hashlib
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"content/taxa/Poaceae/Eragrostis/eragrostis-hirsuta"
CARD=BASE/"species.json"
REPORT=ROOT/"reports/lane2-eragrostis-hirsuta-anderson-flowering-roots-20261027.json"
OBS=241215433
UA={"User-Agent":"HaysBotanyVisualLearner/1.0 verified image-level license and species"}
PHOTOS=[
{"id":429865923,"file":"tgarrison-anderson-bigtop-whole-flowering-rooted-429865923.jpg",
"label":"TEXAS · entire flowering clump with leafy culms and actual root crown",
"role":"One pulled-up source-identified field plant connects tufted leaves to branching airy panicle and visibly attached fine roots, with hand scale; true ligule too small to resolve.",
"caption":"Original Anderson County Eragrostis hirsuta photograph by TgarrisonPlateau. Follow the fine, cloudlike upper branching panicle down to the long basal blades and the actual dense crown held in the hand. Fibrous roots hang beneath that SAME tuft. This is rooted growth evidence, not evidence of rhizomes or a measured inner ligule. Flowerhead and root connection are from the same photographed plant.",
"why":"One of the strongest complete form photographs found for this species, directly joining field habit, flowering and rooting instead of unrelated closeups.",
"arrows":[{"label":"Fine airy attached flowering branches","label_x":5,"label_y":18,"target_x":56,"target_y":25},
          {"label":"Leafy tuft, rooted growth base","label_x":73,"label_y":71,"target_x":51,"target_y":76},
          {"label":"Attached fine roots, beneath crown","label_x":11,"label_y":91,"target_x":52,"target_y":86}]},
{"id":429865942,"file":"tgarrison-anderson-bigtop-connected-fibrous-root-crown-429865942.jpg",
"label":"TEXAS · closer actual crown, attached basal shoots and fibrous roots",
"role":"Source-identified flowering specimen close-up showing green blade bases, brown sheaths and connected hanging roots below shoot crown; do not mistake split older sheaths for underground rhizomes.",
"caption":"Same Anderson County individual and observation, held up for a closer view of the lower clump. Living basal blades insert above dry brown overlapping old sheaths. The darker crown and long narrow fibrous roots are actually attached to this plant. No dug-out creeping rhizomes or opened 0.5-mm ligule are demonstrated. Preserve the separated crown-and-root anatomy as visible.",
"why":"Direct connected root/crown evidence with basal tillers, allowing crew to learn bunch-forming growth instead of treating any leafy image as a rooted specimen.",
"arrows":[{"label":"Basal shoot and overlapping sheaths","label_x":4,"label_y":17,"target_x":53,"target_y":48},
          {"label":"Hanging true fine roots","label_x":77,"label_y":80,"target_x":52,"target_y":88}]}
]
def get(url):
 with urlopen(Request(url,headers=UA),timeout=50) as h:
  b=h.read(10000001)
 if len(b)>10000000:raise RuntimeError("oversize")
 return b
def main():
 data=json.loads(CARD.read_text())
 if data["scientific_name"]!="Eragrostis hirsuta":raise RuntimeError("Wrong card")
 gallery=data["visual_comparison"]["items"]
 paths={x["image_url"] for x in gallery}
 if all("content/taxa/Poaceae/Eragrostis/eragrostis-hirsuta/images/"+x["file"] in paths for x in PHOTOS):
  print("ALREADY_INSTALLED");return
 obs=json.loads(get(f"https://api.inaturalist.org/v1/observations/{OBS}"))["results"][0]
 if obs["taxon"]["name"]!="Eragrostis hirsuta" or obs["quality_grade"]!="research":
  raise RuntimeError("Exact source research-grade identity missing")
 panels=[];imgs=[];report=[]
 for a in PHOTOS:
  src=next((p for p in obs["photos"] if p["id"]==a["id"]),None)
  if src is None or src.get("license_code")!="cc-by-nc" or "TgarrisonPlateau" not in src.get("attribution",""):
   raise RuntimeError(f"Photo rights or attribution changed {a['id']}")
  source_url=src["url"].replace("/square.","/original.").replace("/medium.","/original.").replace("/thumb.","/original.").replace("/large.","/original.")
  raw=get(source_url)
  with Image.open(io.BytesIO(raw)) as x:
   if x.format not in ("JPEG","PNG"): raise RuntimeError("Not an original JPEG/PNG")
   im=ImageOps.exif_transpose(x).convert("RGB")
   dims=list(im.size)
   if min(dims)<1000:raise RuntimeError("Insufficient full-resolution pixels")
   out=io.BytesIO();im.save(out,format="JPEG",quality=90,optimize=True)
  jpeg=out.getvalue()
  if not (jpeg.startswith(b"\xff\xd8") and jpeg.endswith(b"\xff\xd9")):raise RuntimeError("JPEG structure invalid")
  dest=BASE/"images"/a["file"]
  if dest.exists():raise RuntimeError("unexpected already existing image")
  dest.write_bytes(jpeg)
  rel="content/taxa/Poaceae/Eragrostis/eragrostis-hirsuta/images/"+a["file"]
  source="https://www.inaturalist.org/photos/"+str(a["id"])
  meta={"creator":"TgarrisonPlateau","license":"CC BY-NC 4.0",
    "license_url":"https://creativecommons.org/licenses/by-nc/4.0/",
    "source_page":source,"source_observation_id":OBS,"public_reuse":"yes — only genuinely noncommercial learner with CC BY-NC credit",
    "modifications":"EXIF/GPS metadata stripped via clean RGB JPEG re-encode; SVG/browser overlay arrows not burned in",
    "source_photo_taxon":"Eragrostis hirsuta, source Research Grade observation",
    "sha256":hashlib.sha256(jpeg).hexdigest(),"dimensions_px":dims}
  imgs.append({"file":"images/"+a["file"],"role":a["role"],**meta})
  panels.append({"label":a["label"],"scientific_name":"Eragrostis hirsuta","image_url":rel,"image_fit":"contain",
    "image_role":a["role"],"caption":a["caption"],"why_it_matters":a["why"],
    "markers":a["arrows"],"photo_status":"Original-source pixels inspected Oct 27 2026; endpoints only on observed branching heads, basal shoots, crown or roots; no inner ligule, creeping rhizome or measured floret claimed.",**meta})
  report.append({"photo":a["id"],"source":source,"image":rel,"license":meta["license"],"creator":meta["creator"],
   "bytes":len(jpeg),"dimensions_px":dims,"sha256":meta["sha256"],"arrows":len(a["arrows"])})
 ix=next((i for i,x in enumerate(gallery) if x.get("scientific_name")!="Eragrostis hirsuta"),len(gallery))
 gallery[ix:ix]=panels;data["images"]+=imgs
 data["visual_comparison"]["subtitle"]="Nine archived source-labeled bigtop lovegrass photos: direct original Anderson County flowering clump and clearly attached fibrous root crown, hair-bearing sheath mouth, branching beard and actual spikelets. INNER ligule still requires an opened, mm-calibrated photo.";
 data["curation_status"]["lane2_hirsuta_real_connected_root_growth_20261027"]={"stage":"FIELD_READY_PHOTO_GAPS","new_photos":2,"new_arrows":5,"same_species_archived_total":len(data["images"]),"whole_plant_habit":"PRESENT photographed on one flowering crown","true_connected_rooted_base":"PRESENT real fibrous roots under attached culms","true_ligule":"MISSING innermost ciliate junction not opened and measured","public_website":"pending controlled Pages validation"}
 data["photo_note"]+="\n2026-10-27 Lane2: two original full-resolution CC BY-NC TgarrisonPlateau Anderson County photos depict one rooted flowering bigtop lovegrass tuft with hanging true fibrous roots, 5 gross arrows, physically archived; no true ligule claim."
 REPORT.write_text(json.dumps({"date":"2026-10-27","species":"Eragrostis hirsuta","observation":OBS,"locality":"Anderson County, Texas","exact_photos":report,"new_jpegs":2,"new_arrows":5,"rights":"CC BY-NC; noncommercial educational site only","photo_roles_filled":["whole true field flowering habit","actual connected rooted base"],"still_missing":["true inner ligule and hair fringe at mm scale"],"stage":"FIELD_READY_PHOTO_GAPS","website_deployment":"unverified"},indent=2)+"\n")
 CARD.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n")
 print("ARCHIVED",json.dumps(report))
if __name__=="__main__":main()
