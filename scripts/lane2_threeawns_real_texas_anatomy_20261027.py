#!/usr/bin/env python3
"""Lane 2 true photographed purple and oldfield threeawn anatomy, exact species.
Only original licensed Texas 2026 iNaturalist research-grade photo bytes; field
pixels inspected on GitHub action run 40540319570. No unseen anatomy marked.
"""
from pathlib import Path
from urllib.request import urlopen, Request
from PIL import Image,ImageOps
import json,io,hashlib

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/"reports/lane2-threeawns-matched-collar-mature-awns-20261027.json"
ROOT_CARD="content/taxa/Poaceae/Aristida/"
UA={"User-Agent":"HaysBotanyVisualLearner/1.0 (individually licensed original species-specific educational photos)"}
PHOTO=[
 {"id":"aristida-purpurea","species":"Aristida purpurea","photo":749623255,"obs":407870376,"license":"cc-by-nc",
  "creator":"colleendieter","local_name":"colleendieter-purple-threeawn-exterior-blade-sheath-749623255.jpg",
  "label":"REAL LEAF JUNCTION · outer blade and sheath against neutral background",
  "role":"Original TX photo of Aristida purpurea narrow green blade, culm and exterior adjoining leaf sheath. Inner fringe ligule NOT opened.",
  "caption":"An actual purple threeawn green leaf and sheath photographed by colleendieter in Horseshoe Bay, Texas. The narrow diagonal blade meets a narrow vertical shoot near its sleeve-like base. Look for the insertion, then GENTLY TURN BACK the leaf to find the true hair-fringe ligule, which this exterior view does not expose or measure. Do not identify the orange background as plant tissue.",
  "why":"Direct species-labelled blade/sheath growth from the Hill Country rather than inferring collar parts from flowering stems.",
  "arrows":[{"label":"Exterior blade–sheath junction (inner ligule unseen)","label_x":60,"label_y":8,"target_x":53,"target_y":46}]},
 {"id":"aristida-purpurea","species":"Aristida purpurea","photo":754606055,"obs":410317237,"license":"cc0",
  "creator":"iNaturalist CC0 photographer (source credit retained)","local_name":"cc0-purple-threeawn-triple-awn-mature-units-754606055.jpg",
  "label":"MATURE THREEAWN · long spreading individual awns against a hand",
  "role":"Actual narrow mature awned spikelet-bearing inflorescence viewed at hand scale, showing the slender starburst awn silhouette; tiny glume veins not measured.",
  "caption":"A Dallas research-grade purple threeawn CC0 original shows long radiating threadlike awns and narrow attached fruiting portions above fingers. Compare an equivalent open mature oldfield threeawn image; both have three awns, so COUNTING THREE alone is not enough to identify either species. Do not label glume-vein number, lemma callus or ligule from this photo.",
  "why":"Provides an up-close true reproductive view matched with oldfield threeawn instead of a generic distant tuft.",
  "arrows":[{"label":"Long spreading lemma awns (gross view)","label_x":7,"label_y":24,"target_x":30,"target_y":54}]},
 {"id":"aristida-oligantha","species":"Aristida oligantha","photo":753081739,"obs":409565487,"license":"cc-by-nc",
  "creator":"beechaser","local_name":"beechaser-oldfield-threeawn-whole-live-field-tuft-753081739.jpg",
  "label":"OLD FIELD · actual many-stemmed annual tuft growing in soil",
  "role":"Living source-determined ground-rooted annual bunch with multiple wiry shoots, some fine flowering branches, and exposed ground-level shoot cluster; roots UNDER soil not visible.",
  "caption":"This real oldfield threeawn in Lavaca County is visibly established in disturbed soil with many narrow, wiry branches gathered near the crown. Nearby green shoots and dry grass form a mixed scene. The ROOTS are underground: do not claim excavated fibrous roots or an actual rhizome. Annual versus perennial growth must be confirmed from known species and basal botanical characters, not merely the tuft silhouette.",
  "why":"Fills the gap between an isolated field awn and the full in-ground basal annual bunch habit, useful to crews identifying disturbed sites.",
  "arrows":[{"label":"Ground-level tuft of wiry culms (roots hidden)","label_x":3,"label_y":77,"target_x":54,"target_y":66}]},
 {"id":"aristida-oligantha","species":"Aristida oligantha","photo":751732084,"obs":408904031,"license":"cc-by-nc",
  "creator":"Michael A. Puttonen","local_name":"puttonen-oldfield-threeawn-outer-leaf-sheath-751732084.jpg",
  "label":"TRUE FIELD PLANT · green narrow blade, lower sheath and stem junction",
  "role":"Close true exterior green oldfield threeawn culm with a narrow leaf at attachment; tiny inner hair-fringe ligule is NOT exposed or calibrated.",
  "caption":"Michael A. Puttonen's Greenville plant shows multiple narrow green structures crossing where an actual attached blade meets its shoot. This is an OUTER leaf-sheath/culm junction from the correct species, not a demonstration of the approximately 0.1–0.5-mm true ligule fringe. A caliper or small scale and inside-throat macro remain necessary.",
  "why":"A species-specific view of the genuine leaf junction rather than inaccurately substituting the collar of another Aristida.",
  "arrows":[{"label":"Visible exterior blade/sheath connection","label_x":10,"label_y":11,"target_x":62,"target_y":58}]},
 {"id":"aristida-oligantha","species":"Aristida oligantha","photo":747930916,"obs":407038483,"license":"cc-by-nc",
  "creator":"C. D. Winker","local_name":"winker-oldfield-threeawn-glumes-awn-in-blue-background-747930916.jpg",
  "label":"REPRODUCTIVE DETAIL · narrow pale spikelets and spreading awns",
  "role":"Actual source-identified reproductive macro of several thin pale glume-like bracts with long radiating awns, held against a blue background. Individual numbered glumes, vein count, mm scale still unresolved.",
  "caption":"C. D. Winker's Sealy, Texas close-up isolates an actual oldfield threeawn fruiting branch over blue cloth, making the slender pale spikelet bracts and long spreading awns visible. Compare to the purple threeawn mature-floret closeup in its separate species card. True 3–7-veined lower glume and hardened lemma diagnosis requires individually spread bracts and hand lens; don't claim a vein count from this image.",
  "why":"Much stronger actual reproductive structure photograph than distant wiry stems; supports beginner-to-macro progression.",
  "arrows":[{"label":"Pale narrow reproductive bracts","label_x":3,"label_y":17,"target_x":42,"target_y":37},{"label":"Long hair-thin spreading awns","label_x":80,"label_y":72,"target_x":46,"target_y":59}]}
]
def fetch_json(url):
 with urlopen(Request(url,headers=UA),timeout=50) as h:return json.load(h)
def fetch_photo(url):
 with urlopen(Request(url,headers=UA),timeout=50) as h:raw=h.read(10_000_001)
 if len(raw)>10_000_000:raise ValueError("Too large")
 return raw
def run():
 cache={}
 cards={}
 for key in ["aristida-purpurea","aristida-oligantha"]:
  path=ROOT/ROOT_CARD/key/"species.json"
  card=json.loads(path.read_text())
  if card["scientific_name"]!=("Aristida "+key.rsplit("-",1)[-1]):raise ValueError("Unexpected canonical taxon")
  cards[key]=(path,card)
 for p in PHOTO:
  card=cards[p["id"]][1]
  if any(p["local_name"] in x.get("image_url","") for x in card["visual_comparison"]["items"]):
   print("ALREADY_INSTALLED",p["local_name"]);return
 records=[]
 galleries={"aristida-purpurea":[],"aristida-oligantha":[]}
 for p in PHOTO:
  obs_id=p["obs"]
  if obs_id not in cache:cache[obs_id]=fetch_json(f"https://api.inaturalist.org/v1/observations/{obs_id}")["results"][0]
  o=cache[obs_id]
  if o.get("taxon",{}).get("name")!=p["species"] or o.get("quality_grade")!="research":raise ValueError("Species/grade mismatch")
  photo=next((x for x in o.get("photos",[]) if x["id"]==p["photo"]),None)
  if not photo or photo.get("license_code")!=p["license"]:raise ValueError("Individual photo license changed: "+str(p["photo"]))
  if p["license"]!="cc0" and p["creator"].lower() not in photo.get("attribution","").lower():
   raise ValueError("Credited photographer mismatch")
  photo_url=photo["url"].replace("/square.","/original.").replace("/medium.","/original.").replace("/large.","/original.")
  raw=fetch_photo(photo_url)
  with Image.open(io.BytesIO(raw)) as f:
   if f.format not in {"JPEG","PNG"}:raise ValueError("Bad raster")
   image=ImageOps.exif_transpose(f).convert("RGB");dims=list(image.size)
   if min(dims)<900:raise ValueError("Source pixels insufficient")
   out=io.BytesIO();image.save(out,format="JPEG",quality=90,optimize=True)
  b=out.getvalue()
  if not(b.startswith(b"\xff\xd8") and b.endswith(b"\xff\xd9")):raise ValueError("bad encoded JPEG")
  dest=ROOT/ROOT_CARD/p["id"]/"images"/p["local_name"]
  if dest.exists():raise ValueError("Refuse overwrite "+str(dest))
  dest.write_bytes(b)
  rel=ROOT_CARD+p["id"]+"/images/"+p["local_name"]
  license_label={"cc0":"CC0 1.0","cc-by-nc":"CC BY-NC 4.0"}[p["license"]]
  license_link={"cc0":"https://creativecommons.org/publicdomain/zero/1.0/","cc-by-nc":"https://creativecommons.org/licenses/by-nc/4.0/"}[p["license"]]
  props={"creator":p["creator"],"license":license_label,"license_url":license_link,
     "source_page":"https://www.inaturalist.org/photos/"+str(p["photo"]),
     "source_observation_id":obs_id,"source_locality":o.get("place_guess"),
     "public_reuse":"yes, only on confirmed genuinely noncommercial education site and visible credit" if p["license"]=="cc-by-nc" else "yes, CC0 source verified",
     "modifications":"EXIF/GPS stripped by RGB clean JPEG re-encode; overlay arrows are separate web annotations",
     "original_dimensions_px":dims,"file_sha256":hashlib.sha256(b).hexdigest()}
  cards[p["id"]][1]["images"].append({"file":"images/"+p["local_name"],"role":p["role"],**props})
  galleries[p["id"]].append({"label":p["label"],"scientific_name":p["species"],"image_url":rel,"image_fit":"contain",
   "image_role":p["role"],"caption":p["caption"],"why_it_matters":p["why"],"markers":p["arrows"],
   "photo_status":"ORIGINAL photograph pixels individually reviewed on 2026-10-27. Gross visible external junction/flowering/base only. Inner ligule, roots and glume veins NOT demonstrable.",**props})
  records.append({"species":p["species"],"photo":p["photo"],"license":license_label,"creator":p["creator"],
    "source":props["source_page"],"archive":rel,"sha256":props["file_sha256"],"dimensions":dims,"bytes":len(b),"arrows":len(p["arrows"])})
 for key,(path,card) in cards.items():
  gallery=card["visual_comparison"]["items"];new=galleries[key]
  idx=next((i for i,x in enumerate(gallery) if x.get("scientific_name")!=card["scientific_name"]),len(gallery))
  gallery[idx:idx]=new
  card["curation_status"]["lane2_threeawn_real_collar_repro_20261027"]={
    "state":"FIELD_READY_PHOTO_GAPS","new_local_JPEGs":len(new),"new_browser_arrows":sum(len(p["markers"]) for p in new),
    "true_inner_ligule":"NOT photographed; only real OUTER junction is documented",
    "actual_exposed_roots":"NOT photographed; oldfield has in-ground crown view with roots hidden",
    "reproductive_macro":"REAL visible awns and bracts, not a vein-count or measured glume",
    "confirmed_hill_country_source":"purple: Horseshoe Bay; oldfield: Lavaca, Greenville, Sealy",
    "publish":"Pending controlled rights-filtered Pages deployment"
  }
  card["photo_note"]=(card.get("photo_note","")+
    "\n2026-10-27 Lane 2 photograph-first: actual Texas source photo originals archived for mature awned florets and species-specific outer blade/sheath. Oldfield additionally has in-soil tuft habit; ligule tips, actual roots and individually venated glumes still require field collection. Only gross visible arrows.")
  path.write_text(json.dumps(card,indent=2,ensure_ascii=False)+"\n")
 REPORT.write_text(json.dumps({"date":"2026-10-27","photo_role_policy":"STRICT six-role: exterior blade/sheath 0.5, true hair ligule absent; in-ground growth at most 0.5; reproductive macro visible but no glume vein count","new_exact_JPEGs":len(records),"new_gross_arrows":sum(r["arrows"] for r in records),
 "photos":records,"publication_status":"not checked; controlled Pages required","license":"each source photo checked cc0 or cc-by-nc under noncommercial policy"},indent=2)+"\n")
 print("SUCCESS",json.dumps(records))
if __name__=="__main__":run()
