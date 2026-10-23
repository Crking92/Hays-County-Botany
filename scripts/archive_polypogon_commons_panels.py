#!/usr/bin/env python3
"""Archive two existing Polypogon Commons teaching panels only after Commons image-level rights checks."""
import io, json, pathlib, re, urllib.parse, urllib.request, hashlib, html
from PIL import Image
p=pathlib.Path("content/taxa/Poaceae/Polypogon/polypogon-monspeliensis/species.json")
s=json.loads(p.read_text()); outcomes=[]
for item in s["visual_comparison"]["items"]:
    url=item.get("image_url","")
    if "thumb.wikimedia.org" not in url: continue
    source=item.get("source_page","")
    try:
        filename=urllib.parse.unquote(source.split("/wiki/File:",1)[1]).replace("_"," ")
        q=urllib.parse.urlencode({"action":"query","prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":"1600","titles":"File:"+filename,"format":"json"})
        def get(u):
            req=urllib.request.Request(u,headers={"User-Agent":"HaysBotany/1.0 (licensed plant media review)"})
            with urllib.request.urlopen(req,timeout=50) as response:return response.read()
        data=json.loads(get("https://commons.wikimedia.org/w/api.php?"+q))
        info=next(iter(data["query"]["pages"].values()))["imageinfo"][0]
        md=info["extmetadata"]
        lic=re.sub(r"[^A-Z0-9]","",md.get("LicenseShortName",{}).get("value","").upper())
        original=re.sub(r"[^A-Z0-9]","",item.get("license","").upper())
        if lic!=original or lic not in ("CCBY40","CCBY20"):raise ValueError("license mismatch or not approved: "+lic+"/"+original)
        artist=html.unescape(re.sub("<[^>]+>","",md.get("Artist",{}).get("value",""))).strip()
        if not artist:raise ValueError("artist missing")
        raw=get(info.get("thumburl") or info["url"])
        if not 10000<len(raw)<25000000:raise ValueError("unexpected byte length")
        im=Image.open(io.BytesIO(raw));im.verify()
        im=Image.open(io.BytesIO(raw)).convert("RGB")
        if min(im.size)<250:raise ValueError("small source")
        dest=p.parent/"images"/("commons-polypogon-"+hashlib.sha256(source.encode()).hexdigest()[:12]+".jpg")
        dest.parent.mkdir(parents=True,exist_ok=True)
        im.save(dest,"JPEG",quality=90,optimize=True)
        item["archived_original_image_url"]=url
        item["image_url"]=str(dest).replace("\\","/")
        item["photo_status"]="LOCALLY ARCHIVED — PROVISIONAL USER PHOTO REVIEW PENDING; visible gross structure arrows only"
        item["archive_creator_from_commons"]=artist
        item["archive_license_verified"]=md["LicenseShortName"]["value"]
        s["images"].append({"file":"images/"+dest.name,"role":item.get("image_role",""),"creator":item["creator"],"license":item["license"],"license_url":item.get("license_url"),"source_page":source,"archived_original_url":url,"source_creator_metadata":artist,"photo_status":"LOCALLY ARCHIVED; provisional ID/anatomy"})
        outcomes.append({"source":source,"archive":str(dest),"status":"archived"})
    except Exception as e:outcomes.append({"source":source,"status":"held","reason":str(e)})
if any(o["status"]=="archived" for o in outcomes):
    s.setdefault("field_id_finish_pass",{})["commons_photo_archive_20261023"]={"results":outcomes,"status":"FIELD_READY_PHOTO_GAPS","no_new_micro_arrows":True}
    p.write_text(json.dumps(s,ensure_ascii=False,indent=2)+"\n")
report=pathlib.Path("reports/polypogon-commons-photo-archive-20261023.json")
report.write_text(json.dumps({"results":outcomes},indent=2)+"\n")
print(json.dumps(outcomes))
