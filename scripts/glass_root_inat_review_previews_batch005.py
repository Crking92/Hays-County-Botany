#!/usr/bin/env python3
"""Create PRIVATE review previews of licensed user-owned iNaturalist photos.

DO NOT modify canonical species.json or mark images as installed. No GPS used.
"""
import argparse
import csv
import io
import json
import pathlib
import re
import time
import urllib.request
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont, ImageOps

TARGETS=[]  # Loaded from canonical backlog priority queue at runtime.
HEADERS={"User-Agent":"HaysBotany-GlassRootGarden-PhotoInventory/1.0",
         "Accept":"image/jpeg,image/png,image/webp,*/*"}
def safe_url(url):
    if not url.startswith("https://"):
        return ""
    # Source URLs were obtained from iNaturalist photo records.
    host=urllib.parse.urlparse(url).hostname
    if host not in ("static.inaturalist.org","inaturalist-open-data.s3.amazonaws.com"):
        return ""
    return re.sub(r"/(?:square|thumb|small|medium|large|original)\.(?:jpg|jpeg|png)$",
                  "/medium.jpg",url,flags=re.I)
import urllib.parse

def load_rows(path):
    with open(path,newline="",encoding="utf-8-sig") as f:
        rows=list(csv.DictReader(f))
    return [r for r in rows if r.get("photo_id","").isdigit()]
def owner_credit(row):
    a=(row.get("source_attribution") or "").lower()
    return any(s in a for s in ("calvinking","calvin king","glass root garden"))
def choose(rows, n=16):
    # Select spread over distinct iNaturalist observations before taking second
    # photos from an observation; take earlier/later seasons into account.
    per_obs=defaultdict(list)
    for row in rows:
        per_obs[row["observation_id"]].append(row)
    for item in per_obs.values():
        item.sort(key=lambda r:int(r["photo_id"]))
    obs=sorted(per_obs.items(),key=lambda it:it[1][0].get("observed_on",""))
    if len(obs)>n:
        positions=[round(i*(len(obs)-1)/(n-1)) for i in range(n)] if n>1 else [len(obs)//2]
        obs=[obs[i] for i in sorted(set(positions))]
    selected=[xs[0] for _,xs in obs]
    while len(selected)<n:
        added=False
        for _,xs in obs:
            if len(xs)>1:
                selected.append(xs.pop(1))
                added=True
                if len(selected)>=n:break
        if not added:break
    return selected[:n]
def retrieve(url,attempts=3):
    for attempt in range(attempts):
        try:
            req=urllib.request.Request(url,headers=HEADERS)
            with urllib.request.urlopen(req,timeout=25) as resp:
                data=resp.read(10_000_000)
            img=Image.open(io.BytesIO(data))
            img.load()
            return img.convert("RGB")
        except Exception as e:
            print("Preview fetch failed:",str(e),flush=True)
            if attempt==attempts-1:return None
            time.sleep(2*(attempt+1))
    return None
def draw_sheet(images, title, out):
    w=332;h=270;cols=4
    rows=(len(images)+cols-1)//cols
    sheet=Image.new("RGB",(cols*w,max(1,rows)*h+66),"#fbfaf6")
    d=ImageDraw.Draw(sheet)
    d.text((12,10), title+" · Glass Root Garden photo REVIEW",fill="#173b2a")
    d.text((12,35),"PRIVATE REVIEW — verify individual image license before publication",fill="#405746")
    for idx,(item,photo) in enumerate(images):
        x=(idx%cols)*w; y=66+(idx//cols)*h
        fitted=ImageOps.contain(photo,(312,226))
        px=x+(w-fitted.width)//2
        sheet.paste(fitted,(px,y+4))
        d.text((x+8,y+231),"Photo "+item["photo_id"],fill="#193127")
        d.text((x+8,y+247),"Obs "+item["observation_id"],fill="#3c4c43")
    out.parent.mkdir(parents=True,exist_ok=True)
    sheet.save(out,format="JPEG",quality=85,optimize=True)
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",default="workflow/glass-root-inat/output/photo-candidates.csv")
    p.add_argument("--out",default="workflow/glass-root-inat/previews")
    p.add_argument("--per-species",type=int,default=16)
    p.add_argument("--pause",type=float,default=0.8)
    p.add_argument("--queue",default="workflow/glass-root-inat/backlog-plan/priority-queue.csv")
    p.add_argument("--taxa-count",type=int,default=4)
    a=p.parse_args()
    out=pathlib.Path(a.out)
    all_rows=load_rows(a.input)
    with open(a.queue,newline="",encoding="utf-8") as f:
        ranked=list(csv.DictReader(f))
    selected=[r for r in ranked if r.get("claim_conflict")=="False"
              and int(r.get("installed_images") or 999)<=2
              and r.get("is_non_native_comparison")=="False"
              and int(r.get("owner_iNat_photos_not_installed") or 0)>=1]
    chosen=selected[:a.taxa_count]
    print("Canonical owner-photo review choices:",
          [r["id"] for r in chosen],flush=True)
    targets=[(r["id"],r["scientific_name"]) for r in chosen]
    manifests={}
    for sid,name in targets:
        matching=[r for r in all_rows if r.get("canonical_id")==sid
                  or r.get("scientific_name")==name]
        allowed=[r for r in matching if owner_credit(r)]
        verified=[r for r in allowed if r.get("source_license")=="cc-by"]
        selection=choose(verified or allowed,a.per_species)
        info=[]; imgs=[]
        for r in selection:
            url=safe_url(r.get("image_url",""))
            if not url: continue
            photo=retrieve(url)
            if photo is None:continue
            pid=r["photo_id"]
            photo.thumbnail((800,800))
            folder=out/sid
            folder.mkdir(parents=True,exist_ok=True)
            filename="inat-"+pid+".jpg"
            photo.save(folder/filename,format="JPEG",quality=83,optimize=True)
            entry={k:r.get(k,"") for k in
                   ("scientific_name","canonical_id","observation_id","observation_url",
                    "photo_id","photo_page","source_license","source_attribution",
                    "proposed_learner_credit","proposed_learner_license",
                    "rights_gate","observed_on","quality_grade")}
            entry["review_preview_path"]=str(folder/filename)
            entry["diagnostic_role"]="pending_visual_review"
            entry["not_canonical_photo"]=True
            info.append(entry);imgs.append((r,photo))
            time.sleep(a.pause)
        if imgs:
            draw_sheet(imgs,name,out/(sid+"-contact-sheet.jpg"))
        from collections import Counter
        manifests[sid]={"taxon":name,
                        "total_photo_records_found":len(matching),
                        "owner_attribution_matches":len(allowed),
                        "cc_by_owner_attributed":len(verified),
                        "source_license_counts":dict(Counter(r.get("source_license") for r in matching)),
                        "rights_gate_counts":dict(Counter(r.get("rights_gate") for r in matching)),
                        "attribution_examples":sorted(set((r.get("source_attribution") or "")[:90] for r in matching))[:8],
                        "genus_photo_records":sum(r.get("scientific_name","").lower().startswith(name.split()[0].lower()+" ") for r in all_rows),
                        "previews_created":len(info),"candidates":info}
        print(sid,":",len(info),"private previews from",len(matching),"records,",len(allowed),"owned-credit,",len(verified),"CC BY",flush=True)
    out.mkdir(parents=True,exist_ok=True)
    (out/"priority-candidates.json").write_text(json.dumps({
        "purpose":"Privately held photo preview queue; NO canonical installation",
        "license_policy":"Private review only; publication requires individually verified ownership and CC BY attribution",
        "photo_selection":"Stratified by observation date, one photo per observation where possible",
        "warning":"Photo identity, visible anatomical structure and arrow coordinates remain unverified",
        "taxa":manifests},indent=2)+"\n",encoding="utf-8")
if __name__=="__main__":main()
