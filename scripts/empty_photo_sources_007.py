import concurrent.futures,io,json,pathlib,urllib.parse,urllib.request
from PIL import Image,ImageOps
ROOT=pathlib.Path(".");OUT=ROOT/"workflow/empty-photo-007";OUT.mkdir(parents=True,exist_ok=True)
targets=json.loads((OUT/"targets.json").read_text())
HEAD={"User-Agent":"HaysBotany-PhotoCoverage/1.0"}
def get(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers=HEAD),timeout=30) as r:return r.read()
def work(t):
 try:
  name=t["scientific_name"]
  common={"taxon_name":name,"quality_grade":"research","per_page":5,"photos":"true"}
  own=json.loads(get("https://api.inaturalist.org/v1/observations?"+urllib.parse.urlencode(dict(common,user_login="calvinking"))))["results"]
  own=[o for o in own if o["taxon"]["name"]==name and o["user"]["login"]=="calvinking" and any(any(s in p.get("attribution","").lower() for s in ["calvin king","glass root garden","calvinking"]) for p in o["photos"])]
  candidates=own or json.loads(get("https://api.inaturalist.org/v1/observations?"+urllib.parse.urlencode(dict(common,photo_license="cc0,cc-by,cc-by-sa"))))["results"]
  for o in candidates:
   if o["taxon"]["name"]!=name or o["quality_grade"]!="research":continue
   for p in o["photos"]:
    owner=o["user"]["login"]=="calvinking" and any(s in p.get("attribution","").lower() for s in ["calvin king","glass root garden","calvinking"])
    if not owner and p.get("license_code") not in ["cc0","cc-by","cc-by-sa"]:continue
    url=p["url"].replace("/square.","/large.")
    raw=get(url)
    with Image.open(io.BytesIO(raw)) as im:
     im.load();rgb=ImageOps.exif_transpose(im).convert("RGB");rgb.thumbnail((1200,1200))
    if min(rgb.size)<400:continue
    dest=OUT/(t["id"]+".jpg");rgb.save(dest,"JPEG",quality=91,optimize=True)
    return dict(t,observation_id=o["id"],photo_id=p["id"],photo_page="https://www.inaturalist.org/photos/"+str(p["id"]),observation_url="https://www.inaturalist.org/observations/"+str(o["id"]),direct_url=url,source_license=p.get("license_code"),source_attribution=p.get("attribution"),observer=o["user"]["login"],owner_photo=owner,quality_grade=o["quality_grade"],source_taxon=name,dimensions=list(rgb.size),preview=str(dest))
  return dict(t,skip="No exact-species immediately licensed candidate")
 except Exception as e:return dict(t,skip=str(e))
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:results=list(pool.map(work,targets))
(OUT/"candidates.json").write_text(json.dumps({"targets":results},indent=2)+"\n")
print(json.dumps(results,indent=2))
