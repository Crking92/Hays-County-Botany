#!/usr/bin/env python3
"""Promote four individually CC BY-licensed, photo-ID-authenticated F. versuta originals.
Safety: source/rights/bytes strict, no arrows until pixel inspection, preserve science holds.
"""
import io,json,pathlib,urllib.request,urllib.parse,hashlib
from PIL import Image,ImageOps
BASE=pathlib.Path("content/taxa/Poaceae/Festuca/festuca-versuta")
CARD=BASE/"species.json"
EVIDENCE=pathlib.Path("reports/lane3-festuca-versuta-photo-scout-20261026.json")
REPORT=pathlib.Path("reports/lane3-festuca-versuta-four-gallery-20261026.json")
SELECTED=[
 (654445773,358732110,"IDClaire","Living fine-leaved grass tuft at soil surface","EXACT FESCUE — living tuft with leaf bases entering soil","Clump in ground with ascending leaves; actual excavated roots and perennial crown remain hidden."),
 (654445755,358732110,"IDClaire","Actual airy terminal flowering branch held by a hand","EXACT FESCUE — live branching panicle against hand","Intact wispy flowering branch shows spikelets widely spaced toward branch ends; the hand is approximate scale only."),
 (644650733,353286607,"Cleveland Powell","Leaf and sheathing culm with attached flowering spikelets","EXACT FESCUE — leaf and flowering culm together","Real leaf held against fingers beside a branching flowering culm; photograph does NOT expose or measure inner 0.5–1 mm ligule."),
 (367035946,207498490,"Jared Shorma","Single mature multi-flowered whole spikelet with hand for scale","EXACT FESCUE — mature spikelet with visible overlapping florets","Whole mature laterally compressed spikelet photographed against a fingertip; its individual glumes, lemma veins and any minute mucro are NOT securely dissected or measured."),
]
UA="HaysCountyBotany/1.0 (public noncommercial botanical source-cited CC BY image archival)"
def get(url,limit=18_000_000):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"image/jpeg,application/json"})
    with urllib.request.urlopen(req,timeout=45) as f:
        payload=f.read(limit+1)
    if len(payload)>limit:raise ValueError("Large remote response")
    return payload
def api(url):return json.loads(get(url))
d=json.loads(CARD.read_text())
assert d["id"]=="festuca-versuta" and d["scientific_name"]=="Festuca versuta"
audit=json.loads(EVIDENCE.read_text())
assert audit["inat_taxon_id"]==162965 and not audit["failures"]
obs_by_id={}
for _,oid,_,_,_,_ in SELECTED:
    if oid in obs_by_id:continue
    o=api("https://api.inaturalist.org/v1/observations/"+str(oid))
    candidates=o.get("results",[])
    assert len(candidates)==1 and candidates[0]["id"]==oid,oid
    observation=candidates[0]
    assert observation["taxon"]["id"]==162965 and observation["taxon"]["name"]=="Festuca versuta"
    assert observation.get("quality_grade")=="research"
    obs_by_id[oid]=observation
newimages=[];newpanels=[];blobs={};rec=[]
for pid,oid,creator,role,label,caption in SELECTED:
    old=next((x for x in d["images"] if x.get("source_photo_id")==pid or str(pid) in str(x.get("file",""))),None)
    if old:raise ValueError("Previously installed image ID; refuse double install "+str(pid))
    candidate=next(x for x in audit["candidate_photos"] if x["photo_id"]==pid and x["observation_id"]==oid)
    assert candidate["license_code"]=="cc-by" and creator.lower() in (candidate.get("attribution") or "").lower()
    photo=next(x for x in obs_by_id[oid]["photos"] if x["id"]==pid)
    assert photo.get("license_code")=="cc-by" and creator.lower() in (photo.get("attribution") or "").lower()
    source_url="https://inaturalist-open-data.s3.amazonaws.com/photos/"+str(pid)+"/original.jpg"
    raw=get(source_url)
    assert hashlib.sha256(raw).hexdigest()==candidate["source_sha256"],"Original source bytes changed since visual scouting"
    with Image.open(io.BytesIO(raw)) as im:
        assert im.format=="JPEG"
        im.verify()
    with Image.open(io.BytesIO(raw)) as im:
        im=ImageOps.exif_transpose(im).convert("RGB")
        assert min(im.size)>=800
        original=[im.width,im.height]
        im.thumbnail((1800,1800),Image.Resampling.LANCZOS)
        buf=io.BytesIO();im.save(buf,"JPEG",quality=90,optimize=True)
        blob=buf.getvalue()
    with Image.open(io.BytesIO(blob)) as im:
        assert im.format=="JPEG" and not im.getexif().get(34853)
        im.verify()
    rel="images/festuca-versuta-inat-"+str(pid)+"-ccby.jpg"
    path=BASE/rel
    if path.exists():raise ValueError("Existing image path; do not overwrite")
    blobs[path]=blob
    sha=hashlib.sha256(blob).hexdigest()
    newimages.append({
      "file":rel,"role":role,"creator":creator,"attribution":photo.get("attribution"),
      "license":"CC BY","license_code":"cc-by", "license_version_note":"Current exact iNaturalist photo license code cc-by verified; specific version not separately certified",
      "license_url":"https://creativecommons.org/licenses/by/",
      "source_page":"https://www.inaturalist.org/photos/"+str(pid),
      "observation_source":"https://www.inaturalist.org/observations/"+str(oid),
      "source_photo_id":pid,"source_observation_id":oid,
      "photo_taxon_identification":"Research Grade source-determined Festuca versuta; no independently checked botanical voucher",
      "original_image_url":source_url,
      "original_sha256":hashlib.sha256(raw).hexdigest(),
      "local_sha256":sha,
      "original_dimensions":original,
      "source_rights_verified":"2026-10-26 current exact iNaturalist observation photo license_code cc-by; image-specific creator and photo ID",
      "modifications":"Resized to fit within 1800px and re-encoded as JPEG, EXIF/GPS removed. No overlaid pixels or crops.",
      "photo_status":"ARCHIVED_FROM_LICENSED_ORIGINAL; broad visible structures screened, microstructures and arrow locations require source-pixel inspection"
    })
    newpanels.append({
      "label":label,"scientific_name":"Festuca versuta",
      "image_url":str(BASE/rel),"image_fit":"contain","image_role":role,
      "caption":caption,"why_it_matters":"True source-identified species photograph strengthens the living crown/flowering/spikelet field lesson without inventing a ligule or glume identity.",
      "creator":creator,"license":"CC BY","license_url":"https://creativecommons.org/licenses/by/",
      "source_page":"https://www.inaturalist.org/photos/"+str(pid),
      "observation_source":"https://www.inaturalist.org/observations/"+str(oid),
      "photo_status":"Exact source CC BY photograph; no hair/ligule/vein or species voucher independently measured; visible-gross-feature arrows not yet reviewed",
      "markers":[]
    })
    rec.append({"photo_id":pid,"observation":oid,"creator":creator,"source_file":source_url,"file":str(path),"sha256":sha,"original_sha256":candidate["source_sha256"],"license":"CC BY","source_taxon":"Festuca versuta"})
oldpanels=d["visual_comparison"]["items"]
assert len(oldpanels)==3 and len(d["images"])==3
assert len(newimages)==len(newpanels)==4
d["images"]+=newimages
d["visual_comparison"]["items"]=newpanels+oldpanels
d["visual_comparison"]["title"]="Texas fescue — living tuft, loose flowering head and actual spikelets"
d["visual_comparison"]["subtitle"]="Four NEW source-identified live source-CC-BY photographs lead the lesson (habit, panicle, leaf/culm and mature spikelet), followed by existing BRIT CC BY historic voucher, correctly labeled 1906 botanical illustration, and credited NC loose-fragment study. Actual true ligule and vouchered dissected glumes remain absent."
d["visual_comparison"]["overlay_note"]="2026-10-26: four exact research-grade iNaturalist source photos CC BY physically archived, original source SHA matched to reviewed contact sheet, JPEG re-encoded without EXIF/GPS, CC author/observation/individual photo verified immediately before installation. NO anatomy arrows yet on these new photos pending final full-pixel review. Three prior old panels and all source science holds preserved."
tiles=d["field_id_short_tiles"]
assert len(tiles)==6
tiles[0]["photo_panel_indices"]=[0,1,2,4]
tiles[0]["details"]="Actual living source-identified tuft photo (panel 1), flowering panicle (panel 2), leaf with flowering culm (panel 3), and preserved BRIT root+panicle voucher (panel 5). Look for perennial rooted bunch, open drooping flowering head and attached spikelets. The living in-ground photograph hides the actual fibrous root crown; do not certify exposed roots, and do not treat the historical specimen as fresh Hays material."
tiles[0]["status"]="REAL LIVING TUFT AND FLOWERING ARCHITECTURE NOW PHOTOGRAPHED; EXPOSED ROOT CROWN STILL MISSING"
tiles[1]["photo_panel_indices"]=[3,2]
tiles[1]["details"]="The new true species photograph (panel 4) shows a mature entire multi-flowered spikelet held against a fingertip; panel 3 shows spikelets attached to a flowering culm. Published 6–9 mm length and 2–4 florets remain taxon-level literature, NOT measurements or a dissected glume count established by photos."
tiles[1]["status"]="SOURCE PHOTOGRAPHS SHOW MATURE WHOLE SPIKELET; CALIBRATED FLORET COUNT PENDING"
tiles[2]["photo_panel_indices"]=[3,4]
tiles[2]["status"]="REPRODUCTIVE PHOTO HELPFUL; TRUE SEPARATED LOWER/UPPER GLUMES STILL MISSING"
tiles[3]["photo_panel_indices"]=[3,5]
tiles[3]["status"]="WHOLE SPIKELET PHOTO HELPFUL; LEMMA NERVES AND MUCRO NOT MEASURED"
tiles[4]["photo_panel_indices"]=[]
tiles[5]["photo_panel_indices"]=[0,1,3,5]
d["field_id_finish_pass"]["stage"]="FIELD_READY_PHOTO_GAPS — 4 new true licensed living and spikelet originals plus existing 3 archival records; actual exposed crown, measured 0.5–1 mm inner ligule and verified glume/lemma dissection remain missing"
d["field_id_finish_pass"]["new_festuca_versuta_photo_pass_20261026"]={
 "physically_archived_new":4,"local_metadata_total":7,"public_gallery_panels":7,
 "review_basis":"research-grade species-labelled iNaturalist exact photo IDs, individual current cc-by licensing and source original SHA; independent voucher ID pending",
 "actual_roles":["living tuft in ground (roots hidden)","live terminal branching inflorescence","blade and culm with intact flowering stems (inner ligule hidden)","mature whole spikelet (no mm ruler)"],
 "remaining":["Expose actual rooted fibrous crown on same verified specimen","True free eciliate membrane 0.5–1 mm at opened sheath beside a 1-mm ruler","Dissect mature whole spikelet with glumes, 2–4 florets and lemma tip resolved at 10–20×"],
 "annotations":"All four new panels initially arrowless pending full-resolution pixel review; older 3 panels unchanged.",
 "rights":"Four new CC BY, original CC BY-NC blake hendon remains credited for genuine noncommercial site, BRIT and historic illustration untouched",
 "science_holds":"Preserve existing Hays county/taxonomy pending flags and synonym caveats; no cultivar or nonlocal range changes"
}
d["curation_status"]["photo_metadata_count"]=len(d["images"])
d["curation_status"]["photo_files_present"]=len(d["images"])
d["curation_status"]["lane3_festuca_four_ccby_20261026"]="Four new real species source photos; copyright metadata verified; 7 total local records; leaf-collar/root micro gap remains; old sources, taxonomy and county holds unchanged."
d["learner_visual_status"]["image_count"]=len(d["images"])
d["learner_visual_status"]["status"]="FIELD_READY_PHOTO_GAPS"
assert all(all(isinstance(idx,int) and 0<=idx<7 for idx in x.get("photo_panel_indices",[])) for x in tiles)
# Stage image files after successful validation of all four source originals.
for path,blob in blobs.items():
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(blob)
CARD.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
REPORT.write_text(json.dumps({"species":"Festuca versuta","result":"FOUR_ORIGINAL_CC_BY_JPEGS_INSTALLED","installed":rec,"new_gallery":4,"species_local_images":len(d["images"]),"species_gallery_panels":len(d["visual_comparison"]["items"]),"new_arrows":0,"retain_status":"FIELD_READY_PHOTO_GAPS","photo_binaries_verification":"All originals SHA-256 matched source audit; each new archived file validated decoded JPEG; EXIF/GPS removed","unresolved":["actual exposed rooted crown","mm-calibrated true inner ligule","one mature dissected spikelet with independently identifiable glumes and lemmas"]},indent=2)+"\n",encoding="utf-8")
print(json.dumps({"result":"FOUR_ORIGINAL_CC_BY_JPEGS_INSTALLED","source_ids":[i[0] for i in SELECTED],"local_image_total":len(d["images"]),"gallery_panels":len(d["visual_comparison"]["items"])}))
