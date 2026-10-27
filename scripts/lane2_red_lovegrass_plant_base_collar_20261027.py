#!/usr/bin/env python3
"""Photo-only Lane 2 field anatomy progress; exact Eragrostis secundiflora.
Three verified Texas photos, original CC BY or individually CC BY-NC, same-species,
no subspecies reinterpretation, visible-only arrows and clean EXIF-free archives.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageOps
import json,hashlib,io
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"content/taxa/Poaceae/Eragrostis/eragrostis-secundiflora"
CARD=BASE/"species.json"
REPORT=ROOT/"reports/lane2-red-lovegrass-real-whole-collar-20261027.json"
UA={"User-Agent":"HaysBotanyVisualLearner/1.0 individually cleared field ID photo archive"}
PHOTOS=[
{"photo":752261900,"obs":408961511,"name":"txgulfcoast-red-lovegrass-pink-flowering-tuft-752261900.jpg","creator":"txgulfcoast","rights":"cc-by-nc",
 "label":"SEADRIFT, TX · real living pink-flowering red lovegrass clump",
 "role":"Full in situ rooted-in-soil perennial tuft with visible long lower blades and several attached pink/red mature flowering panicles; underground roots not exposed",
 "caption":"Texas coastal source-labelled red lovegrass growing in place near Seadrift: several narrow-leaved shoots emerge near the soil surface and carry many branched pink/reddish heads. The flowering units remain attached to the culms, making this a true practical whole-plant example. Soil and adjacent herbs overlap the basal shoots; exact rooting connections and underground structures are not exposed.",
 "why":"First strong whole growing plant connecting lower leafy habit and attached recognizable reddish spikelets, unlike the earlier mostly detached hand-scale flowering shots.",
 "arrows":[{"label":"Pink flowering branchlets attached to culms","label_x":4,"label_y":18,"target_x":52,"target_y":39},
           {"label":"Living tuft blades above soil (roots hidden)","label_x":4,"label_y":86,"target_x":68,"target_y":81}]},
{"photo":752434624,"obs":409250703,"name":"sam-kieschnick-red-lovegrass-ground-growing-bunch-752434624.jpg","creator":"Sam Kieschnick","rights":"cc-by",
 "label":"WILLOW PARK, TX · lower growing bunch with attached seed-bearing shoots",
 "role":"Authentic in-ground lower bunch and erect leafy flowering shoots in sandy/disturbed site; partially visible basal growth but no actual roots",
 "caption":"Sam Kieschnick's Willow Park source photo shows several narrow, source-identified E. secundiflora flowering culms and basal leaves clustered where they emerge from exposed soil. The lower growing tuft is directly visible and supports a FIELD base-habit view, but true fibrous roots/rhizomes and an interior ligule membrane are not visible.",
 "why":"Documents real lower shoot connection to a field-growing bunch, partial root-crown context without claiming excavated roots.",
 "arrows":[{"label":"Grouped basal shoots near soil surface","label_x":7,"label_y":86,"target_x":45,"target_y":78}]},
{"photo":753369298,"obs":409704780,"name":"nativenomadics-red-lovegrass-blade-exterior-sheath-753369298.jpg","creator":"nativenomadics","rights":"cc-by-nc",
 "label":"LEAF BASE · real external V-shaped blade–sheath mouth, not true inner ligule",
 "role":"Actual source-verified green-red lovegrass blade, outer sheath insertion and longitudinal striation; ligule not turned outward",
 "caption":"Source-labelled E. secundiflora original leaf photo. The pale longitudinally striped narrow blade is visible joining its sheath close to the photographer's fingers. It shows the OUTSIDE blade–sheath V, not an unfolded ciliate true ligule or calibrated inner 0.5-mm fringe. Do not label the exposed pale sheath corner as definitive ligule anatomy.",
 "why":"First broad species-labelled above-ground collar photo beyond the oxylepis-subspecies-only detail views, without pretending a true inner ligule is resolved.",
 "arrows":[{"label":"Outer blade-to-sheath junction (inner ligule hidden)","label_x":7,"label_y":86,"target_x":40,"target_y":75}]}
]
def fetch(url):
 with urlopen(Request(url,headers=UA),timeout=55) as h:b=h.read(10_000_001)
 if len(b)>10_000_000:raise RuntimeError("oversize")
 return b
def main():
 j=json.loads(CARD.read_text())
 if j["scientific_name"]!="Eragrostis secundiflora":raise RuntimeError("Wrong species")
 panels=j["visual_comparison"]["items"]
 if any(p.get("image_url","").endswith("red-lovegrass-pink-flowering-tuft-752261900.jpg") for p in panels):
  print("ALREADY_INSTALLED");return
 new=[];imgs=[];report=[]
 for s in PHOTOS:
  o=json.loads(fetch(f"https://api.inaturalist.org/v1/observations/{s['obs']}"))["results"][0]
  if o["taxon"]["name"]!="Eragrostis secundiflora" or o["quality_grade"]!="research":raise RuntimeError("Taxon/grade changed")
  p=next((x for x in o["photos"] if x["id"]==s["photo"]),None)
  if not p or p.get("license_code")!=s["rights"] or s["creator"].lower() not in p.get("attribution","").lower():raise RuntimeError("individual source rights changed")
  url=p["url"].replace("/square.","/original.").replace("/medium.","/original.").replace("/large.","/original.")
  raw=fetch(url)
  with Image.open(io.BytesIO(raw)) as f:
   if f.format not in {"JPEG","PNG"}:raise RuntimeError("bad photo format")
   image=ImageOps.exif_transpose(f).convert("RGB");dims=list(image.size)
   if min(dims)<900:raise RuntimeError("insufficient source pixel evidence")
   buf=io.BytesIO();image.save(buf,"JPEG",quality=90,optimize=True)
  b=buf.getvalue()
  if not b.startswith(b"\xff\xd8") or not b.endswith(b"\xff\xd9"):raise RuntimeError("Invalid JPEG")
  path=BASE/"images"/s["name"]
  if path.exists():raise RuntimeError("Existing path - no unintended overwrite")
  path.write_bytes(b)
  role=s["role"]
  lic="CC BY-NC 4.0" if s["rights"]=="cc-by-nc" else "CC BY 4.0"
  props={"creator":s["creator"],"license":lic,
    "license_url":"https://creativecommons.org/licenses/by-nc/4.0/" if s["rights"]=="cc-by-nc" else "https://creativecommons.org/licenses/by/4.0/",
    "source_page":"https://www.inaturalist.org/photos/"+str(s["photo"]),
    "source_observation_id":s["obs"],"source_region":o.get("place_guess"),
    "public_reuse":"exact individual license — noncommercial educational site with credit only" if s["rights"]=="cc-by-nc" else "yes CC BY credited",
    "modifications":"Original color image re-encoded JPEG without EXIF/GPS; overlay arrows separate",
    "photo_sha256":hashlib.sha256(b).hexdigest(),"original_dimensions_px":dims}
  imgs.append({"file":"images/"+s["name"],"role":role,**props})
  rel="content/taxa/Poaceae/Eragrostis/eragrostis-secundiflora/images/"+s["name"]
  new.append({"label":s["label"],"scientific_name":"Eragrostis secundiflora","image_url":rel,"image_fit":"contain",
    "image_role":role,"caption":s["caption"],"why_it_matters":s["why"],"markers":s["arrows"],
    "photo_status":"Original full source pixels verified in GitHub photo-review run 40537152114; real shoot growth, outside collar or flowering, NO true inner ligule/root claim.",**props})
  report.append({"photo":s["photo"],"creator":s["creator"],"license":lic,"source":props["source_page"],
    "archive":rel,"sha256":props["photo_sha256"],"dimensions":dims,"bytes":len(b),"new_arrows":len(s["arrows"])})
 ix=next((i for i,p in enumerate(panels) if p.get("scientific_name")!="Eragrostis secundiflora"),len(panels))
 panels[ix:ix]=new;j["images"]+=imgs
 j["visual_comparison"]["subtitle"]="Nine actual same-species photo panels including newly archived Texas flowering whole tuft, in-ground basal growth and actual outer blade/sheath collar; existing oxylepis separately labelled as subspecies. True unfolded species-level ligule hair fringe and exposed fibrous roots remain missing."
 j["curation_status"]["lane2_red_lovegrass_real_field_20261027"]={"stage":"FIELD_READY_PHOTO_GAPS","new_source_verified_archived_jpegs":3,"new_visible_only_arrows":4,"same_species_gallery_panels":len([x for x in panels if x.get("scientific_name")==j["scientific_name"]]),"whole_plant_habit":"CLEAR attached flowering field plant","rooted_growth":"PARTIAL in-ground basal clump, roots unseen","collar":"ONLY external species-level collar, not interior ligule","photo_policy":"individual licenses checked, EXIF stripped, all photos physically in repository","pages":"Not verified until separate publishing run"}
 j["photo_note"]+="\n2026-10-27 Lane 2 photo-first: 3 exact source-licensed Texas E. secundiflora JPEGs show complete in-ground flowering tuft, partial basal growth and true exterior blade/sheath V, plus 4 visible-only arrows. NO role credit for exposed root or actual inner ligule. Oxylepis reproductive/collar photos remain separate subtype labelled."
 REPORT.write_text(json.dumps({"species":"Eragrostis secundiflora","status":"FIELD_READY_PHOTO_GAPS","photos":report,
 "new_archived_exact_species_jpegs":3,"new_arrows":4,"actual_photo_roles":["whole flowering tuft","in-ground base partial","outer sheath-blade junction partial"],"not_fixed":["unfolded inner true ligule with ruler","genuine lifted fibrous crown"],"site":"await controlled rights filtered Pages publication"},indent=2)+"\n")
 CARD.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n")
 print("SUCCESSFUL_3_ACTUAL_PHOTO_ARCHIVE",json.dumps(report))
if __name__=="__main__":main()
