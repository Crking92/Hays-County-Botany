#!/usr/bin/env python3
"""Photo-specific, source-verified Paspalum NOTATUM look-alike for P. distichum.

Do not count the look-alike as an own-species knotgrass photograph.
"""
import hashlib,io,json,pathlib,time,urllib.request
from PIL import Image,ImageOps
root=pathlib.Path("content/taxa/Poaceae/Paspalum/paspalum-distichum")
p=root/"species.json"
j=json.loads(p.read_text(encoding="utf-8"))
assert j["id"]=="paspalum-distichum"
assert j["field_id_finish_pass"]["stage"]=="FIELD_READY_PHOTO_GAPS"
source="https://commons.wikimedia.org/wiki/File:Paspalum_notatum_flowerhead9_(7391323812).jpg"
sorig="https://upload.wikimedia.org/wikipedia/commons/6/68/Paspalum_notatum_flowerhead9_%287391323812%29.jpg"
basename="paspalum-notatum-harry-rose-v-racemes-7391323812.jpg"
dest=root/"images"/basename
report={"species":"Paspalum distichum","different_taxon":"Paspalum notatum","added":[],"held":[],"license":"Harry Rose individual original CC BY 2.0; Wikimedia FlickrReviewR 2015-05-20","source_page":source}
target="content/taxa/Poaceae/Paspalum/paspalum-distichum/images/"+basename
if any(x.get("image_url")==target for x in j["visual_comparison"]["items"]):
    report["held"].append("Already published compare panel")
else:
  try:
    variants=[
      (sorig,(2592,1944),"Commons exact original"),
      ("https://thumb.wikimedia.org/wikipedia/commons/thumb/6/68/Paspalum_notatum_flowerhead9_%287391323812%29.jpg/1280px-Paspalum_notatum_flowerhead9_%287391323812%29.jpg",(1280,960),"Commons exact image 1280px derivative"),
      ("https://thumb.wikimedia.org/wikipedia/commons/thumb/6/68/Paspalum_notatum_flowerhead9_%287391323812%29.jpg/960px-Paspalum_notatum_flowerhead9_%287391323812%29.jpg",(960,720),"Commons exact image 960px derivative"),
    ]
    downloaded=None;fails=[]
    for uri,expected,variant in variants:
      for attempt in range(2):
        try:
          req=urllib.request.Request(uri,headers={"User-Agent":"Mozilla/5.0 (HaysCountyBotany educational CC image archiver)","Accept":"image/jpeg,image/*;q=0.8"})
          with urllib.request.urlopen(req,timeout=25) as resp:raw=resp.read(6000000)
          if not(40000<len(raw)<6000000):raise ValueError("Invalid image length")
          with Image.open(io.BytesIO(raw)) as x:x.verify()
          im=ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
          if tuple(im.size)!=expected:raise ValueError("Unexpected source dimensions "+str(im.size))
          downloaded=(im,uri,raw,variant)
          break
        except Exception as e:
          fails.append(variant+": "+str(e))
          if not attempt:time.sleep(5)
      if downloaded:break
    if not downloaded:raise RuntimeError("Only verified Commons file downloads attempted; "+str(fails)[-600:])
    im,download_url,raw,variant=downloaded
    if dest.exists():raise ValueError("Existing JPEG path not overwritten")
    dest.parent.mkdir(parents=True,exist_ok=True)
    im.save(dest,format="JPEG",quality=91,optimize=True)
    digest=hashlib.sha256(dest.read_bytes()).hexdigest()
    j["images"].append({
      "file":"images/"+basename,
      "scientific_name":"Paspalum notatum",
      "comparison_only":True,
      "role":"DIFFERENT SPECIES matched Paspalum notatum two-raceme V shaped flowering photo for Paspalum distichum",
      "creator":"Harry Rose (Macleay Grass Man)",
      "license":"CC BY 2.0",
      "license_url":"https://creativecommons.org/licenses/by/2.0/",
      "source_page":source,
      "original_flickr":"https://www.flickr.com/photos/73840284@N04/7391323812",
      "download_variant":variant,
      "raw_image_sha256":hashlib.sha256(raw).hexdigest(),
      "archived_sha256":digest,
      "modifications":"Original/taxon-specified file re-encoded JPEG with EXIF/GPS stripped; separate overlay labels",
      "public_reuse":"Individually attributed CC BY 2.0, source/photo and license links needed",
      "photo_status":"Different species contrast only; observed V-shaped pair is NOT sufficient to call a knotgrass"
    })
    j["visual_comparison"]["items"].append({
      "label":"LOOK-ALIKE · Paspalum notatum (bahiagrass) ALSO has V-shaped racemes",
      "scientific_name":"Paspalum notatum",
      "image_url":target,
      "image_fit":"contain",
      "image_role":"Real independently identified different-species two-branched Bahia grass inflorescence with larger green spikelets and brown reproductive structures; not Paspalum distichum",
      "caption":"Harry Rose's exact labelled Bahia grass photo clearly shows two near-upright spikelet-bearing racemes converging in a V, just like the quick first impression of knotgrass. Do not use 'two seedhead arms' as identification proof. Follow each specimen to an actual root-bearing basal stem, then compare mature spikelets, glumes and ligules.",
      "why_it_matters":"Prevents the common mistake of treating Paspalum distichum's two-branched head as unique; the knotgrass root-bearing stolons/rhizomes and true reproductive parts must agree.",
      "creator":"Harry Rose (Macleay Grass Man)",
      "license":"CC BY 2.0",
      "license_url":"https://creativecommons.org/licenses/by/2.0/",
      "source_page":source,
      "markers":[
         {"label":"Left bahiagrass raceme","label_x":8,"label_y":8,"target_x":41,"target_y":42},
         {"label":"Right bahiagrass raceme","label_x":73,"label_y":10,"target_x":53,"target_y":43},
         {"label":"Same V-shaped fork!","label_x":75,"label_y":81,"target_x":49,"target_y":80}
      ],
      "photo_status":"Actual original image was human pixel-reviewed 2026-10-26; visible V and branches arrows only. Taxon is Paspalum notatum, NOT knotgrass. Original Commons and Flickr rights explicitly recorded; source image sanitized."
    })
    j["curation_status"]["photo_metadata_count"]=len(j["images"])
    j["curation_status"]["photo_files_present"]=sum((root/x["file"]).is_file() for x in j["images"])
    j["field_id_finish_pass"]["lane4_bahia_compare_20261026"]={
      "stage":"FIELD_READY_PHOTO_GAPS",
      "new_lookalike_photos":1,
      "own_species_photo_files":sum((root/x["file"]).is_file() for x in j["images"] if not x.get("comparison_only",False)),
      "lookalike_photo_files":sum((root/x["file"]).is_file() for x in j["images"] if x.get("comparison_only",False)),
      "new_lookalike_arrows":3,
      "lesson":"Even clean 2-raceme V does not distinguish Paspalum distichum from Paspalum notatum. Confirm rooted growth form and mature spikelet parts.",
      "remaining":["Paspalum distichum live-rooted aboveground stolon and flowering head same specimen","Mature measured upper glume and sterile/fertile lemma dissection","Accurately measured inner ligule with 1mm scale","Complete live Pages and mobile image arrow QA"],
      "pages_QA":"not independently verified"
    }
    j["photo_note"]+=" 2026-10-26: site-safe CC BY 2.0 true Paspalum notatum lookalike JPEG physically archived and labelled a DIFFERENT species, three broad branch/fork arrows. Knotgrass now has the crucial V-head comparison and true root-base photo."
    p.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    report["added"].append({"file":str(dest),"dimensions":list(im.size),"sha256":digest,"url":download_url,"panels":1,"arrows":3})
  except Exception as e:
    if dest.exists() and not any(x.get("file")=="images/"+basename for x in j["images"]):
        dest.unlink()
    report["held"].append(str(e))
rp=pathlib.Path("reports/lane4-distichum-bahia-lookalike-20261026.json")
rp.parent.mkdir(exist_ok=True)
rp.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps(report))
