#!/usr/bin/env python3
"""Lane 5: licensed Commons exact-taxon photographs for Chloris verticillata."""
import io, json, pathlib, re, hashlib, html, urllib.parse, urllib.request
from PIL import Image
p=pathlib.Path("content/taxa/Poaceae/Chloris/chloris-verticillata/species.json")
s=json.loads(p.read_text())
def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":"HaysBotany/1.0 grass-visual-learner (licensed media research)"})
    with urllib.request.urlopen(req,timeout=45) as resp:return resp.read()
api="https://commons.wikimedia.org/w/api.php?"
def query(opts): return json.loads(get(api+urllib.parse.urlencode(dict(opts,format="json"))))
category=query({"action":"query","list":"categorymembers","cmtitle":"Category:Chloris verticillata","cmtype":"file","cmlimit":"100"})
names=[x["title"] for x in category["query"]["categorymembers"]]
names=[x for x in names if re.search(r"\.(jpe?g|png)$",x,re.I) and not re.search(r"HC-19|illustrat|drawing|herbarium",x,re.I)]
def score(n):return (0 if re.search("ligule|collar|spikelet|lemma|glume|awn",n,re.I) else 1 if re.search("flower|detail|close|seed",n,re.I) else 2,n)
names.sort(key=score)
results=[]
existing={x.get("source_page","").replace("%3A",":") for x in s.get("images",[])}
for title in names:
    if sum(x["status"]=="archived" for x in results)>=3:break
    source="https://commons.wikimedia.org/wiki/"+title.replace(" ","_")
    if source in existing:continue
    try:
        page=next(iter(query({"action":"query","prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":"1500","titles":title})["query"]["pages"].values()))
        info=page["imageinfo"][0];md=info["extmetadata"]
        lic=md.get("LicenseShortName",{}).get("value","")
        norm=re.sub(r"[^A-Z0-9]","",lic.upper())
        if norm not in {"CC0","CC01","CC010","CCBY20","CCBY30","CCBY40","CCBYSA20","CCBYSA30","CCBYSA40","PUBLICDOMAIN"}:raise ValueError("license held: "+lic)
        artist=html.unescape(re.sub("<[^>]+>","",md.get("Artist",{}).get("value",""))).strip()
        if not artist:raise ValueError("creator missing")
        raw=get(info.get("thumburl") or info["url"])
        image=Image.open(io.BytesIO(raw)); image.verify()
        image=Image.open(io.BytesIO(raw)).convert("RGB")
        if min(image.size)<400:raise ValueError("image too small")
        name="commons-chloris-verticillata-"+hashlib.sha256(title.encode()).hexdigest()[:12]+".jpg"
        dest=p.parent/"images"/name;dest.parent.mkdir(parents=True,exist_ok=True);image.save(dest,format="JPEG",quality=90,optimize=True)
        rel="images/"+name; local=str(dest).replace("\\","/")
        s["images"].append({"file":rel,"role":"Exact-taxon Wikimedia photograph; anatomical structures require pixel review","creator":artist,"license":lic,"source_page":source,"source_title":title,"photo_status":"LICENSE VERIFIED AND PHYSICALLY ARCHIVED; pixel/anatomy review pending"})
        s["visual_comparison"]["items"].append({"label":"TUMBLE WINDMILLGRASS — archived source photograph ("+title[5:65]+")","scientific_name":"Chloris verticillata","image_url":local,"image_fit":"contain","image_role":"Source-taxonomic species photograph. Specific ligule, spikelet or other organ NOT verified.","caption":"An independently licensed photograph of Chloris verticillata. Inspect visible branching and plant form; don't infer sterile/fertile lemma or measurable anatomy until image-level microscopy is confirmed.","creator":artist,"license":lic,"source_page":source,"markers":[],"photo_status":"PROVISIONAL — physical archive verified, anatomy/arrow review pending."})
        results.append({"file":name,"source":source,"license":lic,"status":"archived"})
    except Exception as exc:results.append({"source":source,"status":"held","reason":str(exc)[:260]})
if any(x["status"]=="archived" for x in results):
    s.setdefault("field_id_finish_pass",{})["lane5_commons_archive_20261023"]={"results":results,"stage":"FIELD_READY_PHOTO_GAPS","remaining":"Photographed TRUE collar ligule and mature spikelet with separated glumes, fertile lemma and sterile awns at millimeter scale; arrows and live Pages QA"}
    p.write_text(json.dumps(s,indent=2,ensure_ascii=False)+"\n")
path=pathlib.Path("reports/lane5-chloris-verticillata-commons-20261023.json")
path.write_text(json.dumps({"results":results,"discovered_files":len(names)},indent=2)+"\n")
print(json.dumps(results))
