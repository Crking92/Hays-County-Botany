#!/usr/bin/env python3
"""Install 2 exact Zizaniopsis photos, one crown, one attached panicle branch. Never
teach unshown rhizomes, inner ligule or floral sex. Original source pixels reviewed.
"""
import json,io,hashlib
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"content/taxa/Poaceae/Zizaniopsis/zizaniopsis-miliacea"
CARD=BASE/"species.json"
REPORT=ROOT/"reports/lane2-zizaniopsis-anahuac-crown-dallas-spikelets-20261027.json"
UA={"User-Agent":"HaysBotanyVisualLearner/1.0 photo source/individual rights verifier"}
P=[
 {"id":717390360,"obs":391509059,"by":"Alexander Coco",
 "file":"alexander-coco-anahuac-attached-basal-crown-717390360.jpg",
 "label":"ANAHUAC TEXAS · collected plant's genuine joined basal shoots and old sheaths",
 "role":"Real source-species clustered green culms, old tan sheaths, dense brown crown and fibrous rootlike material. Underground connecting rhizome NOT visible.",
 "caption":"Alexander Coco photographed Zizaniopsis miliacea from the East Bay Bayou Tract at Anahuac. Broad green blades and old tan sheath bases meet at one dark basal crown, with attached fibrous material. This is actual partial basal growth evidence, but does NOT show a proven long horizontal rhizome, clear root node, or opened true ligule.",
 "why":"Authentic lower shoot/crown connections rather than inferring a growth mechanism from a wetland stand.",
 "markers":[{"label":"Joined living culm bases and old sheaths","label_x":82,"label_y":20,"target_x":52,"target_y":61},
            {"label":"Actual basal crown (rhizome unseen)","label_x":7,"label_y":83,"target_x":36,"target_y":69}]},
 {"id":691196512,"obs":377953271,"by":"Beth",
 "file":"beth-dallas-attached-cutgrass-flowering-branchlets-691196512.jpg",
 "label":"DALLAS TEXAS · actual attached small spikelets on spreading panicle branch",
 "role":"Actual narrow connected green flowering branchlets with visible small spikelet units and some bent branch angles; sex of spikelets NOT resolvable.",
 "caption":"Beth's Dallas source photo displays real narrow branched giant-cutgrass panicle stems and small attached spikelets against a hand for visual scale. It does not show confidently identified separate staminate/anther-bearing versus pistillate/fruiting spikelets, nor a measurable lemma/glume dissection.",
 "why":"A photographed bridge from the complete branching head to attached small reproductive units, without inventing male/female organ arrows.",
 "markers":[{"label":"Small attached reproductive units","label_x":83,"label_y":13,"target_x":66,"target_y":35}]}
]
def get(u):
 with urlopen(Request(u,headers=UA),timeout=50) as h:b=h.read(10000001)
 if len(b)>10000000:raise ValueError("oversized file")
 return b
def main():
 c=json.loads(CARD.read_text())
 assert c["scientific_name"]=="Zizaniopsis miliacea"
 if any(p["file"] in str(c["visual_comparison"]["items"]) for p in P):print("ALREADY_INSTALLED");return
 rows=[];newpan=[];newimages=[]
 for a in P:
  o=json.loads(get(f'https://api.inaturalist.org/v1/observations/{a["obs"]}'))["results"][0]
  assert o.get("quality_grade")=="research" and o["taxon"]["name"]=="Zizaniopsis miliacea"
  p=next(x for x in o["photos"] if x["id"]==a["id"])
  assert p.get("license_code")=="cc-by-nc" and a["by"].lower() in p.get("attribution","").lower()
  src=p["url"].replace("/square.","/original.").replace("/medium.","/original.").replace("/large.","/original.")
  with Image.open(io.BytesIO(get(src))) as im:
   assert im.format in ("JPEG","PNG")
   image=ImageOps.exif_transpose(im).convert("RGB");dims=list(image.size)
   assert min(dims)>=1000
   buf=io.BytesIO();image.save(buf,"JPEG",quality=90,optimize=True)
  data=buf.getvalue();dest=BASE/"images"/a["file"]
  if dest.exists():raise RuntimeError("refuse overwrite")
  dest.write_bytes(data)
  source="https://www.inaturalist.org/photos/"+str(a["id"])
  rel="content/taxa/Poaceae/Zizaniopsis/zizaniopsis-miliacea/images/"+a["file"]
  props={"creator":a["by"],"license":"CC BY-NC 4.0","license_url":"https://creativecommons.org/licenses/by-nc/4.0/",
   "source_page":source,"source_observation":a["obs"],"source_locality":o.get("place_guess"),
   "public_reuse":"Conditional: this noncommercial educational website only, preserve creator license and source",
   "modifications":"JPEG re-encoded RGB with EXIF/GPS stripped, overlay arrows separate",
   "original_dimensions":dims,"sha256":hashlib.sha256(data).hexdigest()}
  newimages.append({"file":"images/"+a["file"],"role":a["role"],**props})
  newpan.append({"scientific_name":"Zizaniopsis miliacea","label":a["label"],"image_url":rel,"image_fit":"contain",
    "image_role":a["role"],"caption":a["caption"],"why_it_matters":a["why"],"markers":a["markers"],
    "photo_status":"Source original independently inspected; only visible crown and spikelet units identified; sex, ligule, underground rhizome unproven.",**props})
  rows.append({"photo":a["id"],"obs":a["obs"],"source":source,"image":rel,"license":"CC BY-NC 4.0",
    "creator":a["by"],"size":len(data),"sha256":props["sha256"],"original_dimensions":dims,"arrows":len(a["markers"])})
 gallery=c["visual_comparison"]["items"]
 idx=next((i for i,x in enumerate(gallery) if x.get("scientific_name")!="Zizaniopsis miliacea"),len(gallery))
 gallery[idx:idx]=newpan;c["images"]+=newimages
 c["curation_status"]["lane2_zizaniopsis_connected_crown_20261027"]={"stage":"FIELD_READY_PHOTO_GAPS",
   "new_source_JPEGs":2,"new_overlay_arrows":3,"true_growth_role":"PARTIAL: real basal crown/sheaths and fibrous material, but rhizome still hidden",
   "reproductive_role":"PARTIAL: branches with attached spikelets but sex unproven","inner_ligule":"MISSING","public_site":"pending rights-filtered Pages QA"}
 c["photo_note"]+="\n2026-10-27 Lane2: added two true source-verified TX Zizaniopsis photo bytes, Anahuac connected collected crown and Dallas attached branching spikelets. 3 gross-only arrows, no false ligule/sex/rhizome claim."
 REPORT.write_text(json.dumps({"date":"2026-10-27","photos":rows,"new_JPEGs":2,"new_arrows":3,
  "six_role_update":"actual basal growth 0 to partial 0.5 only","still_missing":["true inner ligule","exposed spreading rhizome","independently sexed male/female spikelets"],"publication":"pending"},indent=2)+"\n")
 CARD.write_text(json.dumps(c,ensure_ascii=False,indent=2)+"\n")
 print("ARCHIVED",json.dumps(rows))
if __name__=="__main__":main()
