#!/usr/bin/env python3
"""Download Joey's research-grade CC BY-NC candidate images into review staging only."""
import hashlib,io,json
from pathlib import Path
from urllib.request import Request,urlopen
from PIL import Image
R=Path(__file__).resolve().parents[1]
SOURCE=R/"workflow/photo-first-batch003-joey-complementary-photo-leads.json"
OUT=R/"research-drafts/photo-imports/joey-batch003"
OUT.mkdir(parents=True,exist_ok=True)
def get(url,limit=12000000):
    with urlopen(Request(url,headers={"User-Agent":"HaysBotanyPhotoResearch/1.0"}),timeout=30) as response:
        data=response.read(limit+1)
    if len(data)>limit:raise ValueError("exceeds byte cap")
    return data
results=[]
for plant in json.loads(SOURCE.read_text())["records"]:
    out={"name":plant["name"],"photos":[]}
    for lead in plant["photo_leads"]:
        item={"photo_id":str(lead["photo_id"]),"observation_id":str(lead["observation_id"]),"status":"blocked"}
        try:
            obs=json.loads(get("https://api.inaturalist.org/v1/observations/"+item["observation_id"],2000000))["results"][0]
            owner=(obs.get("user") or {}).get("login","").lower()
            attribution=[p for p in obs.get("photos",[]) if str(p.get("id"))==item["photo_id"]]
            if not attribution:raise ValueError("photo not on original observation")
            photo=attribution[0]
            lic=(photo.get("license_code") or "").lower()
            item.update(photographer=photo.get("attribution"),license=lic,quality_grade=obs.get("quality_grade"),taxon=(obs.get("taxon") or {}).get("name"))
            if item["taxon"]!=plant["name"]:raise ValueError("taxon mismatch")
            if lic!="cc-by-nc":raise ValueError("license mismatch; not exact CC BY-NC")
            if "joey santore" not in (photo.get("attribution") or "").lower():raise ValueError("photographer attribution mismatch")
            if obs.get("quality_grade")!="research":raise ValueError("identification not research-grade")
            url=photo.get("url") or lead.get("image_url") or ""
            for size in ("square","thumb","small","medium"):url=url.replace("/"+size+".","/large.")
            if not url.startswith("https://"):raise ValueError("invalid photo URL")
            data=get(url)
            im=Image.open(io.BytesIO(data));im.verify()
            im=Image.open(io.BytesIO(data)).convert("RGB")
            if min(im.size)<300:raise ValueError("image too small")
            slug=plant["name"].lower().replace(" ","-")
            path=OUT/slug/("joey-"+item["photo_id"]+".jpg")
            path.parent.mkdir(parents=True,exist_ok=True)
            im.save(path,quality=88,optimize=True)
            item.update(status="downloaded_pending_visual_review",file=str(path.relative_to(R)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),width=im.width,height=im.height,source_page="https://www.inaturalist.org/photos/"+item["photo_id"],creator="Joey Santore",usage="CC BY-NC — attribution required; noncommercial only")
        except Exception as exc:item["blocker"]=str(exc)[:240]
        out["photos"].append(item)
    results.append(out)
report={"records":results,"note":"Research-grade and metadata checked; visual diagnosis still PENDING. These are NOT installed on public species cards."}
(OUT/"import-report.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({"downloaded":sum(p["status"]=="downloaded_pending_visual_review" for r in results for p in r["photos"]),"blocked":sum(p["status"]=="blocked" for r in results for p in r["photos"])}))
