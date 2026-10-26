#!/usr/bin/env python3
"""Lane 3 exact Tridens albescens four-photo role enrichment.
Only image-specific CC0/CC BY, SHA-verified exact source originals.
No anatomical arrows until the archived originals are independently pixel inspected.
"""
import json,io,pathlib,urllib.request,hashlib
from PIL import Image,ImageOps
BASE=pathlib.Path("content/taxa/Poaceae/Tridens/tridens-albescens")
CARD=BASE/"species.json"
EVIDENCE=pathlib.Path("reports/lane3-tridens-albescens-photo-scout-20261026.json")
REPORT=pathlib.Path("reports/lane3-tridens-albescens-public-roles-20261026.json")
SELECT=[
 (750110822,408110125,"Sam Kieschnick","CC BY","Living rooted-in-place narrow grass tuft and upright culms","WHITE TRIDENS — in-ground green basal bunch","Many fine grass blades gather where stems meet soil, with upright culms visible. The roots and knotty rhizome remain BELOW ground and are not photographed."),
 (755441242,410721126,"Madalyn Chandler","CC BY","Actual flat green grass blades held beside their source plant","WHITE TRIDENS — leaf blades and sheathing growth","A source-identified grass leaf study shows real narrow green blade surfaces, useful to learn leaf width/texture. It does not open the true inner 0.2–0.5 mm hair-fringed ligule."),
 (743316869,404740196,"Rachel","CC BY","Actual green leaf attached beside culm","WHITE TRIDENS — blade and stem junction (not ligule)","A finger holds an actual green leaf where it joins a culm, showing the region crew should examine; the free inner ligule is not confirmed in these pixels."),
 (754601782,410314913,"iNaturalist CC0 image 754601782 (photographer not specified in photo attribution)","CC0","Actual crowded mature multifloret spikelets close to finger","WHITE TRIDENS — overlapping ripe pale spikelets","A strongly resolved source-identified terminal narrow head shows numerous tightly appressed overlapping whole spikelets. The photo is not a measured glume/lemma dissection.")
]
UA="HaysCountyBotany/1.0 (noncommercial CC license verified grass photo curation)"
def get(url,n=17000000):
 req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"image/jpeg,application/json"})
 with urllib.request.urlopen(req,timeout=40) as f:
  bs=f.read(n+1)
 if len(bs)>n:raise ValueError("Downloaded file too large")
 return bs
def api(url):return json.loads(get(url))
d=json.loads(CARD.read_text(encoding="utf-8"))
assert d["id"]=="tridens-albescens" and d["scientific_name"]=="Tridens albescens"
oldimages=d["images"];oldpanels=d["visual_comparison"]["items"]
assert len(oldimages)==2 and len(oldpanels)==6
e=json.loads(EVIDENCE.read_text())
assert e["inat_taxon_id"]==169945 and not e["failures"]
old_holds={k:json.dumps(d.get(k),sort_keys=True) for k in ("county_occurrences_target_zone","target_zone_count","native_target_zone_calculated","native_metrics_excluded","taxonomic_note")}
newmeta=[];newpanels=[];files={};installed=[]
obs={}
for pid,oid,credit,license_type,role,label,caption in SELECT:
 rec=next(x for x in e["candidate_photos"] if x["photo_id"]==pid and x["observation_id"]==oid)
 if not rec.get("source_sha256"):raise ValueError("Image original did not pass source image scout")
 expected="cc0" if license_type=="CC0" else "cc-by"
 assert rec["license_code"]==expected
 if license_type=="CC BY": assert credit.lower() in (rec.get("attribution") or "").lower()
 if oid not in obs:
  z=api("https://api.inaturalist.org/v1/observations/"+str(oid))
  assert len(z.get("results",[]))==1
  o=z["results"][0]
  assert o["taxon"]["id"]==169945 and o["taxon"]["name"]=="Tridens albescens" and o.get("quality_grade")=="research"
  obs[oid]=o
 original=next(x for x in obs[oid]["photos"] if x["id"]==pid)
 assert original.get("license_code")==expected
 if license_type=="CC BY":assert credit.lower() in (original.get("attribution") or "").lower()
 url="https://inaturalist-open-data.s3.amazonaws.com/photos/"+str(pid)+"/original.jpg"
 raw=get(url)
 assert hashlib.sha256(raw).hexdigest()==rec["source_sha256"]
 with Image.open(io.BytesIO(raw)) as im:
  assert im.format=="JPEG"
  im.verify()
 with Image.open(io.BytesIO(raw)) as im:
  im=ImageOps.exif_transpose(im).convert("RGB")
  assert min(im.size)>=800
  dims=[im.width,im.height]
  im.thumbnail((1800,1800),Image.Resampling.LANCZOS)
  buf=io.BytesIO()
  im.save(buf,"JPEG",quality=90,optimize=True)
  blob=buf.getvalue()
 with Image.open(io.BytesIO(blob)) as im:
  assert im.format=="JPEG" and not im.getexif().get(34853)
  im.verify()
 rel=f"images/tridens-albescens-inat-{pid}-{expected.replace('-','')}.jpg"
 dest=BASE/rel
 if dest.exists() or any(str(pid) in str(x.get("file","")) for x in oldimages):raise ValueError("Image path already installed")
 files[dest]=blob
 sha=hashlib.sha256(blob).hexdigest()
 src=f"https://www.inaturalist.org/photos/{pid}"
 obsurl=f"https://www.inaturalist.org/observations/{oid}"
 licenseurl="https://creativecommons.org/publicdomain/zero/1.0/" if license_type=="CC0" else "https://creativecommons.org/licenses/by/"
 newmeta.append({"file":rel,"role":role,"creator":credit,"photo_source_attribution":original.get("attribution"),
  "license":license_type,"license_code":expected,"license_url":licenseurl,"license_version_note":"Photo-specific iNaturalist code verified; no unverified license version claimed" if license_type=="CC BY" else "CC0 1.0",
  "source_page":src,"observation_source":obsurl,"source_photo_id":pid,"source_observation_id":oid,
  "source_type":"iNaturalist research-grade named-species observation, identification not independently herbarium-vouchered",
  "source_raw_url":url,"source_sha256":rec["source_sha256"],"local_sha256":sha,"source_dimensions":dims,
  "public_reuse":"Public educational site with original credited CC license; no commercial expansion without rights review",
  "modifications":"Resized to max 1800px, re-encoded JPEG, EXIF/GPS removed; no crops or baked-in anatomy arrows."})
 newpanels.append({"label":label,"scientific_name":"Tridens albescens","image_url":str(dest),"image_fit":"contain","image_role":role,
  "caption":caption,"why_it_matters":"Real species-source photograph of one of the practical whole habit, basal leaf or reproductive identification roles; not fabricated anatomy.",
  "creator":credit,"license":license_type,"license_url":licenseurl,"source_page":src,"observation_source":obsurl,
  "photo_status":"Full source photograph licensed, archived and SHA checked; fine-structure arrows pending full-pixel inspection, and source botanist voucher not confirmed","markers":[]})
 installed.append({"photo_id":pid,"observation_id":oid,"creator":credit,"license":license_type,"original_sha256":rec["source_sha256"],"sha256":sha,"file":str(dest),"source_page":src,"source_role":role})
d["images"]=oldimages+newmeta
d["visual_comparison"]["items"]=newpanels+oldpanels
d["visual_comparison"]["title"]="White tridens — live bunch, blade/sheath, tight head and local look-alikes"
d["visual_comparison"]["subtitle"]="Four new source-licensed in-ground tuft, blade, leaf/culm and spikelet photos lead the original two true white-tridens panicle images, then four clearly DIFFERENT-species purpletop/Texas tridens comparisons. Roots and true hair ligule not yet visibly exposed."
d["visual_comparison"]["overlay_note"]="2026-10-26 Lane 3: four new taxon-labelled CC0/CC BY original JPEGs physically installed, individual photo license and SHA256 checked. No speculative arrows until pixel inspection. All six original panels preserved in order after the additions, with four comparisons explicitly different species. Unvouchered county/nativity and microscopic hold retained."
ts=d["field_id_short_tiles"];assert len(ts)==6
ts[0]["photo_panel_indices"]=[0,4,5]
ts[0]["details"]="The living in-ground tuft (panel 1) adds practical whole-habit context to the two original genuine narrow flowering-head photographs (panels 5 and 6). Search for a tufted perennial with 8–25 cm contracted, upright densely crowded spikelets, but root fibers and knotty rhizome remain hidden under the soil in panel 1.";
ts[0]["status"]="TRUE LIVING GRASS BASE + TWO OPEN-FIELD FULL HEAD PHOTOS; EXPOSED CROWN STILL MISSING"
ts[1]["photo_panel_indices"]=[0,1,2]
ts[1]["details"]="New exact source tuft (gallery panel 1) and green blade/culm photographs (panels 2–3) display real vegetative architecture. The published short fringe-like true ligule about 0.2–0.5 mm must be found at the INNER blade–sheath joint on the SAME plant with a mm ruler. Neither observed node or leaf attachment alone proves the true ligule.";
ts[1]["status"]="REAL BASAL GROWTH/LEAF CONTEXT PRESENT; EXPOSED RHIZOME AND HAIR-FRINGED LIGULE STILL MISSING"
ts[2]["photo_panel_indices"]=[3,4,5]
ts[2]["details"]="The new (panel 4) close view contains clearly overlapping whole pale multi-flowered spikelets. Existing panels 5–6 provide true attached flowering-head context. Published 4–10 mm size and 4–10 florets must NOT be reported as measured from an uncalibrated close-up; dissect only if important to rule out a genuine look-alike.";
ts[2]["status"]="PHOTOGRAPHED MATURE SPIKELETS; MM SCALE AND FLORET COUNT STILL MISSING"
ts[3]["photo_panel_indices"]=[3]
ts[3]["status"]="REAL GROSS SPIKELET PHOTO; LOWER/UPPER GLUMES, LEMMA NERVES AND MUCRO NOT MEASURED"
ts[4]["photo_panel_indices"]=[4,6,8]
ts[5]["photo_panel_indices"]=[0,1,2,3,4,5,6,8]
d["field_photo_quickcheck"]["featured_photo_indices"]=[0,4,3]
d["field_photo_quickcheck"]["warning"]="Now four more individually licensed source species photos in addition to two original heads, plus four old DIFFERENT-species panels. Root rhizome and true ciliate hair ligule NOT exposed in any new view; micro characters still published source traits not certified on pixels; keep FIELD_READY_PHOTO_GAPS.";
d["field_id_finish_pass"]["stage"]="FIELD_READY_PHOTO_GAPS — four new source-rights-screened habit/blade/sheath-region/spikelet photos now locally archived, root crown and 0.2–0.5 mm true ligule still not exposed";
d["field_id_finish_pass"]["new_living_photos_20261026"]={"new_jpeg_files":4,"new_arrows":0,"total_species_jpeg_files":6,"gallery_panels":10,"rights":"3 CC BY and 1 CC0 photograph source IDs, current photo-level license checks and source original SHA checks, EXIF/GPS removed, original two CC BY/CC0 retained","photo_roles":["grounded live tuft, roots beneath soil","blade/leaf tissue","actual leaf–culm attachment region, ligule hidden","mature whole spikelets, not a dissection"],"remaining":["exposed attached perennial roots and knotty basal rhizome","true 0.2–0.5 mm inner ligule fringe with 1-mm ruler","actual ripe glumes/lemma after dissection only if needed for similar Tridens"],"science_holds":"source identification remains provisional; county/taxonomy/nativity untouched"}
d["curation_status"]["photo_metadata_count"]=len(d["images"])
d["curation_status"]["photo_files_present"]=len(d["images"])
d["curation_status"]["lane3_four_public_roles_20261026"]="Four new exact-source CC photographs physically stored, 6 total Tridens albescens JPEGs, 10 gallery panels with 4 different-species comparisons; true root and ligule photo still missing; status FIELD_READY_PHOTO_GAPS."
d["learner_visual_status"]["image_count"]=len(d["images"])
d["learner_visual_status"]["status"]="FIELD_READY_PHOTO_GAPS"
assert all(json.dumps(d.get(k),sort_keys=True)==v for k,v in old_holds.items())
assert len(d["images"])==6 and len(d["visual_comparison"]["items"])==10
assert all(all(isinstance(i,int) and 0<=i<10 for i in t.get("photo_panel_indices",[])) for t in ts)
for path,blob in files.items():path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(blob)
CARD.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
REPORT.write_text(json.dumps({"result":"FOUR_PUBLIC_PHOTOS_ARCHIVED","species":"Tridens albescens","installed":installed,"species_image_files":6,"species_gallery_panels":10,"arrows_added":0,"practical_status":"FIELD_READY_PHOTO_GAPS","specimen_determination":"Source-determined exact species, provisional without independent voucher","missing":["exposed roots/base/rhizome","true hair-fringed ligule at 1-mm scale","optional ripe dissected floret when field lookalikes cannot be separated"]},indent=2)+"\n")
print(json.dumps({"result":"FOUR_PUBLIC_PHOTOS_ARCHIVED","photo_ids":[r[0] for r in SELECT],"count":len(d["images"])}))
