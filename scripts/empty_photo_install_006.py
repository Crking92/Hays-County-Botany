import copy,hashlib,io,json,pathlib,sys,urllib.request
sys.path.insert(0,str(pathlib.Path(".").resolve()))
from scripts.glass_root_private_photo_install_005 import science,csv_append
from PIL import Image
ROOT=pathlib.Path(".");BATCH=ROOT/"workflow/empty-photo-006/approved.json";REPORT=ROOT/"reports/empty-photo-install-006.json"
def fetch(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"HaysBotany-FirstPhotoInstall/1.0"}),timeout=35) as r:return r.read()
def main():
 batch=json.loads(BATCH.read_text());manifest=json.loads((ROOT/"data/manifest.json").read_text());canonical={s["id"]:s["path"] for s in manifest["species"]};work=[]
 for t in batch["targets"]:
  assert canonical[t["id"]]==t["path"]
  p=ROOT/t["path"];sp=json.loads(p.read_text());before=copy.deepcopy(sp);rel="images/"+t["filename"]
  assert not sp.get("images"),"Target no longer zero-photo: "+t["id"]
  assert not any((p.parent/"images").glob("*")),"Physical image already present"
  o=json.loads(fetch(t["observation_url"].replace("www.inaturalist.org/observations/","api.inaturalist.org/v1/observations/")))["results"][0]
  assert o["taxon"]["name"]==t["scientific_name"] and o["quality_grade"]=="research"
  src=next(x for x in o["photos"] if x["id"]==t["photo_id"])
  assert src["license_code"]==t["source_license"] and src["license_code"] in ["cc0","cc-by","cc-by-sa"]
  assert src["attribution"]==t["source_attribution"]
  raw=(ROOT/t["preview"]).read_bytes()
  with Image.open(io.BytesIO(raw)) as im: dims=list(im.size);im.verify()
  creator=t["source_attribution"].removeprefix("(c) ").split(", some rights reserved")[0]
  code=src["license_code"];license={"cc-by":"CC BY","cc-by-sa":"CC BY-SA","cc0":"CC0"}[code]
  license_url={"cc-by":"https://creativecommons.org/licenses/by/4.0/","cc-by-sa":"https://creativecommons.org/licenses/by-sa/4.0/","cc0":"https://creativecommons.org/publicdomain/zero/1.0/"}[code]
  record={"file":rel,"role":t["role"],"creator":creator,"license":license,"license_url":license_url,"source_platform":"iNaturalist","source_page":t["photo_page"],"observation_url":t["observation_url"],"observation_id":t["observation_id"],"photo_id":t["photo_id"],"source_recorded_photo_license_at_download":code,"source_recorded_photo_attribution_at_download":src["attribution"],"downloaded_from":t["direct_url"],"image_dimensions":dims,"study_use":"yes","public_reuse":"yes; retain attribution"+("; ShareAlike for adaptations" if code=="cc-by-sa" else ""),"modifications":"EXIF removed and JPEG normalized; no anatomy overlays","photo_review":"Exact Research Grade source record and actual pixels reviewed; provisional first-pass view"}
  work.append((t,p,sp,before,raw,record))
 report={"batch_id":batch["batch_id"],"installed":[],"canonical_species_count":len(canonical),"science_preserved":True}
 for t,p,sp,before,raw,r in work:
  out=p.parent/r["file"];out.parent.mkdir(exist_ok=True);out.write_bytes(raw)
  sp["images"]=[r];cur=sp.setdefault("curation_status",{});cur["photo_metadata_count"]=1;cur["photo_files_present"]=1
  sp["learner_visual_status"]={"status":"provisional_learner_ready","mode":"learner_fast_fill","image_count":1,"note":"First exact photograph installed; additional diagnostic views pending."}
  sp["photo_note"]=(sp.get("photo_note") or "")+" First exact licensed photo physically installed 2026-10-14; fine diagnostic gallery pending."
  assert science(sp)==science(before),"Scientific data changed"
  p.write_text(json.dumps(sp,ensure_ascii=False,indent=2)+"\n")
  csv_append(p.parent/"image-sources.csv",[{"file_name":t["filename"],"role":r["role"],"creator":r["creator"],"license":r["license"],"license_url":r["license_url"],"source_page":r["source_page"],"direct_url":r["downloaded_from"],"observation_id":str(r["observation_id"]),"photo_id":str(r["photo_id"]),"study_use":"yes","public_reuse":r["public_reuse"],"modifications":r["modifications"]}])
  s=p.parent/"SOURCES.txt";s.write_text(s.read_text()+"\nFIRST LICENSED PHOTOGRAPH 2026-10-14\n"+r["creator"]+"; "+r["license"]+"; "+r["license_url"]+"\n"+r["source_page"]+" | "+r["observation_url"]+"\n"+r["modifications"]+". Preserve attribution and applicable ShareAlike.\n")
  report["installed"].append({"id":t["id"],"path":t["path"],"file":str(out),"photo_id":t["photo_id"],"observation_id":t["observation_id"],"bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),"dimensions":r["image_dimensions"],"creator":r["creator"],"license":r["license"],"science_preserved":True})
 REPORT.write_text(json.dumps(report,indent=2)+"\n")
 from scripts.curation_pipeline import rebuild_photo_fast_fill_queue
 rebuild_photo_fast_fill_queue()
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
