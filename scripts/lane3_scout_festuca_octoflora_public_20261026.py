#!/usr/bin/env python3
"""Lane 3 targeted source/rights/visual audit for exact Vulpia octoflora.
Writes ONLY credited CC0/CC-BY contact sheet and evidence, not canonical card.
Require a second human visual inspection before promotion to species gallery.
"""
import io,json,pathlib,urllib.request,urllib.parse,hashlib,time,html
from PIL import Image,ImageOps,ImageDraw,ImageFont
ROOT=pathlib.Path("reports")
ROOT.mkdir(exist_ok=True)
OUT=ROOT/"lane3-festuca-octoflora-photo-scout-20261026.json"
IMG=ROOT/"lane3-festuca-octoflora-photo-scout-20261026.jpg"
UA="HaysCountyBotany/1.0 (noncommercial educational flora photo license audit; github.com/Crking92/Hays-County-Botany)"
report={"species":"Vulpia octoflora","purpose":"One-time targeted exact-species public-rights evidence and human pixel-review sheet; NOT final identity or photo installation","candidate_photos":[],"failures":[],"license_allowlist":["cc0","cc-by"],"gallery_install":0,"arrows_added":0}
def get(url,limit=16_000_000):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/json,image/jpeg,image/*"})
    with urllib.request.urlopen(req,timeout=35) as f:
        bs=f.read(limit+1)
        if len(bs)>limit: raise ValueError("Response too large")
        return bs
def api(url):
    return json.loads(get(url))
def maybe_records():
    taxon=api("https://api.inaturalist.org/v1/taxa/autocomplete?"+urllib.parse.urlencode({"q":"Vulpia octoflora","per_page":20}))
    taxa=[x for x in taxon.get("results",[]) if x.get("name")=="Festuca octoflora" and x.get("rank")=="species"]
    if len(taxa)!=1:raise ValueError("Exact species taxon not uniquely resolved: "+str([(x.get("id"),x.get("name")) for x in taxon.get("results",[])][:10]))
    tid=taxa[0]["id"]; report["inat_taxon_id"]=tid; report["canonical_name"]="Festuca octoflora"; report["source_query_synonym"]="Vulpia octoflora"
    allobs=[]
    for page in [1,2]:
        q=urllib.parse.urlencode({"taxon_id":tid,"quality_grade":"research","photos":"true","per_page":100,"page":page,"order":"desc","order_by":"observed_on"})
        data=api("https://api.inaturalist.org/v1/observations?"+q)
        allobs.extend(data.get("results",[]))
        report["observations_reported"]=data.get("total_results",None)
        if len(data.get("results",[]))<100:break
    report["observations_sampled"]=len(allobs)
    candidates=[]
    for ob in allobs:
        if ob.get("taxon",{}).get("name")!="Festuca octoflora":continue
        for photo in ob.get("photos",[])[:6]:
            lic=(photo.get("license_code") or "").lower().strip()
            if lic not in ("cc0","cc-by"):continue
            pid=photo.get("id")
            if not pid or any(x["photo_id"]==pid for x in candidates):continue
            candidates.append({"observation_id":ob["id"],"photo_id":pid,
             "license_code":lic,"attribution":photo.get("attribution"),
             "username":ob.get("user",{}).get("login"),
             "taxon":ob["taxon"]["name"],
             "observation_url":"https://www.inaturalist.org/observations/"+str(ob["id"]),
             "photo_url":"https://www.inaturalist.org/photos/"+str(pid),
             "date":ob.get("observed_on"),
             "source_url":photo.get("url", ""),
             "location_coarse":ob.get("place_guess","")[:85],
             "grade":ob.get("quality_grade"),
             "rights_review":"Exact observation species + photo-level license in iNaturalist API; botany identification remains source-determined until independent specimen check."})
            if len(candidates)>=28:break
        if len(candidates)>=28:break
    return candidates
try:
    candidates=maybe_records()
    if not candidates: raise ValueError("No individual cc0/cc-by source photos in sampled exact species observations")
    font=ImageFont.load_default()
    W=400; H=300; CAP=66
    cols=4; nrows=(len(candidates)+cols-1)//cols
    sheet=Image.new("RGB",(cols*W,nrows*(H+CAP)),(244,244,240))
    draw=ImageDraw.Draw(sheet)
    for i,row in enumerate(candidates):
        x=(i%cols)*W;y=(i//cols)*(H+CAP)
        pid=row["photo_id"]
        # iNaturalist open-data original is a stable exact-photo-ID mirror for rights-screened originals.
        url="https://inaturalist-open-data.s3.amazonaws.com/photos/"+str(pid)+"/original.jpg"
        try:
            bs=get(url)
            with Image.open(io.BytesIO(bs)) as im:
                if im.format not in ("JPEG","PNG"):raise ValueError("Unexpected image format")
                im=ImageOps.exif_transpose(im).convert("RGB")
                if min(im.size)<400:raise ValueError("Source resolution too small")
                row["original_dimensions"]=[im.width,im.height]
                row["source_sha256"]=hashlib.sha256(bs).hexdigest()
                im.thumbnail((W-8,H-8))
                sheet.paste(im,(x+(W-im.width)//2,y+(H-im.height)//2))
            row["preview_status"]="PHOTO_BYTES_READ_FOR_CONTACT_SHEET"
        except Exception as exc:
            row["preview_status"]="REMOTE_SOURCE_UNAVAILABLE"
            row["preview_error"]=str(exc)[:145]
        text=f"{i+1:02d}  photo {pid}  {row['license_code']}  obs {row['observation_id']}"
        draw.text((x+8,y+H+2),text,fill=(10,10,10),font=font)
        credited=(row.get("attribution") or row.get("username") or "unspecified").replace("\n"," ")[:58]
        draw.text((x+8,y+H+20),credited,fill=(20,20,20),font=font)
        draw.text((x+8,y+H+38),row.get("date","") or "date unavailable",fill=(40,40,40),font=font)
    sheet.save(IMG,"JPEG",quality=86,optimize=True)
    report["candidate_photos"]=candidates
    report["contact_sheet"]=str(IMG)
    report["contact_sheet_sha256"]=hashlib.sha256(IMG.read_bytes()).hexdigest()
    report["rights_note"]="Photo-specific cc0 and cc-by only, photo IDs, original source and creator metadata retained. Contact sheet is a credited research review artifact, not a species gallery replacement. Do not export contact image itself without required CC BY credits."
except Exception as exc:
    report["failures"].append(str(exc)[:350])
OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print(json.dumps({"candidate_count":len(report["candidate_photos"]),"failures":report["failures"],"report":str(OUT),"sheet":str(IMG)},indent=2))
