#!/usr/bin/env python3
"""Lane 3: archive five distinct CC0 exact-taxon Muhlenbergia utilis field photographs.

Only exact IDs in the live 2026-10-26 source inventory and zero-rights CC0 licenses.
No arrows until original local JPEGs are visually inspected separately.
"""
import json,io,hashlib,pathlib,urllib.request
from PIL import Image,ImageOps
root=pathlib.Path("content/taxa/Poaceae/Muhlenbergia/muhlenbergia-utilis")
card=root/"species.json"
manifest=json.loads(pathlib.Path("reports/lane3-utilis-inat-open-license-scout-20261026.json").read_text())
assert manifest["taxon"]=="Muhlenbergia utilis"
byid={int(x["photo_id"]):x for x in manifest["sources"]}
photos=[
 (410577667,"LOCAL HABITAT — wild creeping patch beneath limestone","Whole in-situ source-determined plant patch on a limestone-lined riparian bank; true underground roots or rhizomes not exposed.","Real Uvalde County field photograph of a gray-green threadlike creeping grass patch under a limestone bank overhang. Natural growth position is visible, but the actual rhizome and attached flowering shoots cannot be distinguished with certainty."),
 (260420284,"LIVING GROUND-LEVEL PATCH — multiple very fine shoots","Central Texas source-determined small in-ground grass patch with many fine green shoots and litter; no bare crown or actual roots exposed.","Burnet County field photograph shows the closely grouped fine green leafy shoots emerging within a natural litter layer. This teaches plant scale and patch architecture but does not show exposed crown, knotty roots, or scaly buried rhizome."),
 (410577686,"VERY FINE SHOOTS — hand for informal size comparison","Visible very fine green shoots spread over a hand; potentially mixed grass background, no true collar or root confirmed.","Uvalde County photograph shows thin living leaves and slender branching stems at finger scale within the original stand. Avoid treating background stems as automatically connected or independently confirmed taxon anatomy."),
 (410577695,"BLADE–SHEATH DETAIL — possible pale ligule, NOT measured","Close view of green longitudinally ribbed blade adjacent to pale membranous sheath edge; ligule candidate, actual free edge requires original pixel inspection.","An unusually close source-identified Uvalde photograph includes a green ribbed blade/sheath section next to a pale upright tissue projection. It is a promising collar/ligule candidate, NOT an independently exposed or calibrated 0.2–0.8 mm ligule."),
 (410577679,"NARROW ATTACHED FLOWERING HEAD — small slender spikelets","True source-identified narrow terminal inflorescence with individually visible small spikelets along a flowering branch.","Wild Uvalde County close-up shows a narrow flowerhead with slender individually attached spikelets. The real whole reproductive branch is visible; individual glume and lemma lengths remain unmeasured.")
]
cc0="https://creativecommons.org/publicdomain/zero/1.0/"
data=json.loads(card.read_text(encoding="utf8"))
assert data["id"]=="muhlenbergia-utilis" and data["scientific_name"]=="Muhlenbergia utilis"
report={"status":"HOLD","taxon":"Muhlenbergia utilis","added":[],"holds":[],"preexisting_images":len(data["images"]),"preexisting_gallery_panels":len(data["visual_comparison"]["items"])}
def get(url):
 req=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotanyCC0EducationalPhotoArchive/1.0 (github.com/Crking92/Hays-County-Botany)","Accept":"image/jpeg,image/*"})
 with urllib.request.urlopen(req,timeout=35) as h:
  raw=h.read(16000001)
 assert 30000<len(raw)<=16000000
 return raw
for id,label,role,caption in photos:
 assert id in byid
 info=byid[id]
 assert info["taxon"]=="Muhlenbergia utilis" and info["license_code"]=="cc0" and info["quality_grade"]=="research"
 rel=f"images/aparejo-cc0-inat-{id}.jpg"
 dest=root/rel
 if any(x.get("file")==rel for x in data["images"]):
  if not dest.exists():raise RuntimeError("Canonical photo has missing bytes: "+rel)
  report["holds"].append({"photo_id":id,"status":"ALREADY_ARCHIVED; preserved"})
  continue
 if dest.exists():raise RuntimeError("Orphan file exists without canonical metadata: "+rel)
 original=info["photo_url"].replace("/square.","/original.")
 try:
  raw=get(original)
  with Image.open(io.BytesIO(raw)) as im:
   assert im.format=="JPEG"
   im.verify()
  with Image.open(io.BytesIO(raw)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   if min(im.size)<550:raise RuntimeError("Insufficient smallest dimension for field role")
   original_dims=list(im.size)
   im.thumbnail((2400,2400),Image.Resampling.LANCZOS)
   buff=io.BytesIO()
   im.save(buff,"JPEG",quality=90,optimize=True)
   jpg=buff.getvalue()
  with Image.open(io.BytesIO(jpg)) as im:
   assert not im.getexif().get(34853)
   im.verify()
  dest.parent.mkdir(parents=True,exist_ok=True)
  dest.write_bytes(jpg)
  sha=hashlib.sha256(jpg).hexdigest()
  item={
   "file":rel,"role":role,"creator":info["creator_source"],
   "license":"CC0 1.0","license_url":cc0,
   "source_page":info["source_page"],"source_observation":info["observation"],
   "photo_source_id":id,"source_observation_id":info["observation_id"],
   "source_taxon":"Muhlenbergia utilis (iNaturalist Research Grade, not independently vouchered)",
   "source_place":info["place_guess"],"original_source_image":original,
   "original_sha256":hashlib.sha256(raw).hexdigest(),
   "archive_sha256":sha,"original_dimensions":original_dims,
   "public_reuse":"CC0 public domain dedication; retain exact photo source attribution and photographer metadata as available",
   "modifications":"Resaved JPEG max 2400px with EXIF/GPS removed; source photo itself not marked; gallery arrows postponed until pixel inspection.",
   "photo_status":"Exact photo ID and CC0 license confirmed at iNaturalist; role provisionally assigned from viewed contact sheet; no measured ligule, scaly rhizome or rooted crown certified"
  }
  panel={
   "label":label,"scientific_name":"Muhlenbergia utilis",
   "image_url":str(root/rel),"image_fit":"contain",
   "image_role":role,"caption":caption,
   "why_it_matters":"True local Central Texas source-ID, CC0 public-licensed photo representing a distinct crew identification role, not a replacement for live dissected ligament/rhizome microphoto.",
   "creator":info["creator_source"],"license":"CC0 1.0","license_url":cc0,
   "source_page":info["source_page"],"source_observation":info["observation"],
   "source_place":info["place_guess"],
   "photo_status":"Archived full source original with source-specific CC0; anatomy described conservatively; browser arrows awaiting actual full-JPEG pixel audit.",
   "markers":[]
  }
  data["images"].append(item)
  items=data["visual_comparison"]["items"]
  insert=next((i for i,p in enumerate(items) if p.get("scientific_name")!="Muhlenbergia utilis"),len(items))
  items.insert(insert,panel)
  report["added"].append({"photo_id":id,"file":str(dest),"sha256":sha,
   "source_page":info["source_page"],"license":"CC0 1.0","original_dimensions":original_dims})
 except Exception as exc:report["holds"].append({"photo_id":id,"failure":str(exc)[:240]})
if report["added"]:
 data["curation_status"]["photo_metadata_count"]=len(data["images"])
 data["curation_status"]["photo_files_present"]=sum(str(x.get("file","")).startswith("images/") for x in data["images"])
 data["learner_visual_status"]["image_count"]=len(data["images"])
 data["visual_comparison"]["title"]="Aparejograss — riparian creeping patch, fine leaves, possible collar, narrow flowering head"
 data["visual_comparison"]["subtitle"]="Five new source-confirmed CC0 Central Texas field photos added to original three archived pictures. Full anatomy review pending: actual rhizomes, a free measured 0.2–0.8 mm ligule, and independently dissected spikelets not proven."
 data["visual_comparison"]["overlay_note"]="Lane 3 2026-10-26: five exact-source iNaturalist CC0 originals physically archived with separate field roles; all existing older panels and annotated lookalike kept. No new arrows yet; no tiny membranous ligule, rooted crown, or underground scaly rhizome named as observed without full JPEG inspection."
 data["field_id_finish_pass"]["stage"]="FIELD_READY_PHOTO_GAPS — 5 new locally licensed original photos including a narrow flowering head and close sheath/junction candidate; true belowground scaly rhizome, measured inner ligule and same rooted shoot proof NOT CLOSED"
 data["field_id_finish_pass"]["lane3_five_cc0_field_photos_20261026"]={
  "photo_ids":[id for id,_,_,_ in photos],
  "source_rights":"all individual CC0 at iNaturalist exact observation photo records",
  "new_local_photos":len(report["added"]),
  "uncleared_roles":["actually excavated scaly rhizome with nodes and attached shoots","free measured membranous true ligule at 0.2–0.8 mm","fully attached same-root complete plant with flowering head"],
  "morphology_authority":"2023 Central America Muhlenbergia taxonomic revision and Kew GrassBase; ranges are literature traits, not measurements made on these photographs"
 }
 data["curation_status"]["lane3_utilis_cc0_archive_20261026"]="Five source-specific CC0 exact species original photographs physically archived, provisional anatomical panel roles and no unseen-part arrows; previous three photos and science holds remain.";
 card.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
 report["status"]="ARCHIVED_SOURCE_CONFIRMED_NEEDS_PIXEL_ARROWS"
else:report["status"]="NO_NEW_IMAGES_WRITTEN"
report["current_photo_count"]=len(data["images"])
report["current_gallery_panels"]=len(data["visual_comparison"]["items"])
pathlib.Path("reports/lane3-utilis-five-cc0-archive-20261026.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print(json.dumps(report,indent=2))
