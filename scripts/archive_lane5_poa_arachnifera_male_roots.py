#!/usr/bin/env python3
"""Lane 5 follow-up: archive the missing original F4 female maturation panel and
screen, but never guess, additional Bob Harms male/rhizome media.
All Selected Monocots material is credited educational-only, NOT CC.
"""
import io,json,pathlib,re,urllib.request,urllib.error,hashlib
from PIL import Image
P=pathlib.Path("content/taxa/Poaceae/Poa/poa-arachnifera/species.json")
S=json.loads(P.read_text());base="https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/data/"
prefix="https://w3.biosci.utexas.edu/prc/Monocots/GrassHTML/"
report={"source_rights":"Bob Harms expressly authorizes credited scientific/educational use of Selected Central Texas Monocots (NOT Creative Commons).","new_images":[],"possible_sources":[],"held":[]}
def get(url):
 req=urllib.request.Request(url,headers={"User-Agent":"Hays-County-Botany/1.0 educational archive"})
 with urllib.request.urlopen(req,timeout=25) as res:return res.read()
def save_image(code,role,page,caption,label):
 url=base+"images/"+code+".jpg";raw=get(url)
 im=Image.open(io.BytesIO(raw));im.verify()
 im=Image.open(io.BytesIO(raw)).convert("RGB")
 if min(im.size)<250:raise ValueError("insufficient original dimensions")
 destination=P.parent/"images"/("bob-harms-"+code.lower()+"-source.jpg")
 im.save(destination,"JPEG",quality=91,optimize=True)
 image_path="images/"+destination.name
 if not any(x.get("file")==image_path for x in S["images"]):
  S["images"].append({"file":image_path,"role":role,"creator":"Bob Harms","license":"© Bob Harms — credited scientific/educational use ONLY; NOT Creative Commons","license_url":prefix,"source_page":page,"source_image":url,"image_status":"SOURCE-LABELLED EDUCATIONAL LOCAL JPEG; site permission NOT transferable","photo_review":"Author source caption used; microscopic structures and arrow positions await on-pixel review","sha256_local":hashlib.sha256(destination.read_bytes()).hexdigest(),"image_dimensions":list(im.size)})
 visual_path=str(destination)
 if not any(x.get("image_url")==visual_path for x in S["visual_comparison"]["items"]):
  S["visual_comparison"]["items"].append({"label":label,"scientific_name":"Poa arachnifera","image_url":visual_path,"image_fit":"contain","image_role":role,"caption":caption,"why_it_matters":"Authentic original specimen-view photograph for distinguishing native Texas bluegrass; no microscopic arrow added without pixel verification.","creator":"Bob Harms","license":"© Bob Harms — scientific/educational attributed use only (NOT CC)","license_url":prefix,"source_page":page,"markers":[],"photo_status":"Physically archived original author-labelled photograph; anatomy markers held pending individual photo inspection."})
 report["new_images"].append({"code":code,"file":visual_path,"source":page,"pixels":list(im.size)})
 return image_path
# Guaranteed documented missing F4: photographed matured pistillate inflorescence, not male anatomy.
page=base+"pages/POAR-F4.html"
for x in S["visual_comparison"]["items"]:
 if x.get("source_page")==page and not x.get("image_url","").startswith("content/"):
  try:
   saved=save_image("POAR-F4","Mature dried FEMALE panicle with source scale; sex verified only by photographer's original PISTILLATE caption",page,"The dry female head may lose the conspicuous cottony web seen in fresh female flowers. This is NOT a male specimen and must not be labelled as one.","Mature FEMALE Texas bluegrass head — locally archived")
   x["image_url"]=str(P.parent/saved);x["photo_status"]="Originally externally hosted author-labelled pistillate F4 JPEG now physically archived; source and education-only rights preserved."
  except Exception as exc:report["held"].append({"code":"POAR-F4","reason":str(exc)[:200]})
# Find prospective authentic male/rhizome pages by verified text, not by an unexamined file name.
for code in ["POAR-M","POAR-M1","POAR-M2","POAR-M3","POAR-MS","POAR-SM","POAR-R","POAR-R1","POAR-8","POAR-B","POAR-b"]:
 candidate=base+"pages/"+code+".html"
 try:
  raw=get(candidate).decode("utf-8","replace")
  txt=re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",raw)).strip()
  if "Poa arachnifera" not in txt:continue
  is_male=bool(re.search(r"\b(staminate|male)\b",txt,re.I))
  is_female=bool(re.search(r"\b(pistillate|female)\b",txt,re.I))
  is_rhizome=bool(re.search(r"\b(rhizome|rhizomatous)\b",txt,re.I))
  report["possible_sources"].append({"code":code,"url":candidate,"text":txt[:600],"male":is_male,"female":is_female,"rhizome":is_rhizome})
  if is_male and not is_female:
   try:save_image(code,"Original author's STAMINATE/male Poa arachnifera flowering specimen; exact anther and sex anatomy not independently dissected",candidate,"AUTHOR-LABELLED MALE (staminate) Texas bluegrass specimen: compare with female cobwebby florets. Sex is sourced from the photographed specimen page, not inferred from head smoothness.","TEXAS BLUEGRASS — authenticated staminate MALE flower reference")
   except Exception as exc:report["held"].append({"code":code,"reason":str(exc)[:200]})
  elif is_rhizome and not is_male and not is_female:
   try:save_image(code,"Original author-labelled Texas bluegrass rhizome/root base, not a photo-derived proof of tiller linkage unless genuinely visible",candidate,"Original-author-labelled Texas bluegrass underground region. Check that connected rhizomes, nodes and shoots are clearly shown before adding arrows.","TEXAS BLUEGRASS — author-labelled rhizome study")
   except Exception as exc:report["held"].append({"code":code,"reason":str(exc)[:200]})
 except urllib.error.HTTPError as exc:
  if exc.code not in (403,404):report["held"].append({"code":code,"reason":str(exc)[:150]})
 except Exception as exc:report["held"].append({"code":code,"reason":str(exc)[:150]})
if report["new_images"]:
 # Avoid duplicate gallery references when replacing the already documented remote F4 panel.
 seen=set();unique=[]
 for panel in S["visual_comparison"]["items"]:
  k=(panel.get("scientific_name"),panel.get("image_url"))
  if k not in seen:unique.append(panel);seen.add(k)
 S["visual_comparison"]["items"]=unique
 S["field_id_finish_pass"]["lane5_second_pass_20261024"]={"status":"FIELD_READY_PHOTO_GAPS","report":"reports/lane5-poa-arachnifera-male-root-search-20261024.json","new_media":report["new_images"],"remaining":"Independently photographed male stamen and female carpel closeups (unless original male found); visibly connected real rhizome; exact site photo arrow audit."}
 P.write_text(json.dumps(S,ensure_ascii=False,indent=2)+"\n")
pathlib.Path("reports/lane5-poa-arachnifera-male-root-search-20261024.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
print(json.dumps(report,ensure_ascii=False))
