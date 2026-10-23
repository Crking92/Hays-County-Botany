#!/usr/bin/env python3
"""Batch archive vetted diagnostic Commons photographs into exact-species grass folders."""
import json,urllib.parse,urllib.request,io,pathlib
from PIL import Image
photos=[["Eleusine","eleusine-indica","Eleusine indica ligule1 (6974723960).jpg","Harry Rose","CC BY 2.0","True ligule: short membrane and hair fringe"],["Eleusine","eleusine-indica","Eleusine indica spikelet2 annotated (6974711762).jpg","Harry Rose","CC BY 2.0","Annotated flattened spikelet and glume lemma anatomy"],["Bromus","bromus-japonicus","Bromus japonicus (3860476601).jpg","Matt Lavin","CC BY-SA 2.0","Individual spikelet, rounded lemmas and awns"],["Bromus","bromus-lanceolatus","Bromus lanceolatus dry.jpg","Yves Bas","CC BY 4.0","Dry flowering structure; check Commons rights live"]]
for genus,species,filename,creator,license,role in photos:
    base=pathlib.Path("content/taxa/Poaceae")/genus/species
    p=base/"species.json"
    d=json.loads(p.read_text())
    assert d["id"]==species
    title="File:"+filename
    api="https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url%7Cextmetadata&format=json&titles="+urllib.parse.quote(title)
    req=urllib.request.Request(api,headers={"User-Agent":"Hays-County-Botany/1.0 (educational media archive)"})
    with urllib.request.urlopen(req,timeout=45) as response: page=json.load(response)
    obj=next(iter(page["query"]["pages"].values()))
    assert "imageinfo" in obj,title
    info=obj["imageinfo"][0]
    metadata=info.get("extmetadata",{})
    licensestr=metadata.get("LicenseShortName",{}).get("value","")
    # Fail closed; never silently import an unauthorized image.
    assert licensestr.replace("-"," ").lower().startswith(license.replace("-"," ").lower()) or license.replace(" ","") in licensestr.replace(" ",""),(title,licensestr)
    url=info["url"]
    req=urllib.request.Request(url,headers={"User-Agent":"Hays-County-Botany/1.0"})
    with urllib.request.urlopen(req,timeout=60) as response: binary=response.read()
    assert 12000<len(binary)<18000000
    im=Image.open(io.BytesIO(binary));im.verify()
    im=Image.open(io.BytesIO(binary)).convert("RGB")
    assert im.width>=350 and im.height>=350
    name="commons-"+str(abs(sum((i+1)*ord(c) for i,c in enumerate(filename))))+"-diagnostic.jpg"
    dest=base/"images"/name
    dest.parent.mkdir(parents=True,exist_ok=True)
    im.save(dest,"JPEG",quality=92,optimize=True)
    record={"file":"images/"+name,"role":role,"creator":creator,"license":license,"source_page":"https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_")),"public_reuse":"Attribution required; preserve ShareAlike where specified","photo_status":"PROVISIONAL — USER PHOTO REVIEW PENDING"}
    if not any(x.get("file")==record["file"] or x.get("source_page")==record["source_page"] for x in d.get("images",[])):
        d.setdefault("images",[]).append(record)
    d.setdefault("curation_status",{})["photo_metadata_count"]=len(d["images"])
    d["curation_status"]["photo_files_present"]=sum(str(x.get("file","")).startswith("images/") for x in d["images"])
    d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
    print(species,name,role)
