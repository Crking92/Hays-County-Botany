#!/usr/bin/env python3
"""Physically archive source-attributed open-license exact-taxon pine muhly
photos selected after contact-sheet and enlarged original pixel review.
Scientific species determination remains iNat needs-ID; no metric anatomy certification.
"""
import io,json,pathlib,hashlib,urllib.request,urllib.error,time
from PIL import Image,ImageOps
root=pathlib.Path("content/taxa/Poaceae/Muhlenbergia/muhlenbergia-dubia")
card=root/"species.json";data=json.loads(card.read_text())
assert data["id"]=="muhlenbergia-dubia"
src=json.loads(pathlib.Path("reports/lane3-pine-muhly-inat-sources-20261025.json").read_text())
zoom=json.loads(pathlib.Path("reports/lane3-pine-muhly-zoom-audit-20261025.json").read_text())
byid={x["photo"]["id"]:x for x in src["eligible"]}
zoom_byid={x["photo_id"]:x for x in zoom["photos"]}
selection=[
 (325197748,"ligule-junction-carlos-martorell-ccby.jpg",
  "Attached leaf blade and sheath junction; exposed pale membranous flap consistent with true ligule, but not ruler-calibrated or dissected",
  "Pine muhly — exposed blade/sheath junction (ligule candidate)",
  "Original CC BY photo shows a papery flap at the opened leaf junction; this is a good ligule-view candidate, but its free membrane, precise boundaries and 4–10 mm length are NOT independently specimen-verified. No anatomy arrow yet."),
 (321497847,"mature-panicle-spikelets-carlos-martorell-ccby.jpg",
  "Mature clustered lanceolate spikelet-like units photographed close-up; no individual glume, lemma or awn origin independently dissected",
  "Pine muhly — photographed mature flowering units",
  "An enlarged actual source-identified mature grass head. It supports seeing many narrow reproductive units, NOT measured or separately identified glumes, lemmas, awns or exact spikelet dimensions."),
 (665790824,"flowering-head-cleveland-powell-ccby.jpg",
  "Flowering panicle tip supported on the photographer's fingers with many narrow spikelet-like units; finger gives non-metric scale",
  "Pine muhly — intact flowerhead against fingers",
  "A separate source-identification photographed near fingers for visual size reference. No millimeter ruler or individual spikelet dissection; independent species identification remains provisional."),
]
report={"added":[],"holds":[],"source_audit":"reports/lane3-pine-muhly-inat-sources-20261025.json","original_pixel_review":"reports/lane3-pine-muhly-zoom-audit-20261025.json","gallery_status":"SOURCE_DETERMINED_NEEDS_ID__MICRO_METRICS_PENDING"}
def get(url):
 req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyVisualLearner/1.0 (CC BY photo and source credit archive, github.com/Crking92/Hays-County-Botany)"})
 for trial in range(3):
  try:
   with urllib.request.urlopen(req,timeout=40) as res:return res.read(13000001)
  except urllib.error.HTTPError as e:
   if e.code!=429 or trial==2:raise
   time.sleep(6*(trial+1))
for pid,filename,role,label,caption in selection:
 try:
  row=byid[pid];p=row["photo"];obs=row["observation"]
  if p["license_code"]!="cc-by":raise ValueError("source photo no longer open CC BY")
  if pid not in zoom_byid:raise ValueError("photo original never separately reviewed at pixel level")
  if str(pid) not in p["original_url"]:raise ValueError("source photo ID/URL mismatch")
  if any(str(pid) in str(x.get("source_page","")) for x in data["images"]):raise ValueError("photo already in species gallery")
  raw=get(p["original_url"])
  fullsha=hashlib.sha256(raw).hexdigest()
  if fullsha!=zoom_byid[pid]["sha256"]:raise ValueError("original photo bytes changed from reviewed pixels")
  with Image.open(io.BytesIO(raw)) as im:im.verify()
  with Image.open(io.BytesIO(raw)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   if min(im.size)<900:raise ValueError("photo resolution too small")
   src_size=list(im.size)
   im.thumbnail((2100,2100))
   out=io.BytesIO();im.save(out,"JPEG",quality=90,optimize=True);blob=out.getvalue()
  rel="images/"+filename;dest=root/rel
  if dest.exists():raise ValueError("existing image name protected")
  dest.write_bytes(blob)
  creator="Carlos Martorell" if "Carlos" in p["attribution"] else "Cleveland Powell"
  source=f"https://www.inaturalist.org/photos/{pid}"
  imgrec={"file":rel,"role":role,"creator":creator,"license":"CC BY","source_page":source,"source_observation":f"https://www.inaturalist.org/observations/{obs}","source_photo_id":pid,"original_source_photo_url":p["original_url"],"original_source_sha256":fullsha,"archive_sha256":hashlib.sha256(blob).hexdigest(),"source_dimensions":src_size,"source_determination":"Muhlenbergia dubia (iNaturalist observation; needs-ID not independently vouchered)","taxonomic_caution":"Reported source taxon, needs-ID; visually similar Muhlenbergia rigens and other muhly species must be independently considered before definitive teaching label.","public_reuse":"CC BY source photo; credit creator/photo link. JPEG re-encoded without EXIF. Public website can publish under proper attribution.","photo_review":"Actual original enlarged pixels and separate independent photo contact-sheet inspected; coarse visible role reviewed, submillimeter dissections not proven."}
  data["images"].append(imgrec)
  data["visual_comparison"]["items"].append({"label":label,"scientific_name":"Muhlenbergia dubia (source reported, provisional)","image_url":str(root/rel),"image_fit":"contain","image_role":role,"caption":caption,"why_it_matters":"Provides genuine close diagnostic teaching view, beyond habit photos, while clearly holding taxon verification and calibrated microanatomy.","creator":creator,"license":"CC BY","source_page":source,"photo_status":"LOCAL_JPEG_VERIFIED__SOURCE_TAXON_NEEDS_ID__METRIC_MACRO_UNVERIFIED","markers":[]})
  report["added"].append({"image":str(dest),"photo_id":pid,"source":source,"license":"CC BY","archive_sha256":hashlib.sha256(blob).hexdigest(),"bytes":len(blob),"role":role})
 except Exception as e:report["holds"].append({"photo_id":pid,"reason":str(e)[:260]})
if report["added"]:
 data["learner_visual_status"]["image_count"]=len(data["images"])
 data["learner_visual_status"]["status"]="FIELD_READY_PHOTO_GAPS"
 data["learner_visual_status"]["note"]="Now 2 prior habit photographs plus up to 3 archived CC BY anatomical candidates: exposed attached collar, enlarged mature reproductive units and a whole flowering tip. Source iNat taxon is needs-ID and 1-mm scale/glume/lemma dissections remain missing."
 data["curation_status"]["photo_files_present"]=sum(z.get("file","").startswith("images/") for z in data["images"])
 data["curation_status"]["photo_metadata_count"]=len(data["images"])
 data["lane3_anatomy_archive_20261025"]={"status":"LOCALLY_ARCHIVED_SOURCE_DETERMINED_CLOSEUP_PHOTOS__SCIENTIFIC_AND_METRIC_HOLDS","added_photo_ids":[z["photo_id"] for z in report["added"]],"source_license":"CC BY","pixel_visual_review":"Enlarged full-original source views screened; no submillimeter arrows placed","hard_holds":["True detached/free ligule measured 4–10 mm on a species-verified specimen with mm ruler","Independently identified specimen fully dissected into persistent 2–3 mm paired glumes, 3.8–5 mm fertile lemma, hairy callus","Matched verified M. rigens ligule and mature spikelet at same scale","Original source observations listed needs-ID, do not mark taxon expert-certified or native-to-Hays from these"],"public_page_status":"Not verified"}
 card.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
pathlib.Path("reports/lane3-pine-muhly-anatomy-archive-20261025.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps(report))
