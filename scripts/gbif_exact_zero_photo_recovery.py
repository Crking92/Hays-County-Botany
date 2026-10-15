#!/usr/bin/env python3
"""Conservative first-photo GBIF/herbarium media recovery for canonical true-zero learner taxa.

Only install when: unclaimed zero card; exact source determination (accepted name or
Kew-checked synonym); individual IMAGE license CC0 / CC BY / CC BY-SA / CC BY-NC;
credited image bytes fully downloaded and verified. No taxonomic/range edits.
Otherwise emit a detailed skipped/candidate audit, not a borrowed genus photo.
"""
import argparse,copy,csv,datetime,hashlib,io,json,pathlib,re,sys,urllib.parse,urllib.request,urllib.error,time,collections
from concurrent.futures import ThreadPoolExecutor,as_completed
from PIL import Image,ImageOps
ROOT=pathlib.Path(".");sys.path.insert(0,str(ROOT.resolve()))
QUEUE=ROOT/"reports/photo-fast-fill-zero-queue.json"
REPORT=ROOT/"reports/gbif-first-photo-targeted-latest.json"
BASE="https://api.gbif.org/v1/occurrence/search"
HEAD={"User-Agent":"Hays-County-Botany-ExactSpecimenPhotoRecovery/1.0 (educational project)","Accept":"application/json,image/*"}
# Explicitly validated synonyms from Kew POWO and ITIS; the source determination
# itself must also name the species/variety, never its broader parent taxon.
NAMES={
 "erigeron-geiseri":["Erigeron geiseri"],
 "symphyotrichum-lanceolatum-subsp-lanceolatum":["Symphyotrichum lanceolatum subsp. lanceolatum","Aster lanceolatus subsp. lanceolatus"],
 "physaria-sessilis":["Physaria sessilis","Lesquerella sessilis","Lesquerella gracilis var. sessilis"],
 "astragalus-crassicarpus-var-berlandieri":["Astragalus crassicarpus var. berlandieri","Astragalus mexicanus"],
 "astragalus-nuttallianus-var-pleianthus":["Astragalus nuttallianus var. pleianthus","Astragalus austrinus var. pleianthus","Astragalus pleianthus"],
 "oenothera-patriciae":["Oenothera patriciae","Gaura brachycarpa","Gaura hexandra var. coryi","Gaura tripetala var. coryi"],
 "muhlenbergia-piniflora":["Muhlenbergia piniflora"],
 "tridentopsis-buckleyana":["Tridentopsis buckleyana","Tridens buckleyanus","Triodia buckleyana","Sieglingia buckleyana"],
 "sorghastrum-elliottii":["Sorghastrum elliottii"],
 "senna-pilosior":["Senna pilosior"],
 "bouteloua-pectinata":["Bouteloua pectinata"],
 "eragrostis-hirsuta":["Eragrostis hirsuta"],
}
# Catch falsely identified separate taxa sharing an initial binomial.
RANK_BAD=re.compile(r"^(variety|subspecies|subsp|form|f\\.)\b",re.I)
def http(url,maximum=14500000):
 for attempt in range(3):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers=HEAD),timeout=29) as r:
    data=r.read(maximum+1)
   if len(data)>maximum:raise ValueError("oversized source")
   return data
  except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError):
   if attempt==2:raise
   time.sleep(1+attempt*2)
def getjson(params):
 url=BASE+"?"+urllib.parse.urlencode(params)
 return json.loads(http(url,maximum=3000000))
def licensed(media):
 lic=str(media.get("license") or "").lower().strip()
 if not lic:return None
 clean=lic.replace("http:","https:").replace("creativecommons.org/licenses/","creativecommons.org/licenses/")
 # Require an actual media-level license; cannot infer from occurrence record.
 if "creativecommons.org/publicdomain/zero/" in clean or lic in ("cc0","cc0 1.0"):
  return ("CC0 1.0","https://creativecommons.org/publicdomain/zero/1.0/")
 for code,label in (("by-nc-sa","CC BY-NC-SA"),("by-nc","CC BY-NC"),("by-sa","CC BY-SA"),("by","CC BY")):
  if re.search(r"creativecommons\.org/licenses/"+code+r"/\d",clean):
   return (label,lic)
 return None
def exact_name(source,expected):
 if not source:return False
 s=re.sub(r"\s+"," ",re.sub(r"[×]","x",source)).strip().lower()
 target=expected.lower().replace("subsp. ","subsp ").replace("var. ","var ")
 s=s.replace("subsp. ","subsp ").replace("var. ","var ")
 if not s.startswith(target):return False
 trail=s[len(target):]
 if trail and trail[0] not in (" ",",", "(", "."):return False
 if len(target.split())==2 and re.match(r"^\s+(var\b|subsp\b|f\b)",trail):return False
 return True
def scan_one(sid, names):
 candidate=[]; stats=[]
 for name in names:
  try:dat=getjson({"scientificName":name,"mediaType":"StillImage","limit":30})
  except Exception as exc:
   stats.append({"name":name,"error":str(exc)[:120]});continue
  rows=dat.get("results") or []
  matched=0
  for obs in rows:
   # GBIF taxon inference can synonymize source specimen differently. The original
   # occurrence identification is the decisive source, not its parent accepted taxon.
   orig=str(obs.get("scientificName") or "")
   if not exact_name(orig,name):continue
   if "TAXON_MATCH_HIGHERRANK" in (obs.get("issues") or []):continue
   matched+=1
   if obs.get("basisOfRecord") not in ("PRESERVED_SPECIMEN","HUMAN_OBSERVATION","MATERIAL_SAMPLE","MACHINE_OBSERVATION"):
    continue
   for media in obs.get("media") or []:
    perm=licensed(media)
    if not perm:continue
    uri=media.get("identifier") or media.get("references") or ""
    parsed=urllib.parse.urlparse(uri)
    if parsed.scheme!="https" or not parsed.hostname:continue
    if parsed.hostname in ("gbif.org","www.gbif.org","pinterest.com","www.pinterest.com"):continue
    person=media.get("creator") or media.get("rightsHolder") or obs.get("rightsHolder") or obs.get("recordedBy") or ""
    if not person and perm[0]!="CC0 1.0":continue
    candidate.append({"id":sid,"searched_name":name,"source_determination":orig,
      "gbif_id":obs.get("key"),"occurrence_url":"https://www.gbif.org/occurrence/"+str(obs.get("key")),
      "dataset_key":obs.get("datasetKey"),"uri":uri,"creator":str(person)[:160],
      "license":perm[0],"license_url":perm[1],
      "format":media.get("type") or media.get("format") or "",
      "basis":obs.get("basisOfRecord"),"source_publisher":obs.get("publisher") or "",
      "media_title":str(media.get("title") or "")[:150]})
  stats.append({"name":name,"results":len(rows),"exact_determinations":matched})
 # Prefer specimen with clearly licensed image, then human observation. Break ties.
 candidate.sort(key=lambda x:(x["basis"]!="PRESERVED_SPECIMEN",x["license"]!="CC0 1.0",len(x["creator"])<2,x["gbif_id"] or 0))
 return sid,stats,candidate[:25]
def encode(uri):
 parsed=urllib.parse.urlparse(uri)
 if parsed.scheme!="https" or not parsed.hostname:return None
 raw=http(uri)
 with Image.open(io.BytesIO(raw)) as im:
  im.load(); RGB=ImageOps.exif_transpose(im).convert("RGB")
 if min(RGB.size)<350 or max(RGB.size)<700:return None
 RGB.thumbnail((1350,1350),Image.Resampling.LANCZOS)
 stream=io.BytesIO();RGB.save(stream,format="JPEG",quality=90,optimize=True,progressive=True)
 if len(stream.getvalue())<19000:return None
 return stream.getvalue(),list(RGB.size)
def unchanged(src):
 s=copy.deepcopy(src)
 for key in ("images","photo_note","learner_visual_status"):s.pop(key,None)
 status=s.get("curation_status")
 if isinstance(status,dict):
  for key in ("photo_metadata_count","photo_files_present","gbif_first_photo_install"):status.pop(key,None)
  if not status:s.pop("curation_status",None)
 return s
def csvappend(path,new):
 txt=path.read_text(encoding="utf-8-sig") if path.exists() else ""
 rd=csv.DictReader(io.StringIO(txt));keys=list(rd.fieldnames or []);lines=list(rd)
 for key in new:
  if key not in keys:keys.append(key)
 b=io.StringIO();writer=csv.DictWriter(b,fieldnames=keys,lineterminator="\n")
 writer.writeheader();writer.writerows(lines+[new]);path.write_text(b.getvalue(),encoding="utf-8")
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--reclaim-expired",action="store_true",help="Allow work on expired leases ONLY; preserve any live/renewed claim and never overwrite.")
 p.add_argument("--report",default=str(REPORT))
 p.add_argument("--focus",default="",help="Comma-separated exact species IDs, if supplied")
 args=p.parse_args()
 focus={x.strip() for x in args.focus.split(",") if x.strip()}
 reportfile=ROOT/args.report
 now_dt=datetime.datetime.now(datetime.timezone.utc)
 now=now_dt.isoformat()
 manifest=json.loads((ROOT/"data/manifest.json").read_text(encoding="utf-8"))
 refs={e["id"]:e["path"] for e in manifest["species"]}
 queue=json.loads(QUEUE.read_text(encoding="utf-8"))
 busy=set()
 claims=json.loads((ROOT/"workflow/work-claims.json").read_text(encoding="utf-8"))
 for x in claims["claims"]:
  if x.get("status") not in ("active","queued","blocked"):continue
  expiry=x.get("expires_at")
  can_reclaim=False
  if args.reclaim_expired and expiry and x.get("status")=="active":
   try:
    lease=datetime.datetime.fromisoformat(expiry.replace("Z","+00:00"))
    can_reclaim=lease<now_dt and x.get("lane") in ("photo-fast-fill","genus-comparison-builder")
   except (ValueError,TypeError):pass
  if not can_reclaim:busy.update(x.get("taxa") or [])
 inbox=set()
 for p in (ROOT/"curation-inbox").rglob("species.json"):
  try:inbox.add(json.loads(p.read_text())["id"])
  except (KeyError,ValueError,OSError):pass
 report={"run_at":now,"lane":"targeted first-photo GBIF individually licensed source recovery",
   "source_policy":"Exact original specimen determination or independently confirmed botanical synonym. Image-level CC0/CC BY/CC BY-SA/CC BY-NC license required. Anatomy provisional.",
   "installed":[],"skipped":[],"searches":[]}
 queued=[r for r in queue["items"] if r["id"] in NAMES and (not focus or r["id"] in focus)]
 eligible=[]
 for row in queued:
  sid=row["id"]
  if sid in busy or sid in inbox or row.get("in_curation_inbox") or row.get("active_claims"):
   report["skipped"].append({"id":sid,"reason":"another active project lane"});continue
  loc=refs.get(sid);path=ROOT/loc if loc else None
  if not path or not path.is_file():continue
  sp=json.loads(path.read_text(encoding="utf-8"))
  if (sp.get("images") or []) or (path.parent/"images").exists() and any((path.parent/"images").iterdir()):
   report["skipped"].append({"id":sid,"reason":"no longer physically/gallerically empty"});continue
  eligible.append((sid,path,sp))
 findings={}
 with ThreadPoolExecutor(max_workers=4) as executor:
  fut={executor.submit(scan_one,sid,NAMES[sid]):sid for sid,_,_ in eligible}
  for future in as_completed(fut):
   sid,stats,candidates=future.result();findings[sid]=(stats,candidates)
 staged=[]
 for sid,path,sp in eligible:
  stats,possible=findings[sid]
  report["searches"].append({"id":sid,"queries":stats,"licensed_exact_media_candidates":len(possible)})
  media=None
  for row in possible[:15]:
   try:
    encoded=encode(row["uri"])
    if not encoded:continue
    blob,dim=encoded
   except Exception:continue
   media=(row,blob,dim)
   break
  if not media:
   report["skipped"].append({"id":sid,"reason":"No retrievable individually licensed exact-determination image among search results", "image_candidates":len(possible)})
   continue
  staged.append((sid,path,sp,media))
  if len(staged)>=8:break
 for sid,path,sp,(row,binary,dim) in staged:
  before=unchanged(sp)
  filename="gbif-first-"+str(row["gbif_id"])+"-"+hashlib.sha1(row["uri"].encode()).hexdigest()[:10]+".jpg"
  dest=path.parent/"images"/filename
  if dest.exists():raise ValueError("Refused to overwrite existing photo "+str(dest))
  dest.parent.mkdir(exist_ok=True);dest.write_bytes(binary)
  record={"file":"images/"+filename,"role":"Provisional exact source determination first-recognition photo; diagnostic details not checked",
    "creator":row["creator"] or "CC0 creator not specified",
    "license":row["license"],"license_url":row["license_url"],
    "source_platform":"GBIF mediated record; credit original dataset, specimen and creator",
    "source_page":row["occurrence_url"],"gbif_occurrence_id":str(row["gbif_id"]),
    "source_determination":row["source_determination"],"accepted_target":sp["scientific_name"],
    "media_source_url":row["uri"],"source_dataset_key":row["dataset_key"],
    "image_dimensions":dim,
    "study_use":"Yes; rights-specific conditions on original image",
    "public_reuse":"Respect photo license; CC BY-NC images are noncommercial only",
    "photo_review":"Source-reported taxon and image license verified; morphological identification and teaching view need independent visual review",
    "modifications":"Resized JPEG and EXIF removed"}
  sp["images"]=[record]
  cs=sp.setdefault("curation_status",{})
  cs["photo_metadata_count"]=1;cs["photo_files_present"]=1;cs["gbif_first_photo_install"]=now[:10]
  lv=sp.setdefault("learner_visual_status",{})
  lv.update({"status":"provisional_learner_ready","mode":"learner_fast_fill","image_count":1,
             "note":"Specimen/observation source first photo installed provisionally with an individually verified license. Botanical diagnostic morphology pending.",
             "missing_diagnostic_views":["Confirm diagnostic vegetative and reproductive characters"]})
  sp["photo_note"]=((sp.get("photo_note") or "")+" Exact source determination GBIF-linked image provisionally installed with image-level license; visual ID requires review.").strip()
  if unchanged(sp)!=before:raise AssertionError("Scientific fields changed for "+sid)
  csvappend(path.parent/"image-sources.csv",{"file_name":filename,"role":record["role"],
    "creator":record["creator"],"license":record["license"],"license_url":record["license_url"],
    "source_page":row["occurrence_url"],"direct_url":row["uri"],
    "study_use":"yes","public_reuse":record["public_reuse"],
    "modifications":record["modifications"]})
  with (path.parent/"SOURCES.txt").open("a",encoding="utf-8") as out:
   out.write("\nPROVISIONAL GBIF EXACT-SPECIMEN FIRST PHOTO "+now+"\n"+str(row["source_determination"])+"\n"+str(row["creator"])+"\n"+str(row["license"])+" "+str(row["license_url"])+"\n"+row["occurrence_url"]+"\n"+row["uri"]+"\nAnatomy visual verification pending; no scientific taxon/range status changed.\n")
  path.write_text(json.dumps(sp,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
  report["installed"].append({"id":sid,"source_taxon":row["source_determination"],"photo_file":str(dest),"source_page":row["occurrence_url"],"license":row["license"],"bytes":len(binary),"sha256":hashlib.sha256(binary).hexdigest()})
 reportfile.parent.mkdir(parents=True,exist_ok=True)
 reportfile.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 if report["installed"]:
  from scripts.curation_pipeline import rebuild_photo_fast_fill_queue
  rebuild_photo_fast_fill_queue()
 print(json.dumps({"installed":report["installed"],"skips":report["skipped"],"searches":report["searches"]},indent=2),flush=True)
if __name__=="__main__":main()
