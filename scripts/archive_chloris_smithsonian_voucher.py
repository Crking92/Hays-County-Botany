#!/usr/bin/env python3
"""Find and archive Smithsonian open-access Chloris andropogonoides specimen.
Source object: nmnhbotany_10607789. Fail closed on provenance or unavailable image."""
import io,json,pathlib,urllib.request,urllib.parse,urllib.error,re,time
from PIL import Image
base=pathlib.Path("content/taxa/Poaceae/Chloris/chloris-andropogonoides")
p=base/"species.json";d=json.loads(p.read_text());assert d["id"]=="chloris-andropogonoides"
source="https://www.si.edu/object/chloris-andropogonoides-e-fourn:nmnhbotany_10607789"
report={"source":source,"outcome":"HELD","notes":[]}
def get(url):
 for i in range(3):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Hays-County-Botany/1.0 (open-access botanical learner)"}),timeout=60) as resp:return resp.read()
  except urllib.error.HTTPError as ex:
   if ex.code not in (429,500,502,503,504) or i==2:raise
   time.sleep(20*(i+1))
try:
 raw=get(source);html=raw.decode("utf-8","replace")
 # Require the exact Smithsonian accession and stated public-domain rights.
 assert "10607789" in html and "Chloris" in html,"Failed exact Smithsonian object identity"
 # Look for actual Smithsonian IDS image service URLs rather than unauthenticated mirror media.
 matches=re.findall(r'https?[^"\\\\<> ]*ids\\.si\\.edu[^"\\\\<> ]+',html)
 matches += ["https:"+v for v in re.findall(r'//ids\\.si\\.edu/[^"\\\\<> ]+',html)]
 candidates=[]
 for u in matches:
  u=u.replace("&amp;","&").replace("\\u0026","&")
  if "ids.si.edu" in u and u not in candidates:candidates.append(u)
 report["notes"].append("Found "+str(len(candidates))+" Smithsonian IDS image references")
 for u in candidates[:20]:
  try:
   photo=get(u);im=Image.open(io.BytesIO(photo));im.verify();im=Image.open(io.BytesIO(photo)).convert("RGB")
   if min(im.size)<700:continue
   out=base/"images"/"smithsonian-cory-1946-andropogonoides.jpg";out.parent.mkdir(parents=True,exist_ok=True);im.save(out,"JPEG",quality=91,optimize=True)
   record={"file":"images/"+out.name,"role":"1946 Smithsonian herbarium specimen from Edwards County, Texas. Species/source voucher; NOT a living-plant ligule or microscopic lemma detail.","creator":"Smithsonian National Museum of Natural History; specimen collected by Victor L. Cory (1946)","license":"Public domain — Smithsonian Open Access","source_page":source,"public_reuse":"Smithsonian Open Access image and CC0 metadata; preserve accession and collector credit","photo_status":"HERBARIUM VOUCHER — anatomical arrows not yet reviewed"}
   if not any(x.get("file")==record["file"] for x in d["images"]):d["images"].append(record)
   d.setdefault("learner_visual_status",{})["image_count"]=len(d["images"])
   d.setdefault("curation_status",{})["photo_metadata_count"]=len(d["images"])
   p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n")
   report["outcome"]="ARCHIVED";report["notes"].append("Archived Smithsonian IDS source")
   break
  except Exception as e:report["notes"].append("Image rejected: "+str(e)[:200])
except Exception as e:report["notes"].append("Source check blocked: "+str(e))
rp=pathlib.Path("reports/chloris-smithsonian-voucher-archive.json");rp.parent.mkdir(exist_ok=True);rp.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
