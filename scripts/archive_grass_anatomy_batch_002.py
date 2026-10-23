#!/usr/bin/env python3
"""Install licensed exact-taxon photo candidates, fail closed, track individual failures."""
import io,json,pathlib,urllib.request,urllib.parse,re,hashlib
from PIL import Image
items=[{"genus":"Digitaria","id":"digitaria-ciliaris","name":"Digitaria ciliaris - Flickr - osahiro nishihata.jpg","creator":"Osahiro Nishihata","license":"CC0","role":"Emerging inflorescence close view; confirm anatomical detail from actual pixels"},{"genus":"Digitaria","id":"digitaria-ciliaris","name":"Starr 090121-1186 Digitaria ciliaris.jpg","creator":"Forest & Kim Starr","license":"CC BY 3.0","role":"Multiple inflorescences and specimen-scale flowering architecture"},{"genus":"Bromus","id":"bromus-pubescens","name":"Bromus pubescens - Copenhagen Botanical Garden - DSC07693.JPG","creator":"Daderot","license":"CC0","role":"Additional botanical garden flowering plant reference; lemma hairs remain unverified"}]
failed=[]
for item in items:
 try:
    base=pathlib.Path("content/taxa/Poaceae")/item["genus"]/item["id"]
    path=base/"species.json"
    d=json.loads(path.read_text()); assert d["id"]==item["id"]
    title="File:"+item["name"]
    api="https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url%7Cextmetadata&format=json&titles="+urllib.parse.quote(title)
    with urllib.request.urlopen(urllib.request.Request(api,headers={"User-Agent":"Hays-County-Botany/1.0 (botanical educational image archiver)"}),timeout=45) as f:
        pages=json.load(f)["query"]["pages"]
    info=next(iter(pages.values()))["imageinfo"][0]
    recorded=info.get("extmetadata",{}).get("LicenseShortName",{}).get("value","").upper().replace("-","").replace(" ","")
    expected=item["license"].upper().replace("-","").replace(" ","")
    assert expected in recorded or (expected=="CC0" and "CC0" in recorded),(item["name"],recorded)
    with urllib.request.urlopen(urllib.request.Request(info["url"],headers={"User-Agent":"Hays-County-Botany/1.0"}),timeout=60) as f: raw=f.read()
    assert 12000<len(raw)<18000000
    image=Image.open(io.BytesIO(raw));image.verify()
    image=Image.open(io.BytesIO(raw)).convert("RGB")
    assert image.width>=350 and image.height>=350
    name="commons-"+hashlib.sha256(item["name"].encode()).hexdigest()[:12]+".jpg"
    dest=base/"images"/name;dest.parent.mkdir(parents=True,exist_ok=True)
    image.save(dest,"JPEG",quality=90,optimize=True)
    record={"file":"images/"+name,"role":item["role"],"creator":item["creator"],"license":item["license"],"source_page":"https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_")),"public_reuse":"Exact image-level Commons license checked at ingestion","photo_status":"PROVISIONAL — USER PHOTO REVIEW PENDING; no unverified anatomy arrows"}
    if not any(x.get("file")==record["file"] or x.get("source_page")==record["source_page"] for x in d.get("images",[])): d.setdefault("images",[]).append(record)
    d.setdefault("curation_status",{})["photo_metadata_count"]=len(d["images"])
    d["curation_status"]["photo_files_present"]=sum(str(x.get("file","")).startswith("images/") for x in d["images"])
    d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
    path.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
    print("INSTALLED",item["id"],name)
 except Exception as e:
    failed.append([item["id"],item["name"],str(e)])
    print("HELD",item["id"],str(e))
pathlib.Path("reports/grass-anatomy-archive-002-result.json").write_text(json.dumps({"failed":failed},indent=2)+"\n")
