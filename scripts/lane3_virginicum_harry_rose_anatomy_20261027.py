#!/usr/bin/env python3
"""Lane 3: install only pixel-inspected Harry Rose CC BY 2.0 Anatherum virginicum photos.
Originals independently viewed, source license individually documented at Commons.
Make no ligule, paired-glume, same-plant crown claims from these two images.
"""
from __future__ import annotations
import hashlib,io,json,pathlib,time,urllib.request,urllib.parse
from PIL import Image,ImageOps
ROOT=pathlib.Path("content/taxa/Poaceae/Anatherum/anatherum-virginicum")
CARD=ROOT/"species.json"
REPORT=pathlib.Path("reports/lane3-broomsedge-harry-rose-photos-20261027.json")
SOURCES=[
 dict(id="6802476704",name="harry-rose-virginicum-open-spathe-silky-raceme-ccby2.jpg",
   raw="https://upload.wikimedia.org/wikipedia/commons/1/11/Andropogon_virginicus_flowerhead_racemes_%286802476704%29_%282%29.jpg",
   commons="https://commons.wikimedia.org/wiki/File:Andropogon_virginicus_flowerhead_racemes_(6802476704)_(2).jpg",
   label="BROOMSEDGE — real exposed silky flowering branch and enclosing spathe",
   role="Photographed, actual pale spathe/bract with emerging feathery slender raceme branch from source-identified A. virginicus; not a complete same-plant spikelet/glume dissection",
   caption="Harry Rose's actual A. virginicus (broomsedge) flowering spathe. The narrow golden leaflike bract runs diagonally above the hand, and a hairy, pale-white flowering branch projects sideways. Photo made in Australia, where the same species is introduced: this does not independently document a native Hays County specimen. The two arrows indicate only visible spathe and silky reproductive branch, not unmeasured sessile/pedicellate spikelets.",
   why="A real recognizable spathe-covered broomsedge branch, especially useful against un-spathed native little bluestem.",
   markers=[{"label":"Narrow straw-colored spathe (floral bract)","label_x":2,"label_y":9,"target_x":53,"target_y":35},
            {"label":"Exposed branch with long white dispersal hairs","label_x":61,"label_y":77,"target_x":57,"target_y":49}]),
 dict(id="6948584315",name="harry-rose-virginicum-hairy-dispersal-unit-ccby2.jpg",
   raw="https://upload.wikimedia.org/wikipedia/commons/1/1f/Andropogon_virginicus_seed1_%286948584315%29_%282%29.jpg",
   commons="https://commons.wikimedia.org/wiki/File:Andropogon_virginicus_seed1_(6948584315)_(2).jpg",
   label="BROOMSEDGE — mature wind-dispersal unit with radiating silky hairs",
   role="True source-identified detached seed-bearing dispersal unit magnified against fingertips: actual narrow pointed central bracts and radiating long white hairs; glumes/awn/floret identities not dissected and no millimeter scale",
   caption="Harry Rose CC BY 2.0 photograph of a detached mature broomsedge dispersal unit. Long translucent silky hairs radiate from a narrow central bract structure. The fingertip shows informal scale, not a calibrated ruler. Do not call this individual hair a lemma awn, or the bract a measured glume, without specimen dissection.",
   why="Demonstrates what disperses in the wind from the grass, with real close-up silky hairs rather than an unrelated seedhead.",
   markers=[{"label":"Long spreading translucent dispersal hairs","label_x":66,"label_y":23,"target_x":63,"target_y":41},
            {"label":"Narrow central bract structure; not dissected","label_x":3,"label_y":16,"target_x":49,"target_y":40}])
]
HEADERS={"User-Agent":"HaysCountyBotanyNoncommercialFieldLearner/1.0 (grass image archival; educational)","Accept":"image/jpeg,image/*"}
def fetch(src):
  tries=[
    src["raw"],
    "https://commons.wikimedia.org/wiki/Special:Redirect/file/"+urllib.parse.quote("Andropogon virginicus "+("flowerhead racemes" if src["id"]=="6802476704" else "seed1")+" ("+src["id"]+") (2).jpg").replace("%2F","/")
  ]
  errors=[]
  for url in tries:
    for attempt in range(2):
      try:
        req=urllib.request.Request(url,headers=HEADERS)
        with urllib.request.urlopen(req,timeout=38) as response:
          raw=response.read(5_000_001)
        if not 20000<len(raw)<5000000:raise ValueError("Unexpected bytes length: "+str(len(raw)))
        with Image.open(io.BytesIO(raw)) as im:
          assert im.format=="JPEG" and min(im.size)>=900,(im.format,im.size)
          rgb=ImageOps.exif_transpose(im).convert("RGB")
          rgb.thumbnail((2200,2200))
          buffer=io.BytesIO()
          rgb.save(buffer,"JPEG",quality=91,optimize=True,exif=b"")
          clean=buffer.getvalue()
          dims=list(rgb.size)
        with Image.open(io.BytesIO(clean)) as im:
          assert not im.getexif().get(34853) and im.format=="JPEG"
          im.verify()
        return clean,dims,url,errors
      except Exception as e: errors.append(type(e).__name__+":"+str(e)[:170]);time.sleep(1)
  raise RuntimeError("Unable to download "+src["commons"]+"; "+" | ".join(errors))
def main():
  j=json.loads(CARD.read_text())
  assert j["id"]=="anatherum-virginicum"
  items=j["visual_comparison"]["items"]
  imgs=j["images"]
  inserted=[];blocks=[]
  for src in SOURCES:
    dst=ROOT/"images"/src["name"]
    if dst.exists() or any(x.get("image_url")==dst.as_posix() for x in items):
      blocks.append({"source":src["commons"],"reason":"already installed; no duplicate"});continue
    try:clean,dims,url,errors=fetch(src)
    except Exception as e:
      blocks.append({"source":src["commons"],"reason":str(e)});continue
    dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_bytes(clean)
    digest=hashlib.sha256(clean).hexdigest()
    frame={"label":src["label"],"scientific_name":"Anatherum virginicum",
      "image_url":dst.as_posix(),"image_fit":"contain","image_role":src["role"],
      "caption":src["caption"],"why_it_matters":src["why"],
      "creator":"Harry Rose","license":"CC BY 2.0",
      "license_url":"https://creativecommons.org/licenses/by/2.0/",
      "source_page":src["commons"],"original_flickr_id":src["id"],
      "source_taxon_name":"Andropogon virginicus (synonym of canonical Anatherum virginicum)",
      "photo_review":"Actual source photograph visually inspected before upload: spathe, hairy raceme and detached mature dispersal unit; no true ligule, microscopic glumes or authenticated Hays roots claimed.",
      "source_locality":"Australia (species introduced there; taxon same but not Texas-local photograph)",
      "modification_note":"Source JPEG resized to 2200px max, re-encoded quality 91 and all EXIF/GPS removed; arrows are separate website overlays",
      "photo_status":"EXACT_SPECIES_CC_BY_2_0_PHYSICALLY_ARCHIVED_REPRODUCTIVE_ONLY",
      "markers":src["markers"]}
    items.append(frame)
    imgs.append({"file":"images/"+src["name"],"role":src["role"],"creator":"Harry Rose",
      "license":"CC BY 2.0","license_url":"https://creativecommons.org/licenses/by/2.0/",
      "source_page":src["commons"],"source_flickr_photo_id":src["id"],
      "original_download_url":url,"source_taxon_name":"Andropogon virginicus",
      "image_dimensions":dims,"sha256":digest,"modifications":frame["modification_note"],
      "public_reuse":"YES under individual CC BY 2.0 photo license with creator, source, version and modifications",
      "photo_status":"PHYSICALLY_ARCHIVED_CC_BY_2_REPRODUCTIVE_ANATOMY"} )
    inserted.append({"flickr_id":src["id"],"file":dst.as_posix(),"sha256":digest,"dimensions":dims,"arrows":len(src["markers"])})
  REPORT.parent.mkdir(parents=True,exist_ok=True)
  j["visual_comparison"]["subtitle"]="Source verified CC BY 2.0 broomsedge true flowering-spathe and wind-dispersal detail now accompany existing 2 field views. An actual opened ligule, calibrated spikelet glumes and Texas rooted flowering specimen remain missing."
  if inserted:
    j["visual_comparison"]["overlay_note"]+=" 2026-10-27: individual Harry Rose CC BY 2.0 source photographs added after full-pixel inspection; four gross-structure arrow targets only. Anatomical free ligule and measured sessile/pedicellate pair are NOT proven."
    j["learner_visual_status"]["image_count"]=len(imgs)
    j["learner_visual_status"]["status"]="FIELD_READY_PHOTO_GAPS"
    j["learner_visual_status"]["note"]=str(len(imgs))+" local species-identified images, including actually photographed spathe and mature silky propagule. True inner ligule, 1 mm spikelet/glume proof, connected rooted Texas flowering clump and look-alike matched anatomy remain missing."
    if isinstance(j.get("field_photo_quickcheck"),dict):
      j["field_photo_quickcheck"]["featured_photo_indices"]=list(dict.fromkeys(list(j["field_photo_quickcheck"].get("featured_photo_indices",[]))+list(range(len(items)-len(inserted),len(items)))))
      j["field_photo_quickcheck"]["steps"].append("In new Harry Rose CC BY 2.0 photo panels, recognize the real narrow floral spathe with an exposed silky flowering branch and a separate mature dispersal unit. Australian locality does not establish Hays provenance; the free ligule and individual measured paired spikelets are not shown.")
    j.setdefault("field_id_finish_pass",{})["lane3_virginicum_spathe_photos_20261027"]={
      "status":"ACTUAL_REPRODUCTIVE_PHOTOS_INSTALLED; SIX_ROLE_GAPS_REMAIN",
      "new_image_ids":[x["flickr_id"] for x in inserted],
      "new_browser_arrows":sum(x["arrows"] for x in inserted),
      "not_completed":["free inner ligule with mm scale","rooted whole flowering Texas plant in one view","1mm calibrated sessile/pedicellate spikelet pair","matched lookalike anatomy"],
      "photo_source_country":"Australia, where species introduced (no county nativity claim)"
    }
    CARD.write_text(json.dumps(j,ensure_ascii=False,indent=2)+"\n")
  result={"species":"Anatherum virginicum","status":"REAL_SOURCE_PHOTO_INSTALL" if inserted else "SOURCE_DOWNLOAD_HOLD",
      "installed":inserted,"blocked":blocks,"image_records_after":len(imgs),
      "gallery_panels_after":len(items),"additional_arrows":sum(i["arrows"] for i in inserted),
      "policy":"CC BY 2.0 exact photo verified Harry Rose; retain attribution and changes"}
  REPORT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
  print(json.dumps(result))
  if not inserted:raise RuntimeError("Source unavailable: exact blockers recorded in runner log; do not mark progress.")
if __name__=="__main__":main()
