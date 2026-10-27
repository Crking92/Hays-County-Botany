#!/usr/bin/env python3
"""Photo-level CC scan for accepted tumblegrass iNaturalist records, using historical
Schedonnardus paniculatus synonym. Contact sheet ONLY: original-pixel verification first.
"""
import urllib.request,urllib.parse,json,io,pathlib,hashlib
from PIL import Image,ImageDraw,ImageOps
ROOT=pathlib.Path("reports/lane3-tumblegrass-inat-anatomy-scout-20261027");ROOT.mkdir(parents=True,exist_ok=True)
PHOTO_LIC={"cc0","cc-by","cc-by-sa","cc-by-nc","cc-by-nc-sa"}
HEAD={"User-Agent":"HaysCountyBotany-Educational-Native-Grass-Learner/1.0","Accept":"application/json,image/*"}
def get(url,cap=7_000_000):
  req=urllib.request.Request(url,headers=HEAD)
  with urllib.request.urlopen(req,timeout=27) as r:
    b=r.read(cap+1)
  if len(b)>cap:raise ValueError("Oversize response")
  return b
def main():
  taxa=json.loads(get("https://api.inaturalist.org/v1/taxa/autocomplete?q=Schedonnardus%20paniculatus"))
  matches=[x for x in taxa.get("results",[]) if x.get("name") in ("Schedonnardus paniculatus","Muhlenbergia paniculata") and x.get("rank")=="species"]
  if not matches:
    taxa2=json.loads(get("https://api.inaturalist.org/v1/taxa/autocomplete?q=Muhlenbergia%20paniculata"))
    matches=[x for x in taxa2.get("results",[]) if x.get("name") in ("Schedonnardus paniculatus","Muhlenbergia paniculata") and x.get("rank")=="species"]
  if not matches:raise RuntimeError("No exact accepted/synonym source taxon, fail closed")
  taxon=matches[0]["id"]
  records=[];errs=[]
  for page in range(1,5):
    q=urllib.parse.urlencode({"taxon_id":taxon,"quality_grade":"research","photos":"true","per_page":25,"page":page,"order_by":"observed_on","order":"desc"})
    try:records+=json.loads(get("https://api.inaturalist.org/v1/observations?"+q))["results"]
    except Exception as e:errs.append({"page":page,"error":repr(e)})
  arr=[]
  for obs in records:
    if (obs.get("taxon") or {}).get("id")!=taxon:continue
    photos=obs.get("photos") or [];loc=obs.get("place_guess") or ""
    for ind,p in enumerate(photos[:9]):
      lic=(p.get("license_code") or "").lower()
      if lic not in PHOTO_LIC or not p.get("id"):continue
      url=p.get("url") or ""
      if not url.startswith("https://"):continue
      arr.append({"photo_id":p["id"],"observation_id":obs["id"],"source_taxon":obs["taxon"]["name"],
        "photo_page":f"https://www.inaturalist.org/photos/{p['id']}",
        "observation_page":f"https://www.inaturalist.org/observations/{obs['id']}",
        "thumb_url":url.replace("/square.","/medium."),"license":lic,"attribution":p.get("attribution"),
        "place":loc,"photo_count":len(photos),"sequence":ind+1,"research_grade":True,
        "rank":(35 if "texas" in loc.lower() else 0)+len(photos)*4+(4 if ind else 0)+
          (8 if lic in ("cc0","cc-by","cc-by-sa") else 0)})
  arr.sort(key=lambda p:(p["rank"],p["observation_id"]),reverse=True)
  chosen=[];perobs={}
  for p in arr:
    n=perobs.get(p["observation_id"],0)
    if n>=3:continue
    perobs[p["observation_id"]]=n+1
    chosen.append(p)
    if len(chosen)>=32:break
  W,H,C=300,305,4;rows=max(1,(len(chosen)+C-1)//C)
  out=Image.new("RGB",(W*C,H*rows),"white")
  draw=ImageDraw.Draw(out);selected=[]
  for i,p in enumerate(chosen):
    try:
      data=get(p["thumb_url"],2_000_000)
      with Image.open(io.BytesIO(data)) as im:
        if im.format not in ("JPEG","WEBP","PNG"):continue
        img=ImageOps.exif_transpose(im).convert("RGB")
        img.thumbnail((288,226))
      x=i%C*W;y=i//C*H
      out.paste(img,(x+(W-img.width)//2,y+2))
      for k,lab in enumerate((f"slot {i+1}, photo {p['photo_id']}",f"obs {p['observation_id']} {p['license']}",str(p["attribution"] or "")[:44],p["place"][:44])):
        draw.text((x+5,y+229+k*17),lab,fill="black")
      selected.append(dict(p,slot=i+1))
    except Exception as e:errs.append({"photo":p["photo_id"],"error":repr(e)[:180]})
  output=ROOT/"contact.jpg";out.save(output,"JPEG",quality=90,exif=b"",optimize=True)
  report={"status":"INDIVIDUALLY_CC_LICENSED_OBSERVATION_CONTACT_NEEDS_FULL_PIXEL_AND_SPECIMEN_CHECK",
    "taxon":matches[0]["name"],"iNat_taxon_id":taxon,"canonical_taxon":"Muhlenbergia paniculata",
    "source_synonym":"Schedonnardus paniculatus","observations":len(records),
    "eligible_photo_records":len(arr),"contact_photos":len(selected),"sheet":str(output),
    "sha256":hashlib.sha256(output.read_bytes()).hexdigest(),"selected":selected,"errors":errs,
    "no_gallery_update":True,"no_new_photo_role_certification":True,
    "priority_organs":["true inner membranous ligule","one-sided 3–4 mm spikelet attachment","visible glumes and mature lemma","whole attached flowering plant showing crown"],
    "license_policy":"Filter exact iNat photo-level license, preserve NC/SA and photographer credit; source observation determination is not voucher",
    "source":["https://www.inaturalist.org/","https://api.inaturalist.org/v1/observations"]}
  (ROOT/"report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
  print("Tumblegrass scored obs",len(records),"photo records",len(arr),"source pixels",len(selected),"errors",len(errs))
  assert len(selected)>=1
if __name__=="__main__":main()
