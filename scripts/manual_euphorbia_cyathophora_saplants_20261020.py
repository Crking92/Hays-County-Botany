#!/usr/bin/env python3
"""Install reused licensed macro originally named Euphorbia heterophylla var. cyathophora,
a Kew POWO synonym of accepted Euphorbia cyathophora. Species identity remains
based on the original contributor label and nomenclatural synonym, not image guesswork.
"""
import hashlib,io,json,time
from pathlib import Path
from urllib.parse import quote
import requests
from PIL import Image,ImageOps
BASE=Path("content/taxa/Euphorbiaceae/Euphorbia/euphorbia-cyathophora")
CARD=BASE/"species.json"
NAME="Euphorbia_heterophylla_var._cyathophora_1DS-II_2-6098.jpg"
FILE="images/04-saplants-cyathophora-gland-macro.jpg"
OUT=BASE/FILE
SOURCE="https://commons.wikimedia.org/wiki/File:"+NAME
POWO="https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:101634-2"
REPORT=Path("reports/euphorbia-cyathophora-saplants-install-20261020.json")
def get():
 h=hashlib.md5(NAME.encode()).hexdigest()
 direct="https://upload.wikimedia.org/wikipedia/commons/"+h[0]+"/"+h[:2]+"/"+quote(NAME,safe="._-")
 special="https://commons.wikimedia.org/wiki/Special:Redirect/file/"+quote(NAME,safe="._-")+"?width=1600"
 s=requests.Session()
 s.headers["User-Agent"]="HaysCountyBotanyLearner/1.0 (https://github.com/Crking92/Hays-County-Botany)"
 problems=[]
 for url in [special,direct]:
  try:
   resp=s.get(url,timeout=95);resp.raise_for_status()
   buf=resp.content
   assert 15000<len(buf)<22000000
   with Image.open(io.BytesIO(buf)) as original:
    original.load()
    assert original.format in ("JPEG","PNG")
    pic=ImageOps.exif_transpose(original).convert("RGB")
   dim=list(pic.size)
   assert min(dim)>=700
   sha=hashlib.sha256(buf).hexdigest()
   pic.thumbnail((1750,1750),Image.Resampling.LANCZOS)
   b=io.BytesIO();pic.save(b,"JPEG",quality=91,optimize=True)
   data=b.getvalue()
   with Image.open(io.BytesIO(data)) as test:test.verify()
   assert len(data)>17000
   return data,resp.url,sha,dim,list(pic.size)
  except Exception as e:
   problems.append((url,str(e)[:140]))
 raise RuntimeError("Source photo unavailable: "+repr(problems))
def main():
 j=json.loads(CARD.read_text(encoding="utf-8"))
 assert j["scientific_name"]=="Euphorbia cyathophora"
 assert j["project_inclusion"]["target_zone_status"]=="PASS"
 assert j["field_id_finalization"]["stage"]=="PASS_IN_PROGRESS"
 if any(x["file"]==FILE for x in j["images"]):
  assert OUT.exists()
  print("Already installed");return
 assert len(j["images"])==3 and not OUT.exists()
 raw,download,sha,source_dims,final_dims=get()
 OUT.parent.mkdir(exist_ok=True,parents=True)
 OUT.write_bytes(raw)
 j["images"].append({
  "file":FILE,
  "role":"Close-up of named historical var. cyathophora, synonym of E. cyathophora (Kew POWO); developing capsules and potential oblong-gland anatomy.",
  "creator":"SAplants (Wikimedia Commons)",
  "license":"CC BY-SA 4.0",
  "license_url":"https://creativecommons.org/licenses/by-sa/4.0/",
  "source_page":SOURCE,
  "source_name_as_uploaded":"Euphorbia heterophylla var. cyathophora",
  "accepted_name_basis":POWO,
  "source_platform":"Wikimedia Commons, source identified as var. cyathophora (accepted cyathophora)",
  "downloaded_from":download,
  "original_image_sha256":sha,
  "original_image_dimensions":source_dims,
  "image_dimensions":final_dims,
  "public_reuse":"yes",
  "study_use":"public education with attribution and ShareAlike",
  "modifications":"Downscaled, EXIF removed; no annotations added to image file",
  "anatomy_arrows":"none until direct saved JPEG anatomy review",
  "photo_review":"Species author used historical var. cyathophora, synonym accepted as Euphorbia cyathophora by POWO. Gland anatomy requires verified pixel close-up before an arrow.",
 })
 j["curation_status"]["photo_metadata_count"]=len(j["images"])
 j["curation_status"]["photo_files_present"]=len(j["images"])
 j["curation_status"]["saplants_synonym_photo_added"]="2026-10-20"
 j["learner_visual_status"]["image_count"]=len(j["images"])
 j["field_id_finalization"]["photo_review"]+=" Added licensed SAplants macro originally labelled var. cyathophora, confirmed synonym of this accepted species at Kew POWO. Await pixel-level gland opening check."
 CARD.write_text(json.dumps(j,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 REPORT.parent.mkdir(exist_ok=True,parents=True)
 REPORT.write_text(json.dumps({"scientific_name":"Euphorbia cyathophora","original_source_taxon":"Euphorbia heterophylla var. cyathophora","accepted_synonym_basis":POWO,"creator":"SAplants","license":"CC BY-SA 4.0","source_page":SOURCE,"file":FILE,"source_sha256":sha,"source_dimensions":source_dims,"processed_dimensions":final_dims,"visual_photo_arrows":"pending exact JPEG inspection"},indent=2)+"\n",encoding="utf-8")
 print("PASS one new historical-synonym photo for accepted E cyathophora",FILE)
if __name__=="__main__":main()
