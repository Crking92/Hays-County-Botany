#!/usr/bin/env python3
"""Archive documented anatomical foxtail millet photos with licensing and rate-limit gates."""
import io,json,pathlib,time,urllib.parse,urllib.request,urllib.error
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Setaria/setaria-italica");p=base/"species.json";d=json.loads(p.read_text());assert d["id"]=="setaria-italica"
items=[("Setaria italica subsp. italica sl21.jpg","Photographed stem, leaf sheath and ligule (subsp. italica)","setaria-italica-ligule-stefan-lefnaer.jpg"),("Setaria italica subsp. italica sl48.jpg","Annotated actual spikelet, glume, lemma and palea (subsp. italica)","setaria-italica-spikelet-stefan-lefnaer.jpg")]
holds=[]
def get(url):
 for i in range(5):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Hays-County-Botany/1.0 (public botanical education)" }),timeout=65) as f:return f.read()
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or i==4:raise
   time.sleep(25*(i+1))
for filename,role,name in items:
 try:
  title="File:"+filename
  api="https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url%7Cextmetadata&format=json&titles="+urllib.parse.quote(title)
  info=next(iter(json.loads(get(api))["query"]["pages"].values()))["imageinfo"][0]
  lic=info["extmetadata"]["LicenseShortName"]["value"].upper().replace("-","").replace(" ","")
  assert "CCBYSA4.0" in lic,(filename,lic)
  raw=get(info["url"]);assert 20000<len(raw)<18000000
  im=Image.open(io.BytesIO(raw));im.verify();im=Image.open(io.BytesIO(raw)).convert("RGB")
  assert im.width>=500 and im.height>=500
  out=base/"images"/name;out.parent.mkdir(parents=True,exist_ok=True);im.save(out,"JPEG",quality=91,optimize=True)
  page="https://commons.wikimedia.org/wiki/"+urllib.parse.quote(title.replace(" ","_"))
  entry={"file":"images/"+name,"role":role,"creator":"Stefan.lefnaer","license":"CC BY-SA 4.0","license_url":"https://creativecommons.org/licenses/by-sa/4.0/","source_page":page,"source_taxon_name":"Setaria italica subsp. italica","photo_status":"SOURCE-LABELED anatomy; provisional for user arrow review","public_reuse":"Attribution and share-alike; retained source annotation"}
  if not any(x.get("file")==entry["file"] or x.get("source_page")==page for x in d["images"]):d["images"].append(entry)
  print("ARCHIVED",filename)
 except Exception as e:holds.append({"file":filename,"reason":str(e)});print("HELD",filename,str(e))
d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
d.setdefault("curation_status",{})["photo_metadata_count"]=len(d["images"])
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
report=pathlib.Path("reports/setaria-italica-anatomy-archive.json");report.parent.mkdir(exist_ok=True);report.write_text(json.dumps({"holds":holds,"gallery_entries":len(d["images"])},indent=2)+"\n")
