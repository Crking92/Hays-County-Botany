#!/usr/bin/env python3
"""Lane 2 Erioneuron pilosum — Tom Chester original-photo licensed real habit, white leaf margins, and hairy spikelets.
Reproduces source photographer's page photographs with full credit under the source-specific permission,
without calling any externally visible hair the tiny true ligule.
"""
import io,json,hashlib
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageOps

ROOT=Path("content/taxa/Poaceae/Erioneuron/erioneuron-pilosum")
CARD=ROOT/"species.json"
REPORT=Path("reports/lane2-erioneuron-tom-chester-field-photo-rights-20261026.json")
HOME="https://tchester.org/gc/plants/species/erioneuron_pilosum.html"
BASE="https://tchester.org/gc/plants/species/pix/erioneuron_pilosum/"
UA={"User-Agent":"Hays-Botany-Visual-Learner/1.0 (educational grass photo archive with source credit)"}
PERMIT="Permission is freely granted to reproduce any or all of this page as long as credit is given to me at this source:"
MEDIA=[
{
  "name":"erioneuron_pilosum_5_crop_35.jpg",
  "archive":"tom-chester-hairy-tridens-in-situ-heads-and-crown.jpg",
  "label":"NATURAL GROWTH · leafy tufts in rocky soil and complete attached woolly heads",
  "role":"Actual Arizona in-ground Erioneuron pilosum tuft with leaf clusters emerging from soil and intact stalks bearing several pale woolly flowering heads. ROOTS still belowground.",
  "caption":"Tom Chester's 2008 South Kaibab Trail field photo: real living low leaf clusters remain grounded among reddish rocks, with flowering culms that carry several complete compact pale woolly heads. The leafy crown is AT SOIL LEVEL, not dug out; roots and tiny inner ligule cannot be seen. Species determination follows Tom Chester's voucher-discussed field series, not a Hays County record.",
  "why":"Connects the basal leaf tufts and attached woolly flowering heads in a genuinely grown-in-ground plant, rather than isolated spikelets only.",
  "markers":[
    {"label":"Live leafy clump at soil (roots hidden)","label_x":5,"label_y":66,"target_x":46,"target_y":54},
    {"label":"Whole attached compact woolly head","label_x":75,"label_y":8,"target_x":68,"target_y":10}
  ]
},
{
  "name":"erioneuron_pilosum_4_crop_50.jpg",
  "archive":"tom-chester-hairy-tridens-narrow-white-edged-basal-leaves.jpg",
  "label":"FOLIAGE · narrow folded blades and visibly pale white leaf margins",
  "role":"Close natural field view of E. pilosum's distinctive narrow inward-folded gray-green basal blades edged with pale margins above brown leaf litter. Collars/ligules not opened.",
  "caption":"This source-identified live tuft shows the contrasting pale edges of several narrow basal blades and older straw-colored leaves arising close together. The white margin and folded cross-section are observable broad leaf clues. Do not infer a measured 0.35-mm true white ligule or exposed belowground root crown from this angle.",
  "why":"Adds the identifying real white-edged narrow folded leaves rather than another head-only gallery photograph.",
  "markers":[
    {"label":"Pale-edged narrow folded leaf blade","label_x":72,"label_y":16,"target_x":56,"target_y":27},
    {"label":"Clustered basal blades (no inner ligule visible)","label_x":5,"label_y":84,"target_x":43,"target_y":60}
  ]
},
{
  "name":"erioneuron_pilosum_3_crop_2.jpg",
  "archive":"tom-chester-hairy-tridens-woolly-spikelet-head-close.jpg",
  "label":"WOOLLY HEAD · real overlapping florets and conspicuous silvery hairs",
  "role":"High-detail real E. pilosum compact head with pointed overlapping pale spikelet parts and a profusion of thin white silk-like hairs beside photographer's fingers. No dissection to individually assign glumes or lemmas.",
  "caption":"Tom Chester's macro shows pale pointed overlapping flowering units and conspicuous soft hairs of the actual woolly head against a hand. Only visible white hairs and the overall overlapping spikelet units are arrowed. Do not assign individual glumes, 3-veined lemma, awn attachment, or floret notches without a separate clear scaled dissection.",
  "why":"Gives the crew an actual close photograph of why this tiny grass is called woollygrass while leaving glume-vs-lemma diagnosis open.",
  "markers":[
    {"label":"Silky hairs around flowering units","label_x":4,"label_y":22,"target_x":79,"target_y":45},
    {"label":"Overlapping pointed spikelet parts","label_x":78,"label_y":83,"target_x":41,"target_y":54}
  ]
}
]
def fetch(url,maxlen):
 with urlopen(Request(url,headers=UA),timeout=42) as response:
  data=response.read(maxlen+1)
  assert len(data)<=maxlen,"Unexpected large response"
  return response.url,data

def main():
 url,source=fetch(HOME,3_500_000)
 assert url.startswith("https://tchester.org/"),url
 html=source.decode("utf-8","replace")
 # Allow HTML tags between the quoted permission text; require both actual permission and photo author credit.
 assert "Permission is freely granted to reproduce any or all of this page" in html
 assert "Tom Chester" in html and "Copyright" in html
 j=json.loads(CARD.read_text(encoding="utf-8"))
 assert j["id"]=="erioneuron-pilosum"
 existing={x.get("source_page") for x in j["images"]}
 new_panels=[]
 installed=[]
 for p in MEDIA:
  original=BASE+p["name"]
  assert p["name"] in html,"Original photo no longer linked from permission source"
  assert original not in existing,"Photo previously installed; hold for duplicate"
  downloaded,raw=fetch(original,6_000_000)
  assert downloaded==original and len(raw)>25_000,(downloaded,len(raw))
  with Image.open(io.BytesIO(raw)) as source_img:
   assert source_img.format=="JPEG" and min(source_img.size)>=550,source_img.size
   dims=list(source_img.size)
   img=ImageOps.exif_transpose(source_img).convert("RGB")
  bio=io.BytesIO()
  img.save(bio,format="JPEG",quality=91,optimize=True)
  clean=bio.getvalue()
  with Image.open(io.BytesIO(clean)) as check:
   assert check.format=="JPEG" and not check.getexif(),"EXIF/GPS stripping failed"
  path=ROOT/"images"/p["archive"]
  path.parent.mkdir(parents=True,exist_ok=True)
  if path.exists():assert path.read_bytes()==clean,"Different source bytes at existing path"
  else:path.write_bytes(clean)
  rel="images/"+p["archive"]
  item={
   "file":rel,"role":p["role"],"creator":"Tom Chester",
   "license":"Author's explicit source-page credited-reproduction permission (not CC)",
   "license_url":HOME,"source_page":original,
   "source_permission_page":HOME,
   "source_photo_locality":"South Kaibab Trail, Grand Canyon, Coconino County, Arizona, 24 August 2008",
   "public_reuse":"Authorized for credited reproduction of page photographs at any/all page scope per source author; credit Tom Chester with source-page link. NOT general Creative Commons relicense.",
   "modifications":"RGB JPEG recompressed to remove EXIF/GPS, no cropping; separate non-destructive teaching arrows in gallery.",
   "photo_status":"Exact author source-page permission checked and original downloaded/pixel-reviewed 2026-10-26 for gross structures, not true ligule. Determination follows published author field identification, no Hays voucher."
  }
  j["images"].append(item)
  src_path="content/taxa/Poaceae/Erioneuron/erioneuron-pilosum/"+rel
  new_panels.append({
   "label":p["label"],"scientific_name":"Erioneuron pilosum",
   "image_url":src_path,"image_fit":"contain","image_role":p["role"],
   "caption":p["caption"]+" Photo © Tom Chester; reused with author's explicit credited-publication permission at "+HOME,
   "why_it_matters":p["why"],
   "creator":"Tom Chester","license":"Author's direct permission for credited reproduction (not CC)",
   "license_url":HOME,"source_page":original,"source_permission_page":HOME,
   "modifications":"Underlying RGB JPEG EXIF-scrubbed; UI adds separate arrows without altering pixels",
   "markers":p["markers"],
   "photo_status":"Original field-source pixels inspected. Gross anatomy only. True short 0.35-mm inner ligule and excavated roots are NOT visible."
  })
  installed.append({"file":str(path),"source":original,"source_dims":dims,"saved_bytes":len(clean),"sha256":hashlib.sha256(clean).hexdigest(),"arrows":len(p["markers"]),"role":p["role"]})
 # Existing 3 actual species panels are preserved, and new exact species panels enter before look-alikes.
 panels=j["visual_comparison"]["items"]
 at=next((i for i,x in enumerate(panels) if x.get("scientific_name")!="Erioneuron pilosum"),len(panels))
 panels[at:at]=new_panels
 j["field_photo_quickcheck"]["featured_photo_indices"]=list(range(at+len(new_panels)))
 j["field_photo_quickcheck"]["steps"]=[
  "FIELD HABIT FIRST: use Tom Chester's credited whole in-ground Arizona photo to follow the leafy cluster at ground level up the flowering culm to a compact woolly head. The root attachment is not exposed.",
  "WHITE LEAF EDGE NEXT: his close foliage photograph shows really pale white margins of narrow folded blades and crowded basal tillers, not a peeled-open inner ligule.",
  "FLORAL HAIRS NEXT: his close head shows silvery woolly hair and many pointed overlapping floret/spikelet parts; inspect real leaves and head together rather than identifying generic blond fluff.",
  *j["field_photo_quickcheck"]["steps"]
 ]
 j["field_photo_quickcheck"]["warning"]+=" 2026-10-26: three additional real source-identifed Tom Chester photographs were individually verified for explicit credited reproduction, physically archived and added as whole in-ground bunch, white-edged basal blades and woolly spikelet head with six new gross arrows. No actual exposed 0.35-mm inner ligule or scale; no underground root system. Keep user's private-only Calvin King original OUT of the gallery; preserve Joey NC photo-level terms."
 j["curation_status"]["photo_metadata_count"]=len(j["images"])
 j["curation_status"]["photo_files_present"]=sum(str(x.get("file","")).startswith("images/") for x in j["images"])
 j["curation_status"]["lane2_tom_chester_20261026"]="THREE SOURCE-PERMISSION REAL FIELD PHOTOS + SIX PIXEL-GROUNDED ARROWS; TRUE LIGULE AND ROOT HOLD"
 if isinstance(j.get("learner_visual_status"),dict):j["learner_visual_status"]["image_count"]=len(j["images"])
 j["field_id_finish_pass"]["stage"]="FIELD_READY_PHOTO_GAPS"
 j["field_id_finish_pass"]["lane2_tom_chester_20261026"]={
  "photographs_added":3,"gross_arrows":6,"permission":"Author explicitly permits credited reproduction of his species webpage/photos. Creative Commons NOT asserted.",
  "actual_photo_roles":["whole flowering tuft growing in Arizona red-soil habitat","close folded white-edged basal leaf margins","close hairy woolly flowering head"],
  "unmet_strict_roles":["true 0.35-mm inside ligule visible with mm scale","actual lifted fibrous crown and attached roots","hairy 3-nerved lemma with true short awn and shallow notch verified by scaled dissection"],
  "status":"FIELD_READY_PHOTO_GAPS"
 }
 j["photo_note"]=j.get("photo_note","")+"\n2026-10-26 Lane 2: three real Tom Chester field photos archived from South Kaibab AZ under explicit site-wide credited reproduction permission (not CC), showing living leafy tuft, white-edged folded leaf, woolly flowering head; six gross-organ arrows, all old Joey NC and user-private rights preserved. Inner ligule ~0.35 mm, roots and mature lemma parts still unconfirmed."
 CARD.write_text(json.dumps(j,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 REPORT.parent.mkdir(parents=True,exist_ok=True)
 REPORT.write_text(json.dumps({
  "species":"Erioneuron pilosum","date":"2026-10-26","source_page":HOME,
  "permission_original_text":PERMIT,"rights_basis":"Tom Chester explicit author credited-reproduction permission applies to full photo page and its 3 linked images; NOT a CC license.",
  "images_added":len(installed),"locally_archived_total":j["curation_status"]["photo_files_present"],
  "species_gallery_panels":sum(x.get("scientific_name")=="Erioneuron pilosum" for x in panels),
  "lookalike_panels":sum(x.get("scientific_name")!="Erioneuron pilosum" for x in panels),
  "arrows_added":sum(x["arrows"] for x in installed),"archived":installed,
  "old_private_photo_retained_out_of_public_panels":True,
  "old_joey_NC_photos_retained":True,
  "strict_completion":"FIELD_READY_PHOTO_GAPS — inner ligule still absent, root crown not excavated, lemma microanatomy not measured",
  "public_site_verified":False
 },indent=2)+"\n",encoding="utf-8")
 print("ERIONEURON_ARCHIVED",len(installed),"LOCAL",j["curation_status"]["photo_files_present"])
if __name__=="__main__": main()
