#!/usr/bin/env python3
"""Archive two CC0 in-situ Eragrostis lugens *provisional ID* photos.
Refuse if original observation photo-level licenses or species labelling change.
No anatomy arrows: observation is Needs ID, not Research Grade.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image, ImageOps
from hashlib import sha256
import io,json

ROOT=Path("content/taxa/Poaceae/Eragrostis/eragrostis-lugens")
CARD=ROOT/"species.json"
REPORT=Path("reports/lane2-lugens-field-in-situ-cc0-20261026.json")
OBSID=92968450
WANTED=[
 (154012199,"dryopteris2-in-situ-rooted-leafy-clump.jpg",
  "LIVE FIELD CONTEXT — actual narrow-leaved tuft growing rooted in soil near a blackened tree; roots below soil NOT visible",
  "In-ground leafy grass clump (species identification provisional)"),
 (154012166,"dryopteris2-field-flowering-head.jpg",
  "LIVE FIELD CONTEXT — fine branching panicle held before a hand in the same observation; attached lower culm not shown",
  "Delicate flowering head in situ, hand for contrast (species ID provisional)")
]
UA={"User-Agent":"Hays-County-Botany noncommercial learner/1.0 (photo-level CC0 attribution audit)"}
CC0="https://creativecommons.org/publicdomain/zero/1.0/"

def main():
    with urlopen(Request(f"https://api.inaturalist.org/v1/observations/{OBSID}",headers=UA),timeout=40) as response:
        data=json.load(response)
    assert len(data.get("results",[]))==1
    observation=data["results"][0]
    assert observation.get("id")==OBSID and observation.get("taxon",{}).get("name")=="Eragrostis lugens"
    assert observation.get("quality_grade")=="needs_id","Identity status changed; manually reevaluate"
    assert observation.get("user",{}).get("login")=="dryopteris2"
    listed={p["id"]:p for p in observation["photos"]}
    for photo_id,*_ in WANTED:
        p=listed[photo_id]
        assert p.get("license_code")=="cc0" and p.get("attribution")=="no rights reserved",(photo_id,p.get("license_code"),p.get("attribution"))
    d=json.loads(CARD.read_text(encoding="utf-8"))
    assert d["id"]=="eragrostis-lugens"
    existing_images={str(x.get("file")) for x in d["images"]}
    new_items=[]
    report=[]
    for photo_id,filename,role,label in WANTED:
        target=ROOT/"images"/filename
        source=f"https://www.inaturalist.org/photos/{photo_id}"
        url=f"https://inaturalist-open-data.s3.amazonaws.com/photos/{photo_id}/original.jpg"
        with urlopen(Request(url,headers=UA),timeout=45) as response:
            assert response.url.startswith("https://inaturalist-open-data.s3.amazonaws.com/")
            raw=response.read(9_000_001)
        assert 20000<len(raw)<9_000_001
        with Image.open(io.BytesIO(raw)) as original:
            assert original.format in {"JPEG","PNG"} and min(original.size)>=650
            actual_source_size=original.size
            im=ImageOps.exif_transpose(original).convert("RGB")
        im.thumbnail((2400,2400))
        buf=io.BytesIO(); im.save(buf,format="JPEG",quality=88,optimize=True)
        cleaned=buf.getvalue()
        with Image.open(io.BytesIO(cleaned)) as test:
            assert test.format=="JPEG" and not test.getexif()
        target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():
            assert sha256(target.read_bytes()).digest()==sha256(cleaned).digest(),"Unexpected existing JPEG differs: hold"
        else:
            target.write_bytes(cleaned)
        rel="images/"+filename
        if rel not in existing_images:
            d["images"].append({
                "file":rel,"role":role,
                "creator":"dryopteris2 (iNaturalist observer)",
                "license":"CC0 1.0","license_url":CC0,
                "source_page":source,
                "source_observation_url":f"https://www.inaturalist.org/observations/{OBSID}",
                "source_photo_id":photo_id,"source_observation_id":OBSID,
                "photo_attribution_original":"no rights reserved",
                "public_reuse":"yes (individual photo metadata: CC0)",
                "species_identification":"PROVISIONAL: source-labelled Eragrostis lugens; observation quality NEEDS ID; NOT independently verified as this species",
                "observed_location_note":"North Carolina, US, 2021-08-29 (not a Hays County voucher)",
                "modifications":"EXIF/GPS stripped, converted to RGB JPEG and resized as needed, no cropping; no anatomy arrows",
                "photo_status":"CC0 SOURCE VERIFIED + ACTUAL IN-SITU PIXELS SCREENED; ID NEEDS CONFIRMATION; not strict species ID"
            })
            existing_images.add(rel)
        panel_url="content/taxa/Poaceae/Eragrostis/eragrostis-lugens/"+rel
        if not any(x.get("image_url")==panel_url for x in d["visual_comparison"]["items"]):
            new_items.append({
                "label":label,
                "scientific_name":"Eragrostis lugens",
                "image_url":panel_url,"image_fit":"contain","image_role":role,
                "caption":("Photographer dryopteris2's photographed grass in the actual ground, with narrow blades and leafy basal crown, from North Carolina. "
                         if photo_id==154012199 else
                         "Fine branching panicle and small spikelets seen against a hand in the same North Carolina observation; attached root/crown connection not shown. ")
                         +"Source observation is labelled Eragrostis lugens but remains iNaturalist Needs ID; species ID is PROVISIONAL, not diagnostic proof. Original photo CC0 1.0, GPS metadata removed.",
                "why_it_matters":("Actual growing-in-ground habit compared with the already installed uprooted specimen; roots below soil are not exposed."
                                if photo_id==154012199 else
                                "Contextual flowering-head field view matched to the same observer/observation as the in-ground tuft."),
                "creator":"dryopteris2 (iNaturalist observer)",
                "license":"CC0 1.0","license_url":CC0,"source_page":source,
                "photo_status":"PUBLIC-SAFE CC0, FIELD HABIT VISUALLY INSPECTED; iNaturalist Needs ID means species-level confidence UNVERIFIED; no arrows or microscopic characters asserted",
                "markers":[]
            })
        report.append({"photo_id":photo_id,"url":source,"bytes":len(cleaned),"size":list(im.size),"source_size":list(actual_source_size),"sha256":sha256(cleaned).hexdigest(),"role":role,"license":"CC0 1.0","identification":"Needs ID, provisional"})
    if len(new_items)==2:
        d["visual_comparison"]["items"][1:1]=new_items
        q=d.get("field_photo_quickcheck",{})
        if "featured_photo_indices" in q:
            old=q["featured_photo_indices"]
            q["featured_photo_indices"]=[0,1,2]+[v+2 if v>=1 else v for v in old if v!=0]
        q["steps"].insert(1,"FIELD CONTEXT: two CC0 North Carolina photographs (soil-rooted leafy tuft + panicle held for detail) came from one source observation. They show where to look on real plants, but iNaturalist still lists it as Needs ID; do not treat their species determination as confirmed or use them for missing ligule proof.")
        q["warning"]+=" Two same-observation NC in-ground/flowerhead context views now in public learner under CC0; iNaturalist quality NEEDS ID so both are strictly provisional species references, no identity or microanatomy arrows. Existing Harry Rose and US herbarium images unchanged."
    d["curation_status"]["photo_metadata_count"]=len(d["images"])
    d["curation_status"]["photo_files_present"]=sum(str(x.get("file","")).startswith("images/") for x in d["images"])
    d["curation_status"]["lane2_extra_field_context_20261026"]="TWO CC0 NORTH CAROLINA CONTEXT PHOTOS; IDENTIFICATION UNCONFIRMED; NEVER COUNT TOWARD STRICT DIAGNOSTIC GATE"
    if isinstance(d.get("learner_visual_status"),dict):
        d["learner_visual_status"]["image_count"]=len(d["images"])
    d["photo_note"]=d.get("photo_note","")+"\n2026-10-26 two CC0 photos 154012199 and 154012166 of same NC observation physically archived: live in-ground tuft and fine panicle. iNat Needs ID so explicitly provisional and not counted toward strict completion. Prior five original photographs, morphology and all arrows retained."
    CARD.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps({
        "species":"Eragrostis lugens","date":"2026-10-26","observation_id":OBSID,
        "observation_quality_grade":observation["quality_grade"],
        "license_verification":"Photos individually CC0 per iNaturalist observation API",
        "taxon_identity":"provisional/source-labelled only; no Research Grade agreement",
        "originals":report,"new_photo_files":2,"new_panels":len(new_items),
        "new_markers":0,"local_photo_count":d["curation_status"]["photo_files_present"],
        "public_site":"not verified until independent Pages success + user visual review",
        "strict_completion":"FIELD_READY_PHOTO_GAPS"
    },indent=2)+"\n",encoding="utf-8")
    print("INSTALLED_CLEAN_CC0_IMAGES",len(report),"TOTAL",d["curation_status"]["photo_files_present"])
if __name__=="__main__": main()
