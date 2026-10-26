#!/usr/bin/env python3
"""Lane 3: exact-source, photo-license-checked Buckley's tridens candidate review.
Only commit a CONTACT SHEET to reports; no species gallery changes.
"""
from __future__ import annotations
import io,json,pathlib,urllib.parse,urllib.request,hashlib
from PIL import Image,ImageOps,ImageDraw
ROOT=pathlib.Path("reports/lane3-buckley-anatomy-scout-20261026")
ROOT.mkdir(parents=True,exist_ok=True)
TAXON_ID=169947 # iNaturalist Tridens buckleyanus synonym, as prior 2026-10-23 canonical reports
LIC={"cc0","cc-by","cc-by-sa","cc-by-nc","cc-by-nc-sa"}
EXCLUDE={102622491,174189386,174189373,174189357,240395559,173616239,157748934,380287142}
UA={"User-Agent":"HaysCountyBotanyNoncommercialResearch/1.0","Accept":"application/json,image/*"}
def get(url,cap=6_000_000):
    with urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=23) as r:
        b=r.read(cap+1)
    if len(b)>cap:raise ValueError("response too big")
    return b
def main():
    observations=[];err=[]
    for page in range(1,6):
        q=urllib.parse.urlencode(dict(taxon_id=TAXON_ID,quality_grade="research",photos="true",per_page=25,page=page,order_by="observed_on",order="desc"))
        try:
            j=json.loads(get("https://api.inaturalist.org/v1/observations?"+q))
            observations+=j.get("results",[])
        except Exception as e:err.append({"page":page,"error":repr(e)})
    candidates=[]
    for ob in observations:
        if (ob.get("taxon") or {}).get("id")!=TAXON_ID:continue
        place=ob.get("place_guess") or ""
        photos=ob.get("photos") or []
        for seq,p in enumerate(photos[:9]):
            id=p.get("id")
            if not id or id in EXCLUDE:continue
            lic=(p.get("license_code") or "").lower()
            if lic not in LIC:continue
            url=p.get("url") or ""
            if not url.startswith("https://"):continue
            source=url.replace("/square.","/medium.")
            candidates.append(dict(
                photo_id=id,observation_id=ob["id"],photo_license=lic,
                photographer=p.get("attribution"),source_photo=f"https://www.inaturalist.org/photos/{id}",
                source_observation=f"https://www.inaturalist.org/observations/{ob['id']}",
                photo_url=source,place=place,
                observed_on=ob.get("observed_on"),
                source_taxon=ob["taxon"].get("name"),
                sequence=seq+1,photos_same_observation=len(photos),
                score=(32 if "texas" in place.lower() or ", tx" in place.lower() else 0)+
                  min(photos.__len__(),9)*5+(3 if seq>1 else 0)+
                  (11 if lic in ("cc0","cc-by","cc-by-sa") else 0)
            ))
    candidates.sort(key=lambda x:(x["score"],x["observation_id"]),reverse=True)
    selection=[];used={};ids=set()
    for x in candidates:
        if x["photo_id"] in ids or used.get(x["observation_id"],0)>=5:continue
        used[x["observation_id"]]=used.get(x["observation_id"],0)+1
        selection.append(x);ids.add(x["photo_id"])
        if len(selection)>=45:break
    columns=5;w=285;h=285
    sheet=Image.new("RGB",(columns*w,9*h),(250,250,250))
    d=ImageDraw.Draw(sheet)
    installed=[]
    for pos,x in enumerate(selection):
        try:
            data=get(x["photo_url"],2_000_000)
            with Image.open(io.BytesIO(data)) as im:
                if im.format not in ("JPEG","WEBP","PNG"):raise ValueError(im.format)
                im=ImageOps.exif_transpose(im).convert("RGB")
                im.thumbnail((275,210))
                col=pos%columns;row=pos//columns
                ox=col*w;oy=row*h
                sheet.paste(im,(ox+(w-im.width)//2,oy+4))
            for line,t in enumerate([
                f"{pos+1}. photo {x['photo_id']}",f"obs {x['observation_id']} / {x['photo_license']}",
                str(x["photographer"] or "")[:43],x["place"][:43]
                ]):
                d.text((ox+4,oy+217+line*16),t,fill=(25,25,25))
            installed.append(dict(x,slot=pos+1,review_thumb_saved=True))
        except Exception as e:x["download_hold"]=repr(e)
    img=ROOT/"contact.jpg";sheet.save(img,format="JPEG",quality=88,optimize=True,exif=b"")
    report={
      "species":"Tridentopsis buckleyana","source_taxon_id":TAXON_ID,
      "source_taxon_synonym":"Tridens buckleyanus",
      "status":"PHOTO_LEVEL_LICENSE_CONTACT_SHEET_REVIEW_NOT_INSTALLATION",
      "observations_scanned":len(observations),
      "candidate_photos":len(candidates),"contact_sheet_photos":len(installed),
      "errors":err,"contact_path":str(img),
      "contact_sha256":hashlib.sha256(img.read_bytes()).hexdigest(),
      "licensed_photos":installed,
      "not_accepted_evidence":"Photograph position on contact sheet is not validation that roots, free ligule or glumes are shown; full original pixel review and source/voucher confirmation required",
      "next_photo_role":["Same rooted perennial bunch plus flowering culm and mm scale","True ciliate free ligule interior opening with mm scale","Dissected mature glumes and lemma hairs with mm scale"],
      "noncommercial_scope":"Conditional use only for individually confirmed BY-NC credited site photos, no NC media on monetized site",
      "canonical_gallery_changed":False
    }
    (ROOT/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print("BUCKLEY PHOTO SCOUT",len(observations),len(candidates),len(installed),err)
    assert len(installed)>0,"No licensed thumbnails downloaded, do not claim a photo upgrade"
if __name__=="__main__":main()
