import json,urllib.parse,urllib.request,re
names=["Triodanis leptocarpa","Triodanis coloradoensis","Triodanis texana"]
def get(url):
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"HaysBotanyPhotoAudit/1.0 (education)"}),timeout=15) as r:return json.load(r)
 except Exception as e:return {"error":str(e)}
out={}
for name in names:
 params=urllib.parse.urlencode({"action":"query","generator":"search","gsrsearch":"intitle:"+name,"gsrnamespace":6,"gsrlimit":20,"prop":"imageinfo","iiprop":"url|extmetadata","format":"json"})
 x=get("https://commons.wikimedia.org/w/api.php?"+params)
 items=[]
 for p in x.get("query",{}).get("pages",{}).values():
  for i in p.get("imageinfo",[]):
   m=i.get("extmetadata",{})
   clean=lambda k:re.sub("<[^>]+>","",m.get(k,{}).get("value",""))
   items.append({"title":p.get("title"),"url":i.get("url"),"license":clean("LicenseShortName"),"creator":clean("Artist")[:250]})
 y=get("https://api.inaturalist.org/v1/observations?"+urllib.parse.urlencode({"taxon_name":name,"quality_grade":"research","photos":"true","per_page":80}))
 pics=[]
 for o in y.get("results",[]):
  if o.get("taxon",{}).get("name")!=name:continue
  for p in o.get("photos",[]):
   if p.get("license_code") not in ["cc0","cc-by","cc-by-sa","cc-by-nc","cc-by-nc-sa"]:continue
   pics.append({"photo_id":p.get("id"),"license":p.get("license_code"),"creator":p.get("attribution"),"url":p.get("url"),"place":o.get("place_guess"),"observation":o.get("id")})
 out[name]={"commons":items,"inat":pics[:20],"errors":[x.get("error"),y.get("error")]}
from pathlib import Path
p=Path("research-drafts/triodanis-photo-evidence-20261013.json");p.parent.mkdir(exist_ok=True)
p.write_text(json.dumps(out,indent=2)+"\n")
print({k:(len(v["commons"]),len(v["inat"])) for k,v in out.items()})
