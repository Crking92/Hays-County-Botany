#!/usr/bin/env python3
"""Research-grade seep-muhly photo contact scout. Exact per-photo CC checks; NO gallery promotion."""
import io,json,urllib.request,urllib.parse,hashlib,pathlib
from PIL import Image,ImageDraw,ImageOps
D=pathlib.Path("reports/lane3-seep-observation-scout-20261026");D.mkdir(exist_ok=True)
GOOD={"cc0","cc-by","cc-by-sa","cc-by-nc","cc-by-nc-sa"}
HEAD={"User-Agent":"HaysCountyBotanyResearch/1.0","Accept":"application/json,image/*"}
def req(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers=HEAD),timeout=22) as r:return r.read(3000000)
def main():
    obs=[];errors=[]
    for p in (1,2,3,4,5):
        q=urllib.parse.urlencode({"taxon_id":165570,"quality_grade":"research","photos":"true","per_page":25,"page":p,"order_by":"observed_on","order":"desc"})
        try:obs+=json.loads(req("https://api.inaturalist.org/v1/observations?"+q))["results"]
        except Exception as e:errors.append(str(e))
    candidates=[]
    for o in obs:
        if (o.get("taxon") or {}).get("id")!=165570:continue
        loc=o.get("place_guess") or "";photos=o.get("photos") or []
        for idx,p in enumerate(photos[:6]):
            if p.get("id") in (58493566,4920088,5077102):continue
            lic=(p.get("license_code") or "").lower()
            if lic not in GOOD:continue
            candidates.append({"id":p["id"],"observation":o["id"],"license":lic,
              "attribution":p.get("attribution"),"place":loc,"quality_grade":o.get("quality_grade"),
              "taxon":(o.get("taxon") or {}).get("name"),
              "url":(p.get("url") or "").replace("/square.","/medium."),
              "index":idx+1,"photo_count":len(photos),
              "score":(40 if "texas" in loc.lower() else 0)+min(len(photos),10)*7+(3 if idx>0 else 0)})
    candidates.sort(key=lambda a:a["score"],reverse=True)
    used={};picked=[]
    for p in candidates:
        n=used.get(p["observation"],0)
        if n>=3:continue
        picked.append(p);used[p["observation"]]=n+1
        if len(picked)>=40:break
    W,H,C=290,290,5; canvas=Image.new("RGB",(W*C,H*8),(255,255,255));draw=ImageDraw.Draw(canvas)
    result=[]
    for i,p in enumerate(picked):
        try:
            with Image.open(io.BytesIO(req(p["url"]))) as im:
                if im.format not in ("JPEG","PNG","WEBP"):continue
                im=ImageOps.exif_transpose(im).convert("RGB")
                im.thumbnail((280,218))
                x=(i%C)*W;y=(i//C)*H
                canvas.paste(im,(x+(W-im.width)//2,y))
        except Exception as e:p["error"]=str(e)[:100];continue
        for k,t in enumerate((f"{i+1}: photo {p['id']}",f"obs {p['observation']}, {p['license']}",
             (p["attribution"] or "")[:35],p["place"][:39])):
            draw.text((x+4,y+220+k*16),t,fill=(20,20,20))
        result.append({**p,"slot":i+1,"photo_page":f"https://www.inaturalist.org/photos/{p['id']}"})
    canvas.save(D/"contact.jpg","JPEG",quality=89,exif=b"")
    report={"status":"SCREENING_ONLY_NOT_SPECIES_GALLERY","taxon":"Muhlenbergia reverchonii",
      "observations_scanned":len(obs),"candidate_photos":len(candidates),"downloaded_thumbnails":len(result),
      "errors":errors,"photos":result,
      "rights_rule":"Per-photo licensed only; NC conditionally suitable for strictly noncommercial site with credit, check exact source before installation",
      "anatomy_rule":"Observation determination is not an independent voucher; do not label rooted crown, rhizome, true inner ligule or microscopic anatomy without opening the original",
      "missing":["connected belowground condensed rhizome with roots, scale","opened true ligule with ruler"]}
    (D/"report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print("SCOUT",len(obs),len(candidates),len(result),errors)
if __name__=="__main__":main()
