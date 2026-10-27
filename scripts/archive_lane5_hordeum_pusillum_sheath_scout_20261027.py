#!/usr/bin/env python3
"""Archive actual Hordeum pusillum externally linked leaf sheath, and license-screen
four other photos for real crown/spikelet anatomy. All rights per Commons file,
no false ligule/rachis-triad labeling. No site deployment claim.
"""
import json,pathlib,html,re,hashlib,urllib.parse,urllib.request,urllib.error,time,io,base64,csv
from PIL import Image,ImageOps,ImageDraw
ROOT=pathlib.Path("content/taxa/Poaceae/Hordeum/hordeum-pusillum")
CARD=ROOT/"species.json";LEDGER=ROOT/"image-sources.csv"
REPORT=pathlib.Path("reports/lane5-hordeum-pusillum-sheath-and-candidate-scout-20261027.json")
LICENSE="https://creativecommons.org/licenses/by-sa/2.0/"
FILENAME="Hordeum pusillum (7495171452).jpg"
URL="https://commons.wikimedia.org/wiki/File:"+urllib.parse.quote(FILENAME.replace(" ","_"))
RELPATH="images/matt-lavin-little-barley-external-leaf-sheath-7495171452.jpg"
CANDIDATES=["Hordeum pusillum (3877588841).jpg","Hordeum pusillum (3878383828).jpg","Hordeum pusillum (7495172200).jpg","Hordeum pusillum (7495172732).jpg"]
report={"date":"2026-10-27","species":"Hordeum pusillum","new_photo":[],"candidate_scout":[],"holds":[],"new_arrows":0,"status":"FIELD_READY_PHOTO_GAPS","do_not_infer":["Actual inner 0.2–0.8 mm ligule membrane from external sheath","Exposed rooted annual crown","Three spikelets still attached at one measured rachis node"]}
def get(url):
 for n in range(5):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"HaysCountyBotanyLicensedPhotoResearch/1.0 (educational native grass learner)","Accept":"application/json,image/jpeg,*/*"})
   with urllib.request.urlopen(req,timeout=48) as f:
    blob=f.read(17000001)
   if len(blob)>17000000:raise ValueError("Response >17MB")
   return blob
  except urllib.error.HTTPError as e:
   if e.code not in (429,500,502,503,504) or n==4:raise
   time.sleep((n+1)*2)
def imageinfo(name):
 q=urllib.parse.urlencode({"action":"query","prop":"imageinfo|categories","cllimit":"max","iiprop":"url|extmetadata","iiurlwidth":"1900","titles":"File:"+name,"format":"json"})
 page=next(iter(json.loads(get("https://commons.wikimedia.org/w/api.php?"+q))["query"]["pages"].values()))
 info=page["imageinfo"][0];meta=info["extmetadata"]
 lic=re.sub("[^A-Z0-9]","",meta.get("LicenseShortName",{}).get("value","").upper())
 artist=html.unescape(re.sub("<[^>]+>"," ",meta.get("Artist",{}).get("value",""))).strip()
 categories={x["title"] for x in page.get("categories",[])}
 if lic!="CCBYSA20" or "Matt Lavin" not in artist or "Category:Hordeum pusillum" not in categories:
  raise ValueError("Individual license, photographer or taxon category mismatch: "+str((lic,artist)))
 return info
d=json.loads(CARD.read_text());assert d["id"]=="hordeum-pusillum"
panel=d["visual_comparison"]["items"][5]
if panel.get("source_page")!=URL:raise ValueError("Exact gallery photo/source identity unexpected "+str(panel.get("source_page")))
try:
 info=imageinfo(FILENAME)
 raw=get(info.get("thumburl") or info["url"])
 with Image.open(io.BytesIO(raw)) as im:im.verify()
 with Image.open(io.BytesIO(raw)) as im:
  im=ImageOps.exif_transpose(im).convert("RGB")
  if min(im.size)<900:raise ValueError("Original rendition too small")
  pixels=list(im.size);b=io.BytesIO();im.save(b,"JPEG",quality=89,optimize=True);binary=b.getvalue()
 dest=ROOT/RELPATH
 if not any(x.get("file")==RELPATH for x in d["images"]):
  dest.parent.mkdir(exist_ok=True);dest.write_bytes(binary)
  with Image.open(dest) as im:im.verify()
  digest=hashlib.sha256(binary).hexdigest()
  d["images"].append({"file":RELPATH,"role":"True exterior green upper leaf sheath encircling stem with narrow blade extending; minute inner ligule NOT exposed",
   "creator":"Matt Lavin","license":"CC BY-SA 2.0","license_url":LICENSE,"source_page":URL,
   "source_original_url":info["url"],"source_region":"Charles M. Russell National Wildlife Refuge, Montana — NOT Hays County",
   "modifications":"RGB JPEG re-encoded and EXIF/GPS stripped, no anatomical arrows",
   "sha256":digest,"pixels":pixels,
   "public_reuse":"Individually Commons-confirmed original Matt Lavin CC BY-SA 2.0 attribution/license; adaptation stated",
   "photo_status":"PHYSICALLY ARCHIVED, true outer sheath visible; actual inner sub-mm free ligule and roots unphotographed"})
  panel["image_url"]=str(dest)
  panel["image_role"]="Actual Matt Lavin original of the external leaf sheath wrapping the little-barley culm with a narrow blade. The inner free membranous ligule is hidden."
  panel["caption"]="Real little-barley upper shoot with green outer leaf sheath surrounding the stalk and narrow blade extending at the junction. This photo is now STORED LOCALLY under the original CC BY-SA 2.0 license, not hotlinked. It does NOT resolve the inner free 0.2–0.8 mm ligule, authentic roots or auricles. Montana source, not Hays County."
  panel["photo_status"]="Locally archived original source-labelled photograph; source taxon and individual CC BY-SA 2.0 license verified 2026-10-27. No tiny ligule, roots or measured microscopic structures certified."
  panel["modifications"]="New local RGB JPEG reencode strips EXIF/GPS; no arrows; original source photo and license retained."
  report["new_photo"].append({"source":URL,"photo_file":str(dest),"bytes":len(binary),"pixels":pixels,"sha256":digest,"gallery_index":5,"license":"CC BY-SA 2.0"})
  # Insert at the front of the basename-only source ledger with same columns, preserve existing row data.
  with LEDGER.open(newline="") as f:reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
  if not any(r["file_name"]==dest.name for r in rows):
   record=dict.fromkeys(fields,"")
   for col,val in {"file_name":dest.name,"role":"Source-verified actual exterior leaf sheath and blade, not tiny inner ligule",
     "creator":"Matt Lavin","license":"CC BY-SA 2.0","source_page":URL,
     "direct_url":info["url"],"study_use":"educational with CC BY-SA attribution and derivative obligation",
     "public_reuse":"YES — verified individual Commons CC BY-SA 2.0"}.items():
    if col in record:record[col]=val
   rows.append(record)
   with LEDGER.open("w",newline="") as f:writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
  d["curation_status"]["photo_metadata_count"]=len(d["images"])
  d["curation_status"]["photo_files_present"]=len(d["images"])
  d["curation_status"]["public_licensed_extra_gallery_refs"]=0
  d["curation_status"]["visual_finish"]="FIELD_READY_PHOTO_GAPS — 5 exact species locally archived JPEGs, including true exterior leaf sheath. Inner sub-mm ligule, exposed annual crown, and intact measured rachis triad missing."
  d["learner_visual_status"]["image_count"]=len(d["images"])
  d["learner_visual_status"]["note"]="Five locally archived exact-species photos and one external H. jubatum comparison. Matt Lavin 7495171452 exterior leaf sheath is NOW physically in GitHub, CC BY-SA 2.0. Actual tiny ligule, real roots and attached single rachis triad still missing; public Pages display not verified."
  for tile in d.get("field_id_short_tiles",[]):
   tile["details"]=tile["details"].replace("NEW exact-species source-authenticated Matt Lavin EXTERNAL CC BY-SA 2.0 panel 5","NEW exact-species source-authenticated Matt Lavin LOCALLY STORED CC BY-SA 2.0 panel 5")
   tile["details"]=tile["details"].replace("The source 960-pixel rendition is displayed EXTERNALLY with CC BY-SA 2.0 credit; not downloaded as a GitHub JPEG.","The verified CC BY-SA 2.0 original has now been archived inside GitHub with Matt Lavin credit.")
   tile["details"]=tile["details"].replace("FIVE species-matched teaching panels now include one new credited CC BY-SA 2.0 EXTERNAL upper-sheath photo","FIVE species-matched teaching panels now include one new credited CC BY-SA 2.0 LOCALLY ARCHIVED upper-sheath photo")
  d["lane5_little_barley_sheath_20261027"]={"new_photo":report["new_photo"],"status":"FIELD_READY_PHOTO_GAPS","unresolved":report["do_not_infer"]}
  CARD.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n")
except Exception as e:report["holds"].append({"source":URL,"reason":str(e)})
# Secondary candidates are ONLY inspected for possible role, never automatically installed.
sheet=Image.new("RGB",(840,700),"white");draw=ImageDraw.Draw(sheet)
for i,name in enumerate(CANDIDATES):
 record={"file":name,"source":"https://commons.wikimedia.org/wiki/File:"+urllib.parse.quote(name.replace(" ","_"))}
 try:
  info=imageinfo(name);raw=get(info.get("thumburl") or info["url"])
  with Image.open(io.BytesIO(raw)) as im:im.verify()
  with Image.open(io.BytesIO(raw)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   record["original_rendition_size"]=list(im.size)
   im.thumbnail((405,313))
   sheet.paste(im,((i%2)*420+(420-im.width)//2,(i//2)*350+24+(310-im.height)//2))
  record["status"]="EXACT_SPECIES_LICENSE_VERIFIED__REQUIRES_PIXEL_ROLE_REVIEW"
 except Exception as e:record.update({"status":"HELD","reason":str(e)[:300]})
 draw.text(((i%2)*420+6,(i//2)*350+5),name[16:35],fill="#222222")
 report["candidate_scout"].append(record)
if any(x["status"].startswith("EXACT_SPECIES") for x in report["candidate_scout"]):
 b=io.BytesIO();sheet.save(b,"JPEG",quality=68,optimize=True)
 print("PHOTO_CONTACT_START_"+base64.b64encode(b.getvalue()).decode()+"_PHOTO_CONTACT_END")
REPORT.parent.mkdir(exist_ok=True)
REPORT.write_text(json.dumps(report,indent=2)+"\n")
print("PHOTO_REPORT="+json.dumps(report))
