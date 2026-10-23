#!/usr/bin/env python3
"""Archive independently license-checked Commons pine muhly originals; never fake gallery completion."""
import json, io, hashlib, pathlib, urllib.request, urllib.parse, re, html
from PIL import Image, ImageOps
base=pathlib.Path("content/taxa/Poaceae/Muhlenbergia/muhlenbergia-dubia")
record=base/"species.json"
d=json.loads(record.read_text())
assert d["id"]=="muhlenbergia-dubia"
sources=[
("File:Muhlenbergia dubia - Flickr - aspidoscelis.jpg","pine-muhly-patrick-alexander-cc0.jpg","Wild plant recognition; anatomy not diagnostic"),
("File:Muhlenbergia dubia 001.jpg","pine-muhly-stickpen-public-domain.jpg","Cultivated clump recognition; anatomy not diagnostic")
]
def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotanyPublicPhotoArchive/1.0 (educational attribution checking)"})
    with urllib.request.urlopen(req,timeout=55) as r:
        raw=r.read(18000001)
    assert len(raw)<18000000
    return raw
report={"added":[],"held":[]}
for title,filename,role in sources:
    try:
        query=urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata","titles":title})
        info=next(iter(json.loads(get("https://commons.wikimedia.org/w/api.php?"+query))["query"]["pages"].values()))["imageinfo"][0]
        md=info["extmetadata"]
        license=html.unescape(re.sub("<[^>]+>","",md.get("LicenseShortName",{}).get("value",""))).strip()
        simplified=license.upper().replace(" ","").replace("-","")
        assert simplified in ("CC0","CC01.0","PUBLICDOMAIN","PDSELF","PDM","NORESTRICTIONS"),"Not verified CC0/public domain: "+license
        source="https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_"))
        if any(x.get("source_page")==source for x in d.get("images",[])):
            report["held"].append({"source":source,"reason":"Already installed"});continue
        raw=get(info["url"])
        with Image.open(io.BytesIO(raw)) as im: im.verify()
        with Image.open(io.BytesIO(raw)) as im:
            im=ImageOps.exif_transpose(im).convert("RGB")
            assert min(im.size)>=700
            im.thumbnail((1800,1800))
            out=io.BytesIO();im.save(out,"JPEG",quality=88,optimize=True)
            payload=out.getvalue()
        dest=base/"images"/filename;dest.parent.mkdir(exist_ok=True)
        dest.write_bytes(payload)
        with Image.open(dest) as im:
            im.verify()
        creator="Patrick Alexander" if "aspidoscelis" in title else "Stickpen"
        d.setdefault("images",[]).append({"file":"images/"+filename,"role":role,"creator":creator,"license":license,"source_page":source,"source_determination":"Muhlenbergia dubia","publication_scope":"PUBLIC-WEB-CLEARED","public_reuse":"Source declares CC0/public domain; source and creator retained","sha256":hashlib.sha256(payload).hexdigest(),"photo_status":"LOCAL_FILE_VERIFIED; NOT diagnostic ligule/spikelet"})
        report["added"].append({"file":dest.as_posix(),"source":source,"license":license})
    except Exception as exc:
        report["held"].append({"title":title,"reason":str(exc)})
if report["added"]:
    d["learner_visual_status"]={"status":"FIELD_READY_PHOTO_GAPS","image_count":len(d["images"]),"note":"Habit photographs locally archived; ligule/glume/spikelet micros and anatomical arrows still required."}
    d.setdefault("curation_status",{})["photo_files_present"]=len(d["images"])
    record.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
path=pathlib.Path("reports/pine-muhly-photo-archive-20261023.json")
path.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
