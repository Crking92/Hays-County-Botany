#!/usr/bin/env python3
"""Paspalum setaceum: archive two exact-taxon CC BY detail photos."""
import io,json,pathlib,urllib.request,urllib.parse,hashlib
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Paspalum/paspalum-setaceum")
p=base/"species.json";d=json.loads(p.read_text());assert d["id"]=="paspalum-setaceum"
for id,role in [("49099709","Source-associated additional flowering/leaf view; diagnostic pixels subject to inspection"),("49099728","Source-associated additional growth/inflorescence view; diagnostic pixels subject to inspection")]:
 title="File:Paspalum setaceum "+id+".jpg"
 api="https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url%7Cextmetadata&format=json&titles="+urllib.parse.quote(title)
 req=urllib.request.Request(api,headers={"User-Agent":"Hays-County-Botany/1.0 (educational image archive)"})
 with urllib.request.urlopen(req,timeout=40) as response: pages=json.load(response)["query"]["pages"]
 info=next(iter(pages.values()))["imageinfo"][0]
 license=info.get("extmetadata",{}).get("LicenseShortName",{}).get("value","").upper().replace("-","")
 assert "CCBY4.0" in license.replace(" ",""),license
 with urllib.request.urlopen(urllib.request.Request(info["url"],headers={"User-Agent":"Hays-County-Botany/1.0"}),timeout=60) as response: raw=response.read()
 assert 12000<len(raw)<10000000
 im=Image.open(io.BytesIO(raw));im.verify()
 im=Image.open(io.BytesIO(raw)).convert("RGB")
 name="alex-abair-"+id+".jpg";dest=base/"images"/name;dest.parent.mkdir(parents=True,exist_ok=True)
 im.save(dest,"JPEG",quality=92,optimize=True)
 source="https://commons.wikimedia.org/wiki/File:Paspalum_setaceum_"+id+".jpg"
 record={"file":"images/"+name,"role":role,"creator":"Alex Abair","license":"CC BY 4.0","license_url":"https://creativecommons.org/licenses/by/4.0/","source_page":source,"original_source_page":"https://www.inaturalist.org/photos/"+id,"public_reuse":"Attribution required","photo_status":"PROVISIONAL — USER PHOTO REVIEW PENDING; no claimed ligule/spikelet microscale"}
 if not any(x.get("file")==record["file"] or x.get("source_page")==source for x in d.get("images",[])):d["images"].append(record)
d.setdefault("curation_status",{})["photo_metadata_count"]=len(d["images"])
d["curation_status"]["photo_files_present"]=sum(str(x.get("file","")).startswith("images/") for x in d["images"])
d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
print("Paspalum setaceum archive completed",len(d["images"]))
