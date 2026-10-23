#!/usr/bin/env python3
"""Archive one CC BY exact-taxon slimspike windmillgrass photograph."""
import io, json, pathlib, urllib.request, urllib.error, time
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Chloris/chloris-andropogonoides")
p=base/"species.json"; d=json.loads(p.read_text())
assert d["id"]=="chloris-andropogonoides"
photo_id="348830581"
name="cleveland-powell-inat-348830581.jpg"
dest=base/"images"/name
if not dest.exists():
    source=f"https://static.inaturalist.org/photos/{photo_id}/large.jpg"
    req=urllib.request.Request(source,headers={"User-Agent":"Hays-County-Botany/1.0 (educational botanical archive)"})
    payload=None
    urls=[f"https://static.inaturalist.org/photos/{photo_id}/large.jpg",f"https://inaturalist-open-data.s3.amazonaws.com/photos/{photo_id}/large.jpg"]
    for attempt in range(4):
        for url in urls:
            try:
                req=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 (educational photo archive)"})
                with urllib.request.urlopen(req,timeout=60) as resp:
                    payload=resp.read()
                break
            except (urllib.error.HTTPError, urllib.error.URLError) as err:
                print("SOURCE_UNAVAILABLE",url,str(err),flush=True)
        if payload:break
        time.sleep(20*(attempt+1))
    assert payload, "Neither attributed photo endpoint was reachable"
    assert 15000<len(payload)<12000000
    im=Image.open(io.BytesIO(payload));im.verify()
    im=Image.open(io.BytesIO(payload)).convert("RGB")
    assert im.width>=500 and im.height>=500
    dest.parent.mkdir(parents=True,exist_ok=True)
    im.save(dest,"JPEG",quality=91,optimize=True) # do not transfer original GPS/EXIF
assert dest.stat().st_size>15000
record={"file":"images/"+name,"role":"Additional exact-source flowering/species-recognition reference; visual details require user review","creator":"Cleveland Powell","license":"CC BY","source_page":f"https://www.inaturalist.org/photos/{photo_id}","source_secondary":"https://ournativeplants.com/genus/chloris/","public_reuse":"CC BY; retain creator and source","photo_status":"PROVISIONAL — USER PHOTO REVIEW PENDING; do not infer lemma or ligule anatomy"}
if not any(i.get("file")==record["file"] for i in d["images"]):
    d["images"].append(record)
d.setdefault("curation_status",{})["photo_metadata_count"]=len(d["images"])
d["curation_status"]["photo_files_present"]=sum(1 for i in d["images"] if str(i.get("file","")).startswith("images/"))
d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
d["photo_note"]=str(d.get("photo_note",""))+" Cleveland Powell CC BY iNaturalist image archived for provisional review; this does not resolve microscopic lemma/ligule gaps."
p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
print("Chloris andropogonoides physically archived and species card updated",len(d["images"]))
