#!/usr/bin/env python3
"""Archive CC-cleared exact-taxon fluffgrass photos, with fail-closed rights checks."""
import io,json,time,pathlib,urllib.parse,urllib.request,urllib.error,hashlib,re,html
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Munroa/munroa-pulchella")
p=base/"species.json";d=json.loads(p.read_text());assert d["id"]=="munroa-pulchella"
candidates=[
 ("Dasyochloa pulchella - Flickr - aspidoscelis (3).jpg","Potential additional close plant/flowering view; inspect visual organs before using as diagnostic proof"),
 ("Dasyochloa pulchella 24026826.jpg","Additional exact-taxon photo with diagnostic potential; pixel inspection pending")
]
holds=[]
def get(url):
 for attempt in range(5):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Hays-County-Botany/1.0 (educational photographic archiving)"}),timeout=65) as response:return response.read()
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or attempt==4:raise
   time.sleep(25*(attempt+1))
for filename,role in candidates:
 try:
  title="File:"+filename
  api="https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url%7Cextmetadata&format=json&titles="+urllib.parse.quote(title)
  obj=next(iter(json.loads(get(api))["query"]["pages"].values()));info=obj["imageinfo"][0]
  m=info.get("extmetadata",{})
  license=m.get("LicenseShortName",{}).get("value","").upper().replace("-","").replace(" ","")
  assert license in ("CC0","CCBY2.0","CCBY3.0","CCBY4.0","CCBYSA2.0","CCBYSA3.0","CCBYSA4.0","PUBLICDOMAIN"),(filename,license)
  creator_html=m.get("Artist",{}).get("value","")
  creator=html.unescape(re.sub("<[^>]*>","",creator_html)).strip()
  assert creator and len(creator)<400
  b=get(info["url"]); assert 12000<len(b)<20000000
  im=Image.open(io.BytesIO(b));im.verify();im=Image.open(io.BytesIO(b)).convert("RGB")
  assert im.width>=400 and im.height>=400
  name="commons-"+hashlib.sha256(filename.encode()).hexdigest()[:12]+".jpg"
  dest=base/"images"/name;dest.parent.mkdir(parents=True,exist_ok=True);im.save(dest,"JPEG",quality=90,optimize=True)
  page="https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_"))
  if not any(x.get("source_page")==page or x.get("file")=="images/"+name for x in d["images"]):
   d["images"].append({"file":"images/"+name,"role":role,"creator":creator,"license":m["LicenseShortName"]["value"],"source_page":page,"source_taxon_name":"Dasyochloa pulchella","public_reuse":"Image-specific Commons license checked; credit and SA conditions retained","photo_status":"PROVISIONAL — USER PHOTO REVIEW PENDING; no new anatomy arrow inferred"})
  print("ARCHIVED",filename)
 except Exception as e:
  holds.append({"file":filename,"reason":str(e)});print("HELD",filename,str(e))
d.setdefault("curation_status",{})["photo_metadata_count"]=len(d["images"])
d["curation_status"]["photo_files_present"]=sum(str(x.get("file","")).startswith("images/") for x in d["images"])
d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
report=pathlib.Path("reports/grass-fluffgrass-archive-20261023.json");report.parent.mkdir(exist_ok=True);report.write_text(json.dumps({"species":"Munroa pulchella","holds":holds,"gallery_records":len(d["images"])},indent=2)+"\n")
