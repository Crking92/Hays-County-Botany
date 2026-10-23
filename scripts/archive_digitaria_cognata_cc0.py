#!/usr/bin/env python3
"""One-taxon's exact-source CC0 archive, idempotent; run in GitHub Actions."""
import io, json, pathlib, urllib.request, hashlib
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Digitaria/digitaria-cognata")
p=base/"species.json"
d=json.loads(p.read_text())
assert d["id"] == "digitaria-cognata"
photos=[
("99737795","4/49","shaun-pogacnik-99737795.jpg","Close flowering panicle; reddish fine branching axes and individual spikelets"),
("99737817","1/13","shaun-pogacnik-99737817.jpg","Rooted clump with thin spreading reddish mature panicles")]
for photo_id,folder,name,role in photos:
    url=f"https://upload.wikimedia.org/wikipedia/commons/{folder}/Digitaria_cognata_iNat-{photo_id}.jpg"
    dest=base/"images"/name
    if not dest.exists():
        req=urllib.request.Request(url,headers={"User-Agent":"HaysBotanyVisualLearner/1.0 (educational photo archive)"})
        with urllib.request.urlopen(req,timeout=45) as response:
            b=response.read()
        assert len(b)>15000 and len(b)<12000000, "unexpected image size"
        im=Image.open(io.BytesIO(b)); im.verify()
        im=Image.open(io.BytesIO(b)).convert("RGB")
        assert im.width>=800 and im.height>=600
        dest.parent.mkdir(parents=True,exist_ok=True)
        im.save(dest,format="JPEG",quality=91,optimize=True) # no EXIF/GPS transferred
    assert dest.stat().st_size>15000
    record={"file":"images/"+name,"role":role,"creator":"Shaun Pogacnik","license":"CC0 1.0","license_url":"https://creativecommons.org/publicdomain/zero/1.0/","source_page":f"https://commons.wikimedia.org/wiki/File:Digitaria_cognata_iNat-{photo_id}.jpg","original_source_page":f"https://www.inaturalist.org/photos/{photo_id}","public_reuse":"Public domain CC0; credited for educational provenance","photo_status":"PROVISIONAL — USER PHOTO REVIEW PENDING; exact taxon tagged at source, diagnostic anatomy unverified"}
    if not any(x.get("file")==record["file"] for x in d["images"]):d["images"].append(record)
d.setdefault("curation_status",{})["photo_metadata_count"]=len(d["images"])
d["curation_status"]["photo_files_present"]=sum(1 for x in d["images"] if str(x.get("file","")).startswith("images/"))
d["photo_note"]=str(d.get("photo_note",""))+" Two CC0 Shaun Pogacnik originals archived from Wikimedia Commons: habit and flowering panicle; field-ready with microscopic ligule/spikelet gaps. Photos provisional pending public learner pixel review."
d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
print("archived",len(d["images"]),"exact species photos")
