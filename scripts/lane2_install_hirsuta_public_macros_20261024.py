#!/usr/bin/env python3
"""Install only Commons-verified CC BY-SA 4.0 diagnostic bigtop lovegrass originals."""
import hashlib,io,json,pathlib,time,urllib.error,urllib.parse,urllib.request
from PIL import Image

base=pathlib.Path("content/taxa/Poaceae/Eragrostis/eragrostis-hirsuta")
path=base/"species.json"
results={"taxon":"Eragrostis hirsuta","purpose":"Public web photo-only diagnostic closeups, not unlicensed/private visuals","photos":[]}
specs=[
 (3,"douglas-goldman-single-spikelet-3.jpg","Close real source-labelled small green spikelet with exserted flower parts on hair-thin pedicel; no claimed measured glumes, florets, or ruler","SPIKELET — single reproductive unit, real macro"),
 (4,"douglas-goldman-spikelets-on-branches-4.jpg","Several real narrow spikelets borne separately on ultra-fine panicle branches; different views of attachment; no mm ruler","SPIKELETS — spaced on delicate branching pedicels")
]
def fetch(url):
 request=urllib.request.Request(url,headers={"User-Agent":"Hays-County-Botany-Visual-Learner/1.1 (educational licensed photo archivist; CC BY-SA 4.0)","Accept":"image/jpeg,application/json;q=0.9,*/*;q=0.5"})
 with urllib.request.urlopen(request,timeout=75) as response:return response.read()
for seq,name,role,label in specs:
 title=f"File:Eragrostis hirsuta{seq}.jpg"
 source=f"https://commons.wikimedia.org/wiki/File:Eragrostis_hirsuta{seq}.jpg"
 result={"source":source,"status":"HOLD"}
 try:
  params={"action":"query","format":"json","prop":"imageinfo","titles":title,"iiprop":"url|extmetadata","iiurlwidth":"1280"}
  api="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(params)
  data=json.loads(fetch(api))
  info=next(iter(data["query"]["pages"].values()))["imageinfo"][0]
  license=info["extmetadata"]["LicenseShortName"]["value"]
  creator=info["extmetadata"]["Artist"]["value"]
  assert "BY-SA 4.0" in license.upper(),license
  assert "Douglas" in creator or "Goldman" in creator,(creator[:180])
  originals=[info.get("url"),info.get("thumburl"),
      "https://commons.wikimedia.org/wiki/Special:Redirect/file/"+urllib.parse.quote(title.replace("File:",""))+"?width=1280"]
  raw=None;chosen=None
  for candidate in originals:
   if not candidate:continue
   for retry in range(3):
    try:
     data=fetch(candidate)
     if not data.startswith(b"\xff\xd8"):raise ValueError("Download did not return JPEG")
     raw=data;chosen=candidate;break
    except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as ex:
     if retry==2:break
     time.sleep((2,7,13)[retry])
   if raw is not None:break
  assert raw is not None, "Original and 1280px thumb were inaccessible"
  assert 20000<len(raw)<16000000
  ver=Image.open(io.BytesIO(raw));ver.verify()
  img=Image.open(io.BytesIO(raw)).convert("RGB")
  assert min(img.size)>=550
  dest=base/"images"/name;dest.parent.mkdir(exist_ok=True,parents=True)
  img.save(dest,quality=92,optimize=True)
  # Fresh canonical checkout, so preserve current concurrent-image metadata.
  j=json.loads(path.read_text());assert j["id"]=="eragrostis-hirsuta"
  if not any(x.get("source_page")==source for x in j["images"]):
   j["images"].append({"file":"images/"+name,"role":role,"creator":"Douglas Goldman","license":"CC BY-SA 4.0","license_url":"https://creativecommons.org/licenses/by-sa/4.0/","source_page":source,"public_reuse":"YES public website; CC BY-SA 4.0 attribution, modified/ShareAlike conditions","modifications":"Original image re-encoded as RGB JPEG with EXIF/GPS removed; unchanged organ features","photo_review":"Original source-series seven-photo contact sheet inspected 2026-10-23; this image provides visible entire spikelet and pedicel; no calibrated organ measurements"})
  if not any(x.get("source_page")==source for x in j["visual_comparison"]["items"]):
   j["visual_comparison"]["items"].insert(2 if seq==3 else 3,{
     "label":label,"scientific_name":"Eragrostis hirsuta",
     "image_url":str(dest),"image_fit":"contain","image_role":role,
     "caption":("Douglas Goldman's authentic E. hirsuta closeup from Wikimedia Commons, CC BY-SA 4.0. "
       "Visible tiny spikelet/pedicel structures, not a measured floret/glume/ligule dissection. "
       "Photographed organ details, no invented micron-level arrows."),
     "why_it_matters":"Webpage-serving diagnostic reproductive detail; photo rights permit publication beyond noncommercial research use.",
     "creator":"Douglas Goldman","license":"CC BY-SA 4.0",
     "license_url":"https://creativecommons.org/licenses/by-sa/4.0/",
     "source_page":source,"markers":[],
     "photo_status":"Verified source Creator and Commons individual image CC BY-SA 4.0; physically stored in GitHub; gallery displays exact local file. New organ-target arrows withheld."
   })
  j["field_photo_quickcheck"]["featured_photo_indices"]=[i for i in [3,4,len(j["images"])-1,0,1,2] if i<len(j["images"])]
  j["field_id_finish_pass"]["public_macro_installer_20261024"]={
    "public_site_license_policy":"CC0, CC BY, CC BY-SA or actual U.S. public domain only",
    "no_nc_photos_in_gallery":True,
    "new_diagnostic_spikelet_closeups":"source-verified Douglas Goldman, CC BY-SA 4.0",
    "remaining":["TRUE ligule measured with original 1-mm scale","mature spikelet dissected with 1-mm physical reference","same-plant voucher and mobile Pages view QA"],
    "public_pages_deployment":"NOT VERIFIED"
  }
  path.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n")
  result.update(status="ARCHIVED_AND_GALLERY_LINKED",path=str(dest),dimensions=list(img.size),sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),download=chosen,license=license)
 except Exception as ex: result["error"]=str(ex)
 results["photos"].append(result)
out=pathlib.Path("reports/lane2-eragrostis-hirsuta-public-macros-20261024.json")
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(results,indent=2)+"\n")
print(json.dumps(results))
