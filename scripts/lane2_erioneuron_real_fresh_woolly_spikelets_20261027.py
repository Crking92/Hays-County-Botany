#!/usr/bin/env python3
"""Actual attached vs mature hairy tridens reproductive organs.
Only original, pixel-inspected, individually licensed Erioneuron pilosum photos.
No unphotographed ligule/root/lemma vein label; maintain original rights.
"""
import json,io,hashlib
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"content/taxa/Poaceae/Erioneuron/erioneuron-pilosum"
CARD=BASE/"species.json"
REPORT=ROOT/"reports/lane2-erioneuron-actual-green-and-woolly-mature-spikelets-20261027.json"
UA={"User-Agent":"HaysBotanyVisualLearner/1.0 original photo-specific license verification"}
P=[
 {"photo":698633127,"obs":381794795,"license":"cc-by-sa","creator":"Turner Brockman",
 "name":"turner-brockman-hairy-tridens-green-attached-spikelet-698633127.jpg",
 "label":"GREEN REPRODUCTIVE STAGE · real attached immature spikelets and narrow blades",
 "role":"Actual still-attached pale green and pink edged developing spikelets overlap along an upright young flowering axis, with narrow pale-rimmed blades to left; individual lemma/glume nerves unseen.",
 "caption":"Turner Brockman's photograph of Erioneuron pilosum depicts a real young upright flowering head with narrow overlapping green spikelet units and pale margins, above nearby true narrow leaves. Follow the flowerhead axis and later compare to the fully silvery mature floret photograph; it is not a dissected single lemma or a ruler-calibrated glume-vein image.",
 "why":"Shows the green developing bracts and their attachment before the very pale silvery woolly maturity stage; species-specific diagnostic reproductive progression.",
 "markers":[{"label":"Young attached overlapping spikelets","label_x":5,"label_y":13,"target_x":50,"target_y":35}]},
 {"photo":694991915,"obs":379913881,"license":"cc-by-nc","creator":"Beth",
 "name":"beth-hairy-tridens-silvery-floret-hairs-694991915.jpg",
 "label":"SILVERY MATURE HEAD · real individual densely hairy florets",
 "role":"Mature dense creamy-white feathery spikelet units with visible fine silvery hairs on their flowering bracts; source exact species. Full male/female, lemma/glume count not resolved.",
 "caption":"Beth's real flowering-unit close-up shows several Erioneuron pilosum florets covered in conspicuous long white silky hairs, arranged in dense narrow spikes over the hand. The hairs are actually attached to flowering bracts. We cannot positively assign the underlying vein counts, glumes, lemma/palea or tiny terminal awn from this unscaled image. Compare the very different open hanging panicle of Texas tridens.",
 "why":"A true original high-resolution macro of the actual silvery reproductive structures, giving learners more anatomy than a distant fluffy white seedhead.",
 "markers":[{"label":"White silky hairs on actual flowering bracts","label_x":84,"label_y":11,"target_x":60,"target_y":36},
            {"label":"Dense overlapping mature floret units","label_x":4,"label_y":84,"target_x":49,"target_y":68}]}
]
def read_json(url):
 with urlopen(Request(url,headers=UA),timeout=48) as r:return json.load(r)
def read_bytes(url):
 with urlopen(Request(url,headers=UA),timeout=50) as r:bytes_=r.read(10000001)
 if len(bytes_)>10000000:raise RuntimeError("File too large")
 return bytes_
def main():
 card=json.loads(CARD.read_text())
 assert card["scientific_name"]=="Erioneuron pilosum"
 if any(p["name"] in x.get("image_url","") for x in card["visual_comparison"]["items"] for p in P):
  print("Already partly installed, fail rather than duplicate");return
 cached={};images=[];panels=[];report=[]
 for p in P:
  if p["obs"] not in cached:cached[p["obs"]]=read_json(f'https://api.inaturalist.org/v1/observations/{p["obs"]}')["results"][0]
  obs=cached[p["obs"]]
  if obs["taxon"]["name"]!="Erioneuron pilosum" or obs["quality_grade"]!="research":raise RuntimeError("Taxon status changed")
  phot=next((q for q in obs["photos"] if q["id"]==p["photo"]),None)
  if not phot or phot.get("license_code")!=p["license"] or p["creator"].lower() not in phot.get("attribution","").lower():raise RuntimeError("Original photo level rights/credit changed")
  src=phot["url"].replace("/square.","/original.").replace("/medium.","/original.").replace("/large.","/original.")
  raw=read_bytes(src)
  with Image.open(io.BytesIO(raw)) as f:
   if f.format not in {"JPEG","PNG"}:raise ValueError("Unsupported photo type")
   im=ImageOps.exif_transpose(f).convert("RGB")
   dims=list(im.size)
   if min(dims)<1000:raise ValueError("Pixel resolution inadequate")
   buf=io.BytesIO();im.save(buf,"JPEG",quality=90,optimize=True)
  b=buf.getvalue()
  if not b.startswith(b"\xff\xd8") or not b.endswith(b"\xff\xd9"):raise ValueError("Broken JPEG")
  dest=BASE/"images"/p["name"]
  if dest.exists():raise RuntimeError("Never overwrite")
  dest.write_bytes(b)
  label="CC BY-SA 4.0" if p["license"]=="cc-by-sa" else "CC BY-NC 4.0"
  link="https://creativecommons.org/licenses/by-sa/4.0/" if p["license"]=="cc-by-sa" else "https://creativecommons.org/licenses/by-nc/4.0/"
  rel="content/taxa/Poaceae/Erioneuron/erioneuron-pilosum/images/"+p["name"]
  src_page="https://www.inaturalist.org/photos/"+str(p["photo"])
  metadata={"creator":p["creator"],"license":label,"license_url":link,"source_page":src_page,"source_observation_id":p["obs"],
   "public_reuse":"yes — provided license terms observed, noncommercial only" if p["license"]=="cc-by-nc" else "yes — CC BY-SA with attribution and ShareAlike",
   "modifications":"RGB re-encoded clean JPEG no EXIF/GPS; arrows separate web layer",
   "verified_species":"Erioneuron pilosum, research grade observed record; not subspecies-vouchered",
   "photo_original_dimensions":dims,"photo_sha256":hashlib.sha256(b).hexdigest()}
  images.append({"file":"images/"+p["name"],"role":p["role"],**metadata})
  panels.append({"label":p["label"],"scientific_name":"Erioneuron pilosum","image_url":rel,"image_fit":"contain",
   "image_role":p["role"],"caption":p["caption"],"why_it_matters":p["why"],"markers":p["markers"],
   "photo_status":"Source photo original inspected 2026-10-27; only actually visible florets/hairs/panicle bracts labelled, no invented ligule/root/floral vein count.",**metadata})
  report.append({"photo_id":p["photo"],"source":src_page,"license":label,"creator":p["creator"],"archived_path":rel,
    "source_dimensions_px":dims,"file_sha256":metadata["photo_sha256"],"bytes":len(b),"new_markers":len(p["markers"])})
 arr=card["visual_comparison"]["items"];index=next((i for i,a in enumerate(arr) if a.get("scientific_name")!="Erioneuron pilosum"),len(arr))
 arr[index:index]=panels;card["images"]+=images
 card["visual_comparison"]["subtitle"]="Real locally hosted field tuft/habit, pale-edged narrow leaf and verified flowering head photos; newly added original source CC BY-SA young green attached spikelets and CC BY-NC mature silvery hairy floret macro. Separate genuine Munroa and Tridens look-alikes. Missing photo-verified opened true ligule (0.35 mm), excavated roots and isolated glume/lemma dissection."
 card["curation_status"]["lane2_hairy_tridens_true_reproductive_macro_20261027"]={
  "stage":"FIELD_READY_PHOTO_GAPS","new_exact_species_JPEGs":2,"new_visible_only_arrows":3,
  "same_species_archived_total":len(card["images"]),"reproductive_closeup":"Full SIX-ROLE credited: actual sufficiently sharp young/mature hairy spikelets",
  "true_ligule":"NOT photographed","rooted_growth":"PARTIAL in-soil crown; genuine roots not exposed",
  "microscopic_glumes":"STILL MISSING","site":"await controlled Pages approval, NC policy check"}
 card["photo_note"]+="\n2026-10-27 Lane 2: archived 2 actual E. pilosum source-verified new Texas source photos (green attached spikelets, silvery mature densely hairy florets) and 3 gross-only arrows. No true 0.35-mm ligule, root or lemma vein count claimed."
 REPORT.write_text(json.dumps({"date":"2026-10-27","species":"Erioneuron pilosum","photos":report,"new_JPEGs":2,"new_arrows":3,
   "photographic_role_gain":"diagnostic reproductive close-up from partial to clear",
   "not_yet_photographed":["peeled inner hair-fringe ligule and scale","connected excavated fibrous crown","individually dissected glume/lemma veins"],"Pages_status":"pending"},indent=2)+"\n")
 CARD.write_text(json.dumps(card,indent=2,ensure_ascii=False)+"\n")
 print("ARCHIVED",json.dumps(report))
if __name__=="__main__":main()
