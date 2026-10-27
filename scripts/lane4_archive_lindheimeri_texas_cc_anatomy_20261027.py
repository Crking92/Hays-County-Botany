#!/usr/bin/env python3
"""Photo-level CC BY archive: exact species Texan Lindheimer panicgrass true anatomical photos.

Strict original iNaturalist photo API identity, research grade, independent CC license,
RGB re-encode EXIF/GPS stripping, SHA256, no invented mm or organ identity.
Source taxon is iNat research-grade, not independently botanist-vouchered.
"""
import csv,hashlib,io,json,pathlib,urllib.parse,urllib.request,urllib.error,time
from PIL import Image,ImageOps
BASE=pathlib.Path("content/taxa/Poaceae/Dichanthelium/dichanthelium-lindheimeri")
CARD=BASE/"species.json"
SOURCES=BASE/"image-sources.csv"
IDS=[
(272828976,157692952,"texas-scaled-spikelet-close","A real detached or attached elliptic spikelet photographed beside physical source scale; upper glume and lemma identity not yet established"),
(272799666,157708086,"texas-spikelet-second-face","Reproductive close-up of true small purple-green spikelet; do not infer glume edges before full pixel review"),
(272828978,157692952,"texas-leaf-collar-hair-region","Real macro of blade-sheath junction showing multiple long white hairs; whether hairs arise from inner true ligule vs blade/sheath margins requires actual pixel orientation"),
(272799727,157708086,"texas-spikelet-mm-ruler","Physical ruler adjacent small mature-looking spikelet; scale and units must be confirmed before counting measured diagnostic glume"),
(272829028,157692952,"texas-stem-node-macro","Very close leaf sheath / green culm node, with visible tissue folds; do not call true opened inner free ligule"),
(272799762,157708086,"texas-basal-node-and-sheath","Photographed culm node and pale/brown leaf sheath with attached blade; true inner ligule unseen"),
(272829064,157692952,"texas-leaf-sheath-blade","Live leaf-sheath/blade junction showing stem joint and green blades in source-confirmed grass"),
(272799764,157708086,"texas-dry-sheath-node","Macro of a sheath and adjacent stem joint with brown surface tissues, source species; no disconnected roots"),
(272800423,157708086,"texas-other-side-collar","Photographed leaf base, outside collar and sheath; inner 1–5 mm hair fringe not verified from this angle"),
]
def get(url,limit=14_000_000):
 err=None
 for i in range(4):
  try:
   rq=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotany/1.0 (noncommercial CC exact-grass photo archive, github.com/Crking92/Hays-County-Botany)","Accept":"application/json,image/jpeg,image/*;q=0.8"})
   with urllib.request.urlopen(rq,timeout=45) as rs:
    data=rs.read(limit+1)
   if len(data)>limit:raise ValueError("Oversized")
   return data
  except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as e:
   err=e
   if isinstance(e,urllib.error.HTTPError) and e.code not in (429,500,502,503,504):raise
   time.sleep(2*(i+1))
 raise RuntimeError(str(err))
def api(obs):
 return json.loads(get("https://api.inaturalist.org/v1/observations/"+str(obs),9_000_000))["results"][0]
def main():
 card=json.loads(CARD.read_text(encoding="utf-8"))
 assert card["id"]=="dichanthelium-lindheimeri"
 obsids={row[1] for row in IDS}
 looked={i:api(i) for i in obsids}
 for num,obs in looked.items():
  assert obs["taxon"]["name"]=="Dichanthelium lindheimeri",(num,obs["taxon"].get("name"))
  assert obs.get("quality_grade")=="research",(num,obs.get("quality_grade"))
 with SOURCES.open(newline="",encoding="utf-8") as f:
  reader=csv.DictReader(f);columns=list(reader.fieldnames);rows=list(reader)
 installed=[];held=[];addrows=[]
 for pid,oid,short,role in IDS:
  local=f"images/inat-public-cc-{pid}-{short}.jpg"
  if any(x.get("file")==local for x in card["images"]):continue
  o=looked[oid]
  p=next((x for x in o.get("photos",[]) if x.get("id")==pid),None)
  try:
   assert p is not None,(pid,"missing individually verified photo")
   license=p.get("license_code")
   assert license in {"cc0","cc-by","cc-by-sa"},"Not a website-reusable Creative Commons license"
   src=p["url"]
   assert src.startswith("https://") and urllib.parse.urlparse(src).hostname in {"inaturalist-open-data.s3.amazonaws.com","static.inaturalist.org","inaturalist.s3.amazonaws.com"}
   large=src.replace("/square.","/large.") if "/square." in src else src
   data=get(large,9_000_000)
   probe=Image.open(io.BytesIO(data));probe.verify()
   pic=ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert("RGB")
   assert pic.width>=650 and pic.height>=480,(pid,pic.size)
   path=BASE/local;path.parent.mkdir(parents=True,exist_ok=True)
   pic.save(path,"JPEG",quality=91,optimize=True)
   saved=path.read_bytes();verified=Image.open(io.BytesIO(saved))
   assert saved[:2]==b"\xff\xd8" and saved[-2:]==b"\xff\xd9"
   assert verified.size==pic.size and not verified.getexif() and not verified.info.get("exif")
   locality=(o.get("place_guess") or "")[:150]
   creator=p.get("attribution") or o.get("user",{}).get("name") or o.get("user",{}).get("login")
   if not creator:raise ValueError("Photo creator missing")
   photographic_cc={"cc0":"CC0","cc-by":"CC BY","cc-by-sa":"CC BY-SA"}[license]
   record={"file":local,"role":role,"creator":creator,"license":photographic_cc,
    "license_code":license,"license_version_note":"Individual iNaturalist photo API license code verified. Source-specific license version NOT independently recorded.",
    "source_page":"https://www.inaturalist.org/photos/"+str(pid),
    "source_observation":"https://www.inaturalist.org/observations/"+str(oid),
    "source_observation_taxon":"Dichanthelium lindheimeri",
    "source_observation_quality_grade":"research","source_locality":locality,
    "public_reuse":"Per-individual original iNaturalist photo CC BY or CC0 with source/creator attributed. No noncommercial or no-derivatives media installed.",
    "photo_status":"Real exact source species and photo-level public Creative Commons license VERIFIED; anatomical role/proof and arrow pixel inspection still pending.",
    "modifications":"Proportional large source photograph re-encoded RGB JPEG (EXIF/GPS discarded); no in-image Photoshop or synthesized anatomy.",
    "archive_sha256":hashlib.sha256(saved).hexdigest(),"image_dimensions":list(pic.size),
    "photo_id":pid}
   card["images"].append(record)
   card["visual_comparison"]["items"].append({
    "label":"SOURCE PHOTOGRAPH — "+short.replace("-"," ").upper(),
    "scientific_name":"Dichanthelium lindheimeri",
    "image_url":(BASE/local).as_posix(),"image_fit":"contain",
    "image_role":role,
    "caption":"Real exact-source research-grade iNaturalist photograph by "+creator+" ("+locality+"). "+role+". No tiny structure is called ligule, glume or fertile lemma without actual pixel proof. Source license "+photographic_cc+" (exact version unrecorded).",
    "why_it_matters":"True taxon-linked actual photographic macro candidate for crew to orient anatomical study, not arbitrary genus substitute.",
    "creator":creator,"license":photographic_cc,"source_page":record["source_page"],
    "modifications":record["modifications"],"photo_status":"PHYSICALLY ARCHIVED RESEARCH-GRADE PHOTO — awaiting targeted anatomy pixel QA; no role score gained from source alone.",
    "markers":[]})
   addrows.append({"file_name":path.name,"role":role,"creator":creator,"license":photographic_cc,"source_page":record["source_page"],
      "direct_url":large,"study_use":"Public grass ID learner","public_reuse":"Photo-level CC BY/CC BY-SA/CC0 only; source rights and creator preserved",
      "observation_id":oid,"photo_id":pid})
   installed.append({"id":pid,"file":local,"sha256":hashlib.sha256(saved).hexdigest(),"width":pic.width,"height":pic.height,"bytes":len(saved),
     "license":photographic_cc,"creator":creator,"obs":oid,"locality":locality})
   print("ARCHIVED",pid,local,pic.size,flush=True)
  except Exception as e:
   held.append({"photo_id":pid,"obs":oid,"reason":str(e)[:400]});print("HOLD",pid,str(e)[:250],flush=True)
 if installed:
  card["curation_status"]["photo_metadata_count"]=len(card["images"])
  card["curation_status"]["photo_files_present"]=len(card["images"])
  card["learner_visual_status"]["image_count"]=len(card["images"])
  card["field_id_finish_pass"]["lane4_lindheimeri_texas_macro_sources_20261027"]={
   "photo_additions":len(installed),"new_arrows":0,"score_changes":0,
   "source_scope":"Texas George Bush Park/Houston research-grade observations 157692952 and 157708086 only Texas research-grade observations; non-research Louisiana/Wisconsin candidates explicitly excluded",
   "rights":"Per-photo CC BY verified exact iNaturalist original; attribution preserved; photo license version not presumed.",
   "remaining":"Actual inside collar hair-fringe proof, calibrated individual spikelet/glumes, exposed same-plant rooted crown, exact comparison",
   "status":"Actual source media archived; role scoring and arrow placement require independent pixel inspection."}
  card["visual_comparison"]["overlay_note"]+="\n2026-10-27: source-verified actual D. lindheimeri research-grade exact species licensed CC BY photo original byte archives for aboveground anatomy. All copyright, locality, source observation and author maintained; no unreviewed fine anatomy arrow, score or millimeter claim. Earlier wrongly named D. pedicellatum photos remain excluded."
  CARD.write_text(json.dumps(card,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
  with SOURCES.open("w",newline="",encoding="utf-8") as f:
   w=csv.DictWriter(f,fieldnames=columns,extrasaction="ignore");w.writeheader();w.writerows(rows+addrows)
 report={"date":"2026-10-27","target":"Dichanthelium lindheimeri","installed":installed,"held":held,
   "note":"Physically copied JPEG only from individual photo API record CC BY/CC0/CC BY-SA. NO role scoring or fine-anatomy arrows prior to independent pixel review."}
 folder=pathlib.Path("reports")
 folder.mkdir(exist_ok=True)
 (folder/"lane4-lindheimeri-research-grade-cc-anatomy-archive-20261027.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print(json.dumps({"archive_count":len(installed),"held_count":len(held),"ids":[x["id"] for x in installed]},indent=2),flush=True)
if __name__=="__main__":main()
