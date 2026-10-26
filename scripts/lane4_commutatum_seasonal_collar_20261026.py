#!/usr/bin/env python3
"""Source-fingerprinted photo additions for Dichanthelium commutatum, NOT false roots.

Two original botanical photographs were independently viewed on Commons
2026-10-26. Preserve existing canonical records and noncommercial CC BY-NC
look-alikes; both new photos can be shown on a public learner with their
individual CC BY or CC BY-SA original source terms and creator credit.
"""
import hashlib,io,json,pathlib,time,urllib.request
from PIL import Image,ImageOps

root=pathlib.Path("content/taxa/Poaceae/Dichanthelium/dichanthelium-commutatum")
path=root/"species.json"
j=json.loads(path.read_text(encoding="utf-8"))
assert j["id"]=="dichanthelium-commutatum"
assert j["field_id_finish_pass"]["stage"]=="FIELD_READY_PHOTO_GAPS"

rows=[
{
 "id":"363938848",
 "stem":"Dichanthelium_commutatum_363938848.jpg",
 "hashpath":"e/e9",
 "sha1":"5493c85954bd77ec0779dac4840cf885110fd680",
 "expected":(1536,2048),
 "preview":(960,1280),
 "author":"Alex Abair",
 "license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/",
 "page":"https://commons.wikimedia.org/wiki/File:Dichanthelium_commutatum_363938848.jpg",
 "source_photo":"https://www.inaturalist.org/photos/363938848",
 "filename":"commons-abair-363938848-clasping-sheath.jpg",
 "role":"Close side view of intact leaf blade joining the purplish green sheath at culm; sparse outward hairs along margin and visible collar location. Tiny true INNER ligule is NOT measurable or separately exposed.",
 "label":"TRUE LEAF BASE — clasping blade and purple sheath mouth",
 "caption":"Alex Abair's photo shows a green blade emerging to the right from the purplish stem sheath, with the blade base curving round the culm and wispy hairs near the junction. The real sheath continues down the culm to a dark swollen-looking node lower in the photograph. The interior ligule edge is NOT exposed or scaled, so do not mistake the sheath overlap for a measured 0.5-mm ligule.",
 "why":"Crew can distinguish a real blade–sheath insertion from a stem node or an outer sheath edge and recognize the clasping base. Follow with a freely opened inner collar for ligule type/length.",
 "markers":[
   {"label":"Blade base wraps to stem","label_x":76,"label_y":10,"target_x":52,"target_y":11},
   {"label":"Purplish outer leaf sheath","label_x":7,"label_y":44,"target_x":48,"target_y":47},
   {"label":"Culm node below collar","label_x":72,"label_y":83,"target_x":49,"target_y":74}
 ]
},
{
 "id":"14607522899",
 "stem":"Dichanthelium_commutatum_%2814607522899%29.jpg",
 "hashpath":"5/54",
 "sha1":"f0cac709e3163fced153030b8be3ff2514d929ca",
 "expected":(4912,3264),
 "preview":(1280,851),
 "author":"rockerBOO",
 "license":"CC BY-SA 2.0","license_url":"https://creativecommons.org/licenses/by-sa/2.0/",
 "page":"https://commons.wikimedia.org/wiki/File:Dichanthelium_commutatum_(14607522899).jpg",
 "source_photo":"https://www.flickr.com/photos/rockerboo/14607522899",
 "filename":"commons-rockerboo-14607522899-leafy-branches.jpg",
 "role":"True species-labelled sprawling green late-season leafy shoots with small leaf fascicles at stem branching points, flowering stage/season cannot be established from photo alone; NO actual connected roots.",
 "label":"FIELD LESSON — leafy branching shoots and tight leaf clusters",
 "caption":"This older rockerBOO species-labelled photograph shows narrow green blades on low branching culms and conspicuous groups of short leaves at shoot junctions amid woodland debris. Such leafy clustering illustrates the branch/fascicle shape crew may encounter outside an obvious spring panicle. The photograph does not prove an excavated rooted crown, exact seasonal phenology, inner ligule or measured spikelets.",
 "why":"A useful second growth-phase lesson when a grass no longer presents a textbook open flowering head. Source identity is photo-labelled; confirm actual species with basal leaf bases and mature spikelets.",
 "markers":[
    {"label":"Tight leafy branch cluster","label_x":70,"label_y":7,"target_x":53,"target_y":30},
    {"label":"Branching slender culm","label_x":7,"label_y":77,"target_x":31,"target_y":59}
 ]
}
]
report={"species":"Dichanthelium commutatum","date":"2026-10-26","local_originals_added":[],"held":[],"root_coverage":"NOT RESOLVED, no exposed roots on either picture","true_ligule":"NOT RESOLVED, thin membrane not independently exposed","change_log":"One-species add-only upgrades; existing 8 photos, comparisons and NC credits preserved."}
headers={"User-Agent":"Mozilla/5.0 (compatible; HaysCountyBotanyEducationalPhoto/1.0)","Accept":"image/jpeg,image/*;q=0.8"}
for x in rows:
  relative="images/"+x["filename"]
  target=root/relative
  if any(im.get("file")==relative for im in j["images"]):
      report["held"].append({"id":x["id"],"reason":"Photo metadata already canonical, no duplicate"})
      continue
  prefix=f"https://upload.wikimedia.org/wikipedia/commons/{x['hashpath']}/"
  original=prefix+x["stem"]
  basename=x["stem"].replace("%28","(").replace("%29",")")
  thumb=f"https://thumb.wikimedia.org/wikipedia/commons/thumb/{x['hashpath']}/{x['stem']}/{x['preview'][0]}px-{x['stem']}"
  modes=[(original,x["expected"],"Commons original SHA1-verified"),(thumb,x["preview"],"Same-file Commons thumbnail derivative, source hash separately audited")]
  try:
      downloaded=None;fail=[]
      for url,expected,variant in modes:
          for attempt in range(2):
              try:
                  req=urllib.request.Request(url,headers=headers)
                  with urllib.request.urlopen(req,timeout=40) as f: data=f.read(8_000_001)
                  if not(35_000<len(data)<8_000_000):raise ValueError("Unexpected image length")
                  with Image.open(io.BytesIO(data)) as test:test.verify()
                  im=ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert("RGB")
                  if im.size!=expected:raise ValueError("Source dimensions unexpected, got "+str(im.size))
                  if variant.startswith("Commons original") and hashlib.sha1(data).hexdigest()!=x["sha1"]:
                     raise ValueError("Original hash disagrees with source Commons page")
                  downloaded=(im,data,variant,url)
                  break
              except Exception as e:
                  fail.append(variant+": "+str(e))
                  if not attempt:time.sleep(3)
          if downloaded:break
      if not downloaded:raise ValueError("Both exact-file sources failed: "+"; ".join(fail)[-700:])
      im,data,variant,url=downloaded
      if target.exists():raise ValueError("Destination unexpectedly exists; do not overwrite")
      target.parent.mkdir(parents=True,exist_ok=True)
      im.save(target,format="JPEG",quality=90,optimize=True)
      sha256=hashlib.sha256(target.read_bytes()).hexdigest()
      j["images"].append({
        "file":relative,"role":x["role"],"creator":x["author"],
        "license":x["license"],"license_url":x["license_url"],
        "source_page":x["page"],"source_photo":x["source_photo"],
        "original_commons_sha1":x["sha1"],"download_variant":variant,
        "retrieved_url":url,"archived_sha256":sha256,
        "modifications":"JPEG reencoded as RGB and all EXIF/GPS removed; overlay labels added in gallery but not raster image",
        "public_reuse":"Exact image-specific CC license with creator/source/link and modifications; ShareAlike conditions respected on BY-SA image",
        "photo_status":"ORIGINAL PIXELS VISUALLY REVIEWED 2026-10-26; visible gross morphology arrows; NOT ROOT OR INNER LIGULE PHOTO"
      })
      panel={
        "label":x["label"],"scientific_name":"Dichanthelium commutatum",
        "image_url":str(target).replace("\\","/"),"image_fit":"contain",
        "image_role":x["role"],"caption":x["caption"],
        "why_it_matters":x["why"],
        "creator":x["author"],"license":x["license"],"license_url":x["license_url"],
        "source_page":x["page"],
        "modifications":"Original-source JPEG locally reencoded without EXIF/GPS; page overlays only, pixel accurate gross structures",
        "markers":x["markers"],
        "photo_status":"Same original photographer and taxon source inspected; supported structures ONLY, no measured inner collar or exposed root claims."
      }
      own=j["visual_comparison"]["items"]
      idx=next((k for k,p in enumerate(own) if p.get("scientific_name")!="Dichanthelium commutatum"),len(own))
      own.insert(idx,panel)
      report["local_originals_added"].append({"id":x["id"],"path":str(target),"dimensions":list(im.size),"sha256":sha256,"license":x["license"],"download_variant":variant,"arrows":len(x["markers"])})
  except Exception as e:
      if target.exists() and not any(a.get("file")==relative for a in j["images"]):target.unlink()
      report["held"].append({"id":x["id"],"reason":str(e)})
if report["local_originals_added"]:
   j["curation_status"]["photo_metadata_count"]=len(j["images"])
   j["curation_status"]["photo_files_present"]=sum((root/i["file"]).is_file() for i in j["images"] if i.get("file","").startswith("images/"))
   j["curation_status"]["own_photo_arrows"]=sum(len(x.get("markers",[])) for x in j["visual_comparison"]["items"] if x.get("scientific_name")=="Dichanthelium commutatum")
   j["learner_visual_status"]["image_count"]=len(j["images"])
   j["field_id_finish_pass"]["visible_photo_arrows"]=j["curation_status"]["own_photo_arrows"]
   j["field_id_finish_pass"]["lane4_leaf_base_and_seasonal_20261026"]={
      "status":"FIELD_READY_PHOTO_GAPS","actual_photo_additions":len(report["local_originals_added"]),
      "local_species_JPEGs":j["curation_status"]["photo_files_present"],
      "new_gross_arrows":sum(x["arrows"] for x in report["local_originals_added"]),
      "newly_documented":["real outer clasping leaf base and sheath mouth","leafy shoot/fascicle branching without open spring head"],
      "strictly_unresolved":["verified exposed same-specimen rooted perennial crown or basal rosette with roots","the actual free 0–0.5 mm inner ligule with scale","three 2.2–3.2 mm fully ripe spikelets with mm scale and glume structure","live rights-filtered public Pages deploy and marker QA"],
      "photo_reuse":"Alex Abair CC BY 4.0 and rockerBOO CC BY-SA 2.0; per-photo credit/license/source; no removal of conditional NC comparison photos",
      "live_pages_QA":"NOT VERIFIED"
   }
   j["visual_comparison"]["subtitle"]="Ten local species photos (two new verified upper leaf insertion/branching form views), then three look-alikes. Existing accurate reproductive panels retained. Roots/crown, inner ligule and mm-scaled mature spikelets remain photo holds.";
   j["photo_note"]+=" 2026-10-26: found two public-compatible exact-species photos of true outer sheath/leaf insertion and leafy lateral branching, physically archived and arrowed where genuinely visible. Still no exposed rooted crown or measured true inner ligule.";
   path.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
rp=pathlib.Path("reports/lane4-commutatum-seasonal-collar-20261026.json")
rp.parent.mkdir(exist_ok=True)
rp.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps(report))
