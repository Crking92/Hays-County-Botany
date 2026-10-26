#!/usr/bin/env python3
"""Real Eragrostis trichodes external sheath & blade base photography. Never mislabel ligule."""
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image,ImageOps
from hashlib import sha256
import json,io
ROOT=Path("content/taxa/Poaceae/Eragrostis/eragrostis-trichodes")
CARD=ROOT/"species.json"
REPORT=Path("reports/lane2-trichodes-sheath-outer-collar-20261026.json")
UA={"User-Agent":"HaysBotanyLearner/1.0 (public noncommercial photo-license verification)"}
PAIRS=[
 {"photo":746040999,"obs":406096399,"file":"sam-kieschnick-sheath-and-blades-746040999.jpg",
  "label":"TRUE PHOTO: sheaths and attached blades held apart, not an opened ligule",
  "role":"Leaf blade bases and long sheath portions of a living E. trichodes plant physically held apart by Sam Kieschnick; short inner true ligule NOT exposed",
  "caption":"Sam Kieschnick's source-verified, CC BY photographed sand lovegrass from the Salado Creek Greenway in San Antonio. The narrow green blade and smoothish sheath-wrapped culm can be traced toward the fingers, but the hand partially obscures the blade/sheathed-culm transition. No 0.4-mm hair-fringed inner ligule or 4–5-mm throat hair tuft is conclusively resolved. This is a practical outside-sheath orientation view, not microscopic proof.",
  "markers":[{"label":"Long upright leaf blade / culm region","label_x":69,"label_y":11,"target_x":57,"target_y":36},{"label":"External green sheath near hand (NOT ligule)","label_x":5,"label_y":88,"target_x":46,"target_y":74}]},
 {"photo":557286898,"obs":308867293,"file":"ostrowski-blade-base-hand-557286898.jpg",
  "label":"BLADE BASE: clustered sheaths and emerging tiller held apart (no true ligule)",
  "role":"Close-hand study of green live blade bases and sheaths in the tiller cluster of source-identified E. trichodes; no isolated measured inner ligule",
  "caption":"Michael R. Ostrowski's individually CC BY-NC licensed grass photograph. Fingers part multiple green blades near their lower sheathing bases; use it to locate where the TRUE short ligule would be revealed on the inside of a pulled-back blade. No confidently measured ligule fringe is visible, and this is not a local Texas voucher.",
  "markers":[{"label":"Leaf blades emerging upward from sheath area","label_x":67,"label_y":13,"target_x":52,"target_y":40},{"label":"Sheathing blade bases by fingers; inner ligule unseen","label_x":4,"label_y":87,"target_x":46,"target_y":73}]}
]
def grab(url,maximum=10000000):
    with urlopen(Request(url,headers=UA),timeout=45) as resp:
        raw=resp.read(maximum+1)
        assert len(raw)<=maximum,"Too large"
        return raw
def main():
    d=json.loads(CARD.read_text(encoding="utf-8"));assert d["id"]=="eragrostis-trichodes"
    installed=[]
    for x in PAIRS:
        response=json.loads(grab(f"https://api.inaturalist.org/v1/observations/{x['obs']}",1600000))["results"][0]
        assert response["taxon"]["name"]=="Eragrostis trichodes" and response["quality_grade"]=="research"
        p=next(y for y in response["photos"] if y["id"]==x["photo"])
        lic=p.get("license_code")
        assert lic in ("cc-by","cc-by-nc"),lic
        url=p["url"].replace("/square.","/original.").replace("/medium.","/original.").replace("/large.","/original.")
        binary=grab(url)
        with Image.open(io.BytesIO(binary)) as source:
            assert source.format=="JPEG"
            photo=ImageOps.exif_transpose(source).convert("RGB")
        photo.thumbnail((2200,2200))
        stream=io.BytesIO();photo.save(stream,format="JPEG",quality=88,optimize=True)
        clean=stream.getvalue()
        with Image.open(io.BytesIO(clean)) as check:
            assert check.format=="JPEG" and not check.getexif()
        fname="images/"+x["file"]
        local=ROOT/fname
        local.parent.mkdir(parents=True,exist_ok=True)
        if local.exists():
            assert local.read_bytes()==clean
        else:local.write_bytes(clean)
        link=f"https://www.inaturalist.org/photos/{x['photo']}"
        name="CC BY-NC 4.0 (noncommercial only)" if lic=="cc-by-nc" else "CC BY 4.0"
        url_license=f"https://creativecommons.org/licenses/{lic[3:]}/4.0/"
        media={
          "file":fname,"role":x["role"],"creator":p.get("attribution") or "iNaturalist observer",
          "license":name,"license_url":url_license,"source_page":link,
          "source_observation_url":f"https://www.inaturalist.org/observations/{x['obs']}",
          "photo_specific_evidence":"iNaturalist Research Grade observation + exact PHOTO license code "+lic,
          "public_reuse":"Approved only for strictly noncommercial, credited site with all NC terms" if "nc" in lic else "Approved attributed CC BY on public site",
          "modifications":"EXIF/GPS stripped, JPEG RGB re-encoded, no crop; separate browser SVG arrow overlay",
          "photo_status":"Actual 2026-10-26 visually inspected high-resolution pixels show sheathing blade bases, not measured true ligule."
        }
        if not any(z.get("file")==fname for z in d["images"]):d["images"].append(media)
        media_url="content/taxa/Poaceae/Eragrostis/eragrostis-trichodes/"+fname
        item={
           "label":x["label"],"scientific_name":"Eragrostis trichodes","image_url":media_url,"image_fit":"contain","image_role":x["role"],"caption":x["caption"],
           "why_it_matters":"Trains recognition of outer sheath and lower leaf blade parts while preserving the need for a separate opened, scaled true ligule macro.",
           "creator":media["creator"],"license":name,"license_url":url_license,"source_page":link,
           "markers":x["markers"],"modifications":media["modifications"],
           "photo_status":"Species/photo/rights verified, arrows restricted to gross visible blade and sheath structures; true short ligule not demonstrated."
        }
        if not any(z.get("image_url")==media_url for z in d["visual_comparison"]["items"]):
            ix=next((i for i,z in enumerate(d["visual_comparison"]["items"]) if z.get("scientific_name")!="Eragrostis trichodes"),len(d["visual_comparison"]["items"]))
            d["visual_comparison"]["items"].insert(ix,item)
        installed.append({"photo":x["photo"],"license":lic,"creator":media["creator"],"sha256":sha256(clean).hexdigest(),"bytes":len(clean),"dimensions":list(photo.size),"markers":len(x["markers"])})
    d["curation_status"]["photo_metadata_count"]=len(d["images"])
    d["curation_status"]["photo_files_present"]=sum(z.get("file","").startswith("images/") for z in d["images"])
    d["curation_status"]["lane2_sheath_views_20261026"]="TWO individually licensed sheath/blade base photograph panels installed with four gross arrows; actual inner ligule unresolved"
    d["field_photo_quickcheck"]["steps"].insert(1,"TWO real source-vouchered blade-sheath teaching panels now show the outer green sheathing culms. Neither exposes the INTERNAL 0.4–0.5 mm ciliate ligule, and the 4–5 mm sheath-THROAT hairs should not be confused with its short fringe. Peel one blade away to photograph the true ligule with a scale.")
    d["field_photo_quickcheck"]["warning"]+=" October 26: added two Research Grade, individually credited blade/sheath photos with four gross arrows. The actual inner 0.4-mm ligule and separate long 4–5-mm sheath-throat hair macro remain missing; retain FIELD_READY_PHOTO_GAPS."
    d["field_id_finish_pass"]["photo_gaps"]=[
     "A peeled-open actual INSIDE 0.4-mm hair-fringed ligule with millimeter ruler and clearly separate outer 4–5-mm throat/collar hairs",
     "Real exposed connected fibrous roots, perennial bunch crown and emerging tillers from an authenticated plant",
     "A same-plant 10–20× mature seedhead/spikelet photo for strict look-alike separation"
    ]
    d["field_id_finish_pass"]["lane2_real_sheath_views_20261026"]={"new_local_photos":2,"new_gross_arrows":4,"true_ligule_is_documented":False,"remaining":"FIELD_READY_PHOTO_GAPS"}
    d["photo_note"]=d.get("photo_note","")+"\n2026-10-26 Lane 2: added two CC BY/CC BY-NC public noncommercial source-verified live blade/sheath panels with true-ligule hold; retained all older photo and anatomy arrows."
    if isinstance(d.get("learner_visual_status"),dict):d["learner_visual_status"]["image_count"]=len(d["images"])
    CARD.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps({"species":"Eragrostis trichodes","photos":installed,"new_images":2,"new_arrows":4,"true_ligule":"MISSING","other_holds":["roots attached to crown","measured true ligule and long separate throat hairs"],"status":"FIELD_READY_PHOTO_GAPS"},indent=2)+"\n",encoding="utf-8")
    print("SUCCESS",len(installed),"local",d["curation_status"]["photo_files_present"])
if __name__=="__main__":main()
