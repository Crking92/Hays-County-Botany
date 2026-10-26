#!/usr/bin/env python3
"""Add an individually licensed source-verified E. lugens blade/sheath bend macro.
Do not diagnose the true 0.2–0.3-mm ligule from white tissue at the fold.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from hashlib import sha256
from PIL import Image,ImageOps
import io,json
ROOT=Path("content/taxa/Poaceae/Eragrostis/eragrostis-lugens")
CARD=ROOT/"species.json"
REPORT=Path("reports/lane2-lugens-blade-sheath-bend-20261026.json")
PID=229855521
OID=134813393
FNAME="images/diego-lugens-blade-sheath-bend-229855521.jpg"
UA={"User-Agent":"Hays-Botany-Learner/1.0 (source verified noncommercial photo education)"}
def pull(url,maxbytes=9500000):
    with urlopen(Request(url,headers=UA),timeout=45) as f:
        data=f.read(maxbytes+1)
        assert len(data)<=maxbytes,"Unexpected huge image"
        return data
def main():
    j=json.loads(CARD.read_text(encoding="utf-8"))
    assert j["id"]=="eragrostis-lugens"
    meta=json.loads(pull(f"https://api.inaturalist.org/v1/observations/{OID}",1000000))["results"][0]
    assert meta["taxon"]["name"]=="Eragrostis lugens" and meta["quality_grade"]=="research"
    media=next(p for p in meta["photos"] if p.get("id")==PID)
    assert media.get("license_code")=="cc-by-nc"
    source=media["url"].replace("/square.","/original.").replace("/medium.","/original.").replace("/large.","/original.")
    data=pull(source)
    with Image.open(io.BytesIO(data)) as img:
        assert img.format=="JPEG"
        picture=ImageOps.exif_transpose(img).convert("RGB")
    picture.thumbnail((2200,2200))
    out=io.BytesIO()
    picture.save(out,format="JPEG",quality=88,optimize=True)
    cleaned=out.getvalue()
    with Image.open(io.BytesIO(cleaned)) as check:
        assert check.format=="JPEG" and not check.getexif(),"EXIF retained"
    dest=ROOT/FNAME
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():assert dest.read_bytes()==cleaned,"Existing photo differs"
    else:dest.write_bytes(cleaned)
    link=f"https://www.inaturalist.org/photos/{PID}"
    photo={
      "file":FNAME,
      "role":"True same-species Research Grade photograph of green narrow blade sharply bending back near its basal sheathing region and pale outer collar-like tissue; does NOT prove a distinct inner 0.2–0.3 mm ligule",
      "creator":media.get("attribution") or "Diego, iNaturalist photographer",
      "license":"CC BY-NC 4.0, noncommercial site only",
      "license_url":"https://creativecommons.org/licenses/by-nc/4.0/",
      "source_page":link,
      "source_observation_url":f"https://www.inaturalist.org/observations/{OID}",
      "license_evidence":"Verified exact iNaturalist PHOTO license_code cc-by-nc on Research Grade observation",
      "public_reuse":"Genuinely noncommercial educational website only; preserve full creator/source/NC terms",
      "modifications":"Actual JPEG RGB reencoded without EXIF/GPS, no cropping, separate browser SVG annotations",
      "photo_status":"Visually inspected high-resolution photograph 2026-10-26. Pale tissue at blade bend may be collar/crease; no assertion that it is the true inner ligule without calibration."
    }
    if not any(x.get("file")==FNAME for x in j["images"]):j["images"].append(photo)
    image_url="content/taxa/Poaceae/Eragrostis/eragrostis-lugens/"+FNAME
    new_item={
      "label":"BLADE–SHEATH REGION: leaf bent back at junction (tiny true ligule unverified)",
      "scientific_name":"Eragrostis lugens","image_url":image_url,"image_fit":"contain",
      "image_role":photo["role"],
      "caption":"Diego's Research Grade source-identified mourning lovegrass photo from Querétaro, Mexico. The narrow leaf is bent toward the left near a green upright sheathing base, exposing a pale folded region. That pale region cannot reliably be labelled or measured as the tiny INSIDE true ligule (0.2–0.3 mm). The arrow labels are restricted to blade and green sheathing base. This is a collar-region teaching reference only, not a proven ligule or local Hays specimen.",
      "why_it_matters":"The closest existing source photo to an opened blade–sheath connection. Helps crew see which joint to inspect with 10–20× magnification and a millimeter scale.",
      "creator":photo["creator"],"license":photo["license"],"license_url":photo["license_url"],
      "source_page":link,
      "markers":[{"label":"Narrow blade bent away from sheathing base","label_x":4,"label_y":35,"target_x":56,"target_y":44},{"label":"Upright green outer sheath; inner ligule unresolved","label_x":6,"label_y":82,"target_x":74,"target_y":72}],
      "modifications":photo["modifications"],
      "photo_status":"Original iNaturalist photo/license verified and pixels visually inspected 2026-10-26. Cannot designate or measure the pale fold as true ligule."
    }
    if not any(x.get("image_url")==image_url for x in j["visual_comparison"]["items"]):
        ix=next((i for i,x in enumerate(j["visual_comparison"]["items"]) if x.get("scientific_name")!="Eragrostis lugens"),len(j["visual_comparison"]["items"]))
        j["visual_comparison"]["items"].insert(ix,new_item)
    qc=j["field_photo_quickcheck"]
    qc["steps"].insert(2,"Look at Diego's exact-species leaf/sheath closeup. It shows the narrow blade flexed near a pale collar-like area, but the photo is not proof of the actual tiny 0.2–0.3-mm inner ligule. Obtain a 10–20× peeled-open blade photo with a 1-mm ruler; keep the longer 2–5-mm sheath-throat hairs separate.")
    qc["warning"]+=" October 26: one independently CC BY-NC Research Grade source photo archived at high resolution showing a blade/sheathed culm bend, with two visible-only arrows. Pale tissue at the bend is NOT certified as true ligule, so keep field-photo ligule hold."
    j["field_id_finish_pass"]["photo_evidence_limits"]+=" Additional source-vetted Research Grade blade–sheath bend photograph installed October 26. Distinct inner true ligule remains unproved and unmeasured; same-site Texas specimen still needed."
    j["curation_status"]["photo_metadata_count"]=len(j["images"])
    j["curation_status"]["photo_files_present"]=sum(str(z.get("file","")).startswith("images/") for z in j["images"])
    j["curation_status"]["lane2_collar_candidate_20261026"]="Externally visible folded blade/sheath region documented with 2 arrows; true inner ligule NOT demonstrated"
    j["photo_note"]=j.get("photo_note","")+"\n2026-10-26 Lane 2: archived Diego CC BY-NC blade/sheath photograph, exact photo rights/source checked, 2 gross arrows. Never infer tiny ligule from pale crease; full macro with mm ruler remains."
    if isinstance(j.get("learner_visual_status"),dict):j["learner_visual_status"]["image_count"]=len(j["images"])
    CARD.write_text(json.dumps(j,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps({"species":"Eragrostis lugens","photo_id":PID,"observation_id":OID,"photo_source":link,"creator":photo["creator"],"license":"CC BY-NC","bytes":len(cleaned),"dimensions":list(picture.size),"sha256":sha256(cleaned).hexdigest(),"new_photo_count":1,"new_arrow_count":2,"existing_photo_count":len(j["images"]),"ligule_confirmed":False,"stage":"FIELD_READY_PHOTO_GAPS"},indent=2)+"\n",encoding="utf-8")
    print("SUCCESS_LUGENS",len(j["images"]),len(cleaned))
if __name__=="__main__":main()
