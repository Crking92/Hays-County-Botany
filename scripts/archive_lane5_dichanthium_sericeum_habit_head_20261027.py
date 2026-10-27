#!/usr/bin/env python3
"""Lane 5: physically archive two source-verified Harry Rose CC BY 2.0 silky
bluestem photographs already in gallery, preserving exact panel indices and
existing gross arrows. Do not infer Texas subspecies or fine glume anatomy.
"""
import csv,hashlib,html,io,json,pathlib,re,time,urllib.parse,urllib.request,urllib.error
from PIL import Image,ImageOps
ROOT=pathlib.Path("content/taxa/Poaceae/Dichanthium/dichanthium-sericeum")
CARD=ROOT/"species.json";LEDGER=ROOT/"image-sources.csv"
REPORT=pathlib.Path("reports/lane5-dichanthium-sericeum-habit-head-20261027.json")
TARGETS=[
 (1,"Dichanthium sericeum plant4 (14359286201).jpg","harry-rose-silky-bluestem-australian-flowering-tuft.jpg",
  "Living Australian source-identified flowering tuft with leafy basal bunch and multiple attached racemes; ROOTS HIDDEN, not Texas proven."),
 (4,"Dichanthium sericeum head16 (6775945404).jpg","harry-rose-silky-bluestem-attached-awned-head.jpg",
  "True photographed silky terminal racemes and long dark awns. Sessile and pedicelled spikelet pair and glume hair arch NOT isolated.")
]
rep={"species":"Dichanthium sericeum","date":"2026-10-27","photos":[],"new_arrows":0,
 "status":"FIELD_READY_PHOTO_GAPS","remaining":["Texas-vouchered connected flowering crown and actual roots","True opened inner 0.5–2 mm ligule","1-mm measured sessile/pedicelled spikelet pair, transverse glume hair line and lemma awn origin"]}
def get(url):
 for i in range(4):
  try:
   request=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotanyLicenseCheckedPhotoArchive/1.0 (noncommercial educational field identification)"})
   with urllib.request.urlopen(request,timeout=48) as f: data=f.read(17000000)
   if len(data)>16500000:raise ValueError("oversize response")
   return data
  except urllib.error.HTTPError as ex:
   if ex.code not in (429,500,502,503,504) or i==3:raise
   time.sleep(2*(i+1))
d=json.loads(CARD.read_text());assert d["id"]=="dichanthium-sericeum"
for panelindex,name,basename,role in TARGETS:
 source="https://commons.wikimedia.org/wiki/File:"+name.replace(" ","_")
 rel="images/"+basename
 rec={"file":rel,"source":source,"gallery_index":panelindex}
 try:
  p=d["visual_comparison"]["items"][panelindex]
  if urllib.parse.unquote(p.get("source_page",""))!=source:raise ValueError("Panel source mismatch")
  q=urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo|categories","cllimit":"max","iiprop":"url|extmetadata","iiurlwidth":"1800","titles":"File:"+name})
  page=next(iter(json.loads(get("https://commons.wikimedia.org/w/api.php?"+q))["query"]["pages"].values()))
  info=page["imageinfo"][0];meta=info["extmetadata"]
  lic=re.sub("[^A-Z0-9]","",meta.get("LicenseShortName",{}).get("value","").upper())
  artist=html.unescape(re.sub("<[^>]+>"," ",meta.get("Artist",{}).get("value",""))).strip()
  categories=[c["title"] for c in page.get("categories",[])]
  if lic!="CCBY20" or "Harry Rose" not in artist or "Category:Dichanthium sericeum" not in categories:
   raise ValueError("Exact taxon category/creator/license fails: "+str((lic,artist,categories[:5])))
  raw=get(info.get("thumburl") or info["url"])
  with Image.open(io.BytesIO(raw)) as im:im.verify()
  with Image.open(io.BytesIO(raw)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   if min(im.size)<950:raise ValueError("Image resolution inadequate")
   size=list(im.size);buf=io.BytesIO();im.save(buf,"JPEG",quality=90,optimize=True);blob=buf.getvalue()
  dest=ROOT/rel;dest.parent.mkdir(exist_ok=True)
  if any(x.get("file")==rel for x in d["images"]):raise ValueError("Already installed, refuse duplicate")
  dest.write_bytes(blob)
  with Image.open(dest) as im:im.verify()
  sha=hashlib.sha256(blob).hexdigest()
  d["images"].append({"file":rel,"role":role,"creator":"Harry Rose (Macleay Grass Man)",
   "license":"CC BY 2.0","license_url":"https://creativecommons.org/licenses/by/2.0/",
   "source_page":source,"source_original_url":info["url"],"source_region":"New South Wales, Australia, original source; NOT proof of Texas locality/subspecies",
   "modifications":"Individual Commons original re-encoded to RGB JPEG, EXIF/GPS stripped; no new image arrows",
   "sha256":sha,"pixels":size,"photo_status":"Real exact species source-identified locally stored public-cleared photo, fine anatomy unmeasured"})
  p["image_url"]=str(dest)
  p["photo_status"]="ORIGINAL HARRY ROSE CC BY 2.0 JPEG NOW PHYSICALLY ARCHIVED; source/taxon/rights and JPEG verified 2026-10-27. Existing gross arrows preserved; no true ligule, Texas infraspecific or measured pair certified."
  p["modification_note"]="Source Commons thumbnail reencoded to RGB JPEG stripping EXIF/GPS; no new added arrows or burned labels."
  p["public_reuse"]="Proper photographer/Commons source/CC BY 2.0 attribution retained. Source from Australia, not native-to-Texas evidence."
  p["caption"]=p["caption"].replace("an original externally served CC BY 2.0 image, not yet downloaded into GitHub","a CC BY 2.0 image now stored in GitHub with exact creator and source credits")
  rec.update({"status":"archived","pixels":size,"bytes":len(blob),"sha256":sha,"license":"CC BY 2.0"})
 except Exception as e:rec.update({"status":"HELD","reason":str(e)[:320]})
 rep["photos"].append(rec)
arch=[x for x in rep["photos"] if x["status"]=="archived"]
if arch:
 d["curation_status"]["photo_metadata_count"]=len(d["images"])
 d["curation_status"]["photo_files_present"]=len(d["images"])
 d["curation_status"]["visual_finish"]="FIELD_READY_PHOTO_GAPS — archived bearded node, actual sheath, genuine flowering tuft and attached silky awned head (Australian source). Still requires Texas rooted crown, inner membranous ligule and separately dissected 1-mm paired spikelets."
 d["learner_visual_status"]["image_count"]=len(d["images"])
 d.setdefault("lane5_silky_habit_head_local_20261027",{}).update({"new_photos":arch,
    "stage":"FIELD_READY_PHOTO_GAPS","not_certified":rep["remaining"]})
 for t in d.get("field_id_short_tiles",[]):
  t["details"]=t["details"].replace("(external panel 1","(locally archived panel 1")
  t["details"]=t["details"].replace("(external panel 4","(locally archived panel 4")
  t["details"]=t["details"].replace("(panel 1, EXTERNAL)","(panel 1, LOCALLY ARCHIVED)")
  t["details"]=t["details"].replace("panels 1 and 4 are separately licensed Australian whole habit and head references EXTERNAL only","panels 1 and 4 are now LOCALLY ARCHIVED CC BY 2.0 Australian real whole-habit and attached head photographs")
 CARD.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
 # Preserve rows and source-scoped attributions in the source ledger.
 with LEDGER.open(newline="") as f:rd=csv.DictReader(f);cols=rd.fieldnames;rows=list(rd)
 for r in arch:
  if any(x.get("file_name")==pathlib.Path(r["file"]).name for x in rows):continue
  row=dict.fromkeys(cols,"")
  for k,v in {"file_name":pathlib.Path(r["file"]).name,"role":next(z[3] for z in TARGETS if r["file"].endswith(z[2])),
   "creator":"Harry Rose (Macleay Grass Man)","license":"CC BY 2.0","source_page":r["source"],
   "direct_url":"","study_use":"educational field ID with credit","public_reuse":"YES; Commons individual CC BY 2.0 verified"}.items():
   if k in row:row[k]=v
  rows.append(row)
 with LEDGER.open("w",newline="") as f:wr=csv.DictWriter(f,fieldnames=cols);wr.writeheader();wr.writerows(rows)
REPORT.parent.mkdir(exist_ok=True)
REPORT.write_text(json.dumps(rep,indent=2)+"\n")
print(json.dumps(rep))
